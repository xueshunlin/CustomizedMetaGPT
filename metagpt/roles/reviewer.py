from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.actions import Review
from metagpt.actions import Speak
from metagpt.schema import Message

class Reviewer(Role):
    """A Reviewer role that synthesizes evaluation discussions and provides conclusions.
    
    This role is part of the evaluation process in the CustomizedMetaGPT project, specifically
    designed to review the evaluation results from multi-agent debates, and provide a fair and well-reasoned feedback.
    """

    goal: str = "synthesizing diverse viewpoints from the evaluation discusstions and driving fair, well-reasoned conclusions."

    def __init__(
        self,
        name: str,          # Unique identifier for this reviewer
        profile: str,       # Role description/expertise of the reviewer
        send_to: str,       # Target recipient for review messages
        **kwargs,
    ):
        """Initialize a new Reviewer instance.
        
        Args:
            name: Unique name identifier for this reviewer
            profile: Description of reviewer's expertise/role
            send_to: Recipient for review messages (usually another agent)
            **kwargs: Additional role configuration parameters
        """
        super().__init__(name=name, profile=profile, **kwargs)
        self.set_actions([Review])    # Set Review as the primary action
        self._watch([Speak])          # Monitor Speak actions from other agents
        self.name = name
        self.send_to = send_to

    async def _observe(self) -> int:
        """Filter and process incoming messages for this reviewer.
        
        This method ensures the reviewer only processes messages specifically addressed to them,
        filtering out their own messages from previous rounds.
        
        Returns:
            int: Number of new relevant messages to process
        """
        await super()._observe()
        # Filter messages to only include those addressed to this reviewer
        self.rc.news = [msg for msg in self.rc.news if self.name in msg.send_to]
        return len(self.rc.news)

    async def _act(self) -> Message:
        """Process evaluation discussions and generate review conclusions.
        
        This method:
        1. Logs the current action status
        2. Retrieves the full discussion history
        3. Runs the review process on the context
        
        Returns:
            Message: A message containing the review conclusions and analysis
        """
        logger.info(f"{self._setting}: ready to {self.rc.todo}")
        todo = self.rc.todo

        # Get full discussion history from environment
        memories = self.rc.env.history

        # Run review process on the discussion context
        rsp = await todo.run(context=memories, name=self.name)

        # Create and store review message
        msg = Message(
            content=rsp,
            role=self.profile,
            cause_by=todo,
            sent_from=self.name,
            send_to=self.send_to,
        )

        self.rc.memory.add(msg)

        return msg