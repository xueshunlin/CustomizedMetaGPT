from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.actions import Speak
from metagpt.schema import Message

class Evaluator(Role):
    """A role that evaluates modularized code produced by AI models.
    
    This class is part of the Evaluation Company workflow, responsible for assessing
    the quality of modularized code against predefined standards. It works alongside
    other roles like other Evaluators and Reviewer to ensure comprehensive code evaluation.
    """

    goal : str = "to explicitly evaluate a modularized work produced by AI model"

    def __init__(
        self,
        name: str,          # Unique identifier for this evaluator
        profile: str,       # Description of evaluator's expertise/background
        opponent_name: str, # Name of the other evaluator for debate-style evaluation
        send_to: str,       # Target recipient of evaluation messages
        evaluation_standards: list[str],  # List of criteria to evaluate against
        **kwargs,
    ):
        """Initialize the Evaluator with specific evaluation parameters.
        
        The evaluator participates in a multi-agent debate system where two evaluators
        assess code quality and a reviewer synthesizes their findings.
        """
        super().__init__(name=name, profile=profile, **kwargs)
        self.set_actions([Speak])  # Enable communication through Speak action
        self._watch([Speak])       # Monitor Speak actions from other agents
        self.name = name
        self.opponent_name = opponent_name
        self.send_to = send_to
        self.evaluation_standards = evaluation_standards

    async def _observe(self) -> int:
        """Filter and process incoming messages relevant to this evaluator.
        
        Returns:
            int: Number of new messages to process
        """
        await super()._observe()
        # Only process messages specifically addressed to this evaluator
        self.rc.news = [msg for msg in self.rc.news if self.name in msg.send_to]
        return len(self.rc.news)

    async def _act(self) -> Message:
        """Execute evaluation action and generate response message.
        
        This method:
        1. Logs the current evaluation task
        2. Retrieves evaluation context from environment history
        3. Runs evaluation against predefined standards
        4. Creates and stores response message
        
        Returns:
            Message: Evaluation results formatted as a message
        """
        logger.info(f"{self._setting}: ready to {self.rc.todo}")
        todo = self.rc.todo 

        # Get historical context for evaluation
        memories = self.rc.env.history

        # Run evaluation using context and standards
        rsp = await todo.run(
            context=memories,
            name=self.name,
            opponent_name=self.opponent_name,
            evaluation_standards=self.evaluation_standards
        )

        # Format and store evaluation results
        msg = Message(
            content=rsp,
            role=f"{self.name}'s arguments",
            cause_by=todo,
            sent_from=self.name,
            send_to=self.send_to,
        )

        self.rc.memory.add(msg)

        return msg