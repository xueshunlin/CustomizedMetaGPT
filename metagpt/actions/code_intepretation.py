import shutil
from pathlib import Path
from typing import Optional

from metagpt.actions import Action, ActionOutput
from metagpt.const import RAG_ENGINE_DIR
from metagpt.schema import Documents
from metagpt.utils.file_repository import FileRepository
import json
from metagpt.rag.engines import SimpleEngine
from metagpt.rag.schema import LLMRankerConfig, FAISSRetrieverConfig

# System message prompt for code interpretation task
CODEINTEPRETATIONSYSTEMMSG = """Please explicitly explain the code in the nodes below in few sentences:"""

class CodeIntepretation(Action):
    """Action class responsible for interpreting and understanding code in nodes
    
    This class processes code chunks, generates explanations using LLM, and stores
    the results in a RAG (Retrieval Augmented Generation) engine together for better context retrieval.
    """

    name: str = "CodeIntepretation"  # Name of the action
    i_context: Optional[str] = None  # Optional context for interpretation
    _use_llm_ranker: bool = True     # Flag to enable/disable LLM-based ranking

    @property
    def config(self):
        """Returns the configuration from the context"""
        return self.context.config

    async def run(self, with_messages, **kwargs):
        """Main execution method to interpret code functionality
        
        This method:
        1. Converts input files into nodes for processing
        2. Generates explanations for each code chunk using LLM
        3. Creates and persists a RAG engine with the processed nodes
        
        Args:
            with_messages: Messages to process
            **kwargs: Additional keyword arguments
            
        Returns:
            None - Results are stored in the RAG engine
        """

        intepretations = []  # List to store code interpretations
        workdir = self.repo.scripts.workdir  # Get working directory
        
        # Convert input files to nodes with optimized chunk sizes
        nodes = await SimpleEngine.from_docs_to_nodes(
            input_files=[Path(workdir) / dir for dir in self.repo.scripts.all_files], 
            optimize_chunk_size=True
        )
        
        # Process each node and generate explanations
        for node in nodes:
            code = node.text
            # Get explanation from LLM
            rsp = await self._aask(code, system_msgs=[CODEINTEPRETATIONSYSTEMMSG])
            # Append explanation to node text
            node.text += "\n##The following is the explaination of this part of code:" + rsp
            intepretations.append(node.text)

        # Configure ranking if enabled
        ranker_configs = [LLMRankerConfig()] if self._use_llm_ranker else None

        # Create RAG engine from processed nodes
        engine = SimpleEngine.from_nodes_to_engine(
            nodes=nodes,
            retriever_configs=[FAISSRetrieverConfig()],
            ranker_configs=ranker_configs,
        )

        # Create directory and persist RAG engine
        pathname = self.repo.workdir / RAG_ENGINE_DIR
        pathname.mkdir(parents=True, exist_ok=True)
        engine.persist(pathname)

        
        