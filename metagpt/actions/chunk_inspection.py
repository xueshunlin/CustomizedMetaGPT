import shutil
from pathlib import Path
import re
from typing import Optional, TYPE_CHECKING

from metagpt.actions import Action, ActionOutput
from metagpt.const import INTEPRETATION_FILENAME, RAG_ENGINE_DIR, EVAL_RAG_ENGINE_DIR
from metagpt.schema import Message
from metagpt.logs import logger
from metagpt.rag.schema import FAISSIndexConfig
from metagpt.rag.engines import SimpleEngine

# Type checking imports for better IDE support
if TYPE_CHECKING:
    from metagpt.team import Team
    from metagpt.environment import Environment
    from metagpt.roles import Evaluator, Reviewer, Summarizer
    from metagpt.roles import Scorer

class ChunkInspection(Action):
    """
    Action class responsible for evaluating the quality of code modularization through a multi-agent debate system.
    This class compares original code chunks with their modularized versions and facilitates a structured evaluation process.
    """
    name: str = "ChunkIntepretation"
    i_context: Optional[str] = None  # Optional context for interpretation
    _use_llm_ranker: bool = True     # Flag to enable/disable LLM-based ranking

    @property
    def config(self):
        """Access configuration settings from the context"""
        return self.context.config

    async def run(self, with_messages, **kwargs):
        """
        Main execution method that:
        1. Sets up RAG engines for both original and modularized code
        2. Retrieves and compares code chunks
        3. Initiates multi-agent debates for evaluation
        4. Judging the evaluation results with a summarizer
        5. Calculates final evaluation scores
        
        Returns:
            ActionOutput containing evaluation results
        """
        # Import roles here to avoid circular imports
        from metagpt.team import Team
        from metagpt.environment import Environment 
        from metagpt.roles import Evaluator, Reviewer, Summarizer
        from metagpt.roles import Scorer
       
        # Initialize RAG engine for original code chunks
        chunk_pathname = self.repo.workdir / RAG_ENGINE_DIR
        chunk_config = FAISSIndexConfig(persist_path=chunk_pathname)
        engine = SimpleEngine.from_index(index_config=chunk_config)

        # Initialize RAG engine for modularized code
        modularized_pathname = self.repo.workdir / EVAL_RAG_ENGINE_DIR
        modularized_config = FAISSIndexConfig(persist_path=modularized_pathname)
        modularized_engine = SimpleEngine.from_index(index_config=modularized_config)

        # Get all original code chunks for evaluation
        chunks = engine.retriever._docstore.docs
        scores = 0
        
        # Evaluate each chunk against its modularized version
        for chunk in chunks:
            content = chunks[chunk].text
            
            # Retrieve corresponding modularized code for comparison
            nodes = await modularized_engine.aretrieve( 
                "Please find relative file correspond to the following code "+
                f"##code content:({content})"
            )
            
            # Set up evaluation environment and team
            debate_env = Environment(desc="Code modularization evaluation")
            debate_team = Team(investment=10.0, env=debate_env)
            
            # Prepare context for evaluation debate
            debate_context = f"""
            ## original code before modularization:
            {content.split("##The following is the explaination of this part of code:")[0]}

            ## modularized code:
            #{"    #".join([node.text for node in nodes])}
            """

            # Define comprehensive evaluation standards
            evaluation_standards = [
                "Confirm that all core functionalities and workflows from the original code (e.g., critical functions, input-output behaviors, side effects) still exist and produce the same outcomes in the modularized version.",
                "Check if functionality is split into modules based on coherent responsibilities (e.g., a module focused on user interfaces, another on core business logic, etc.) without creating unnecessary fragmentation or inter-dependencies.",
                "Ensure constant values, configuration settings, or environment references are unchanged and are now placed in the most logical module or file (e.g., a dedicated config module) without scattering them throughout the code.",
                "Verify that each module imports only what it needs (no unused or redundant imports) and that any external dependencies required by the original code are still present and correctly imported in the relevant module(s).",
                "Look for any syntactical mistakes, incorrect function signatures, or missing references that would prevent the code from executing. Confirm that module-to-module references (e.g., from foo import bar) match what's actually defined in the respective files.",
                "Confirm that functions, classes, and variables keep consistent naming with the original code, unless changed to improve clarity. In those cases, verify that references to the old names have been updated across all modules.",
                "Check that the order of function calls and the way parameters are passed among modules mirror the original logic. Any new abstractions should not alter the fundamental control flow or expected input-output transformations.",
                "Confirm that docstrings, inline comments, and other documentation from the original code are preserved or enhanced to explain the newly introduced module boundaries and responsibilities. Look for any missing or outdated references that might confuse future readers." ,
                "Evaluate whether the modularized structure is clearer than the monolithic version. Check that related functions or classes are grouped logically, and that each file has a clear, singular responsibility, making the overall codebase easier to navigate.",
                "Inspect whether the modularization enables easier future changes, testability, or feature additions. Look for signs of good modular design—such as reduced code duplication, fewer tightly coupled components, and well-defined module interfaces."
                ]
            
            # Create evaluators with different perspectives
            evaluator1 = Evaluator(
                    name="Bob",
                    profile=(
                        "a meticulous and seasoned software engineer with a strong background in "
                        "large-scale distributed systems. Enjoys deep-diving into design patterns "
                        "and ensuring optimal performance for critical workflows."
                    ),
                    opponent_name="Alice",
                    send_to="Alice",
                    evaluation_standards=evaluation_standards
                )

            evaluator2 = Evaluator(
                    name="Alice",
                    profile=(
                        "an exacting Senior Quality Assurance Engineer who prioritizes robust test "
                        "coverage and risk mitigation. Known for being highly skeptical of unchecked "
                        "assumptions and passionate about enforcing best practices in QA."
                    ),
                    opponent_name="Bob",
                    send_to="Charlie",
                    evaluation_standards=evaluation_standards
                )

            # Create reviewer to synthesize evaluations
            reviewer = Reviewer(
                    name="Charlie",
                    profile=(
                        "a neutral debate reviewer with years of experience in software project "
                        "management and technical writing. Skilled at synthesizing diverse viewpoints "
                        "and driving fair, well-reasoned conclusions."
                    ),
                    send_to="Bob"
                )
            
            # Assemble the evaluation team
            debate_team.hire([evaluator1, evaluator2, reviewer])

            # Run the evaluation debate
            discussions = await debate_team.run(
                idea=debate_context, 
                n_round=self.config.evaluation_rounds, 
                send_to="Bob"
            )

            # Create summarizer and scorer for final evaluation
            summarizer = Summarizer(name="Sarah", 
                                    profile=(
                                "a seasoned Software Engineer Team Leader with a decade of experience "
                                "translating complex technical details into actionable insights. Skilled "
                                "at synthesizing diverse viewpoints, guiding architectural discussions, "
                                "and fostering cross-functional consensus."
                            ),
                                    send_to="Steven",
                                    project_path = self.project_path
                                    )
            scorer = Scorer(name="Steven", profile="Senior manager")

            # Set up wrap-up environment and team
            wrapup_env = Environment(desc="Code modularization evaluation wrap-up")
            wrapup_team = Team(investment=10.0, env=wrapup_env)

            wrapup_team.hire([summarizer, scorer])

            # Generate final evaluation and score
            final_answer = await wrapup_team.run(
                idea=discussions, 
                n_round=2, 
                send_to="Sarah"
            )

            # Extract numerical score from the final answer
            final_score = int(re.search(r'\d+', final_answer[::-1]).group()[::-1])
            scores += final_score

        # Calculate and log the total evaluation score
        total_score =  len(chunks) * len(evaluation_standards)
        logger.info(f"Evaluation completed | Evaluation score: {scores/total_score*100}%")
            
