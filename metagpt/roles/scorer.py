from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.actions import Score
from metagpt.schema import Message

class Scorer(Role):
    """A role responsible for scoring evaluation results and feedback.
    
    This class is part of the evaluation workflow in the CustomizedMetaGPT project,
    specifically handling the scoring of modularized code quality based on evaluation results.
    """

    goal: str = "score the evaluation results and feedback"

    def __init__(
        self,
        name: str,
        profile: str,
        **kwargs,
    ):
        """Initialize the Scorer role.
        
        Args:
            name (str): The name identifier for this scorer instance
            profile (str): The role profile description
            **kwargs: Additional keyword arguments passed to parent Role class
        """
        super().__init__(name=name, profile=profile, **kwargs)
        self.set_actions([Score])  # Set up scoring action capability
        self.name = name

    async def _observe(self) -> int:
        """Monitor for new evaluation messages that need scoring.
        
        This method filters messages to only process those specifically sent to this scorer,
        ignoring messages from previous rounds or those meant for other roles.
        
        Returns:
            int: Number of new messages to process
        """
        await super()._observe()
        # Filter messages to only those addressed to this scorer
        self.rc.news = [msg for msg in self.rc.news if self.name in msg.send_to]
        return len(self.rc.news)

    async def _act(self) -> Message:
        """Process evaluation results and generate a score.
        
        This method:
        1. Logs the current action being taken
        2. Retrieves relevant context from memory
        3. Dynamically Runs the scoring action on the evaluation results
        4. Creates and stores a message with the scoring results
        
        Returns:
            Message: A message containing the scoring results
        """
        logger.info(f"{self._setting}: ready to {self.rc.todo}")
        todo = self.rc.todo

        # Get historical context from memory
        memories = self.get_memories()
        context = "\n".join(f"{msg.sent_from}: {msg.content}" for msg in memories)

        # Run scoring action
        rsp = await todo.run(context=context)

        # Create and store response message
        msg = Message(
            content=rsp,
            role=self.profile,
            cause_by=todo,
            sent_from=self.name,
        )

        self.rc.memory.add(msg)

        return msg