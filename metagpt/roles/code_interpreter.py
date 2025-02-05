from metagpt.actions import NotebookConvert
from metagpt.roles.role import Role, RoleReactMode
from metagpt.utils.common import any_to_name
from metagpt.actions import CodeIntepretation
from const import SCRIPTS_FILE_REPO
from metagpt.logs import logger


class CodeInterpreter(Role):
    """A specialized role responsible for interpreting and summarizing code functionality.
    
    This role is part of the modularization pipeline that:
    1. Watches for completed notebook conversions
    2. Interprets the converted Python code
    3. Stores code interpretations in the RAG database for better context retrieval
    
    The role works in conjunction with NotebookConverter to process and understand code.
    """
    
    name: str = "David"  # Friendly name for the role
    profile: str = "CodeInterpreter"  # Role identifier
    goal: str = "Interpret and summarize the functionality of the code"  # Main objective

    def __init__(self, **kwargs) -> None:
        """Initialize the CodeInterpreter role.
        
        Sets up:
        1. The CodeIntepretation action for processing code
        2. Watches NotebookConvert action for new code to interpret
        3. Configures sequential execution mode
        """
        super().__init__(**kwargs)

        # Set the main action for code interpretation
        self.set_actions([CodeIntepretation])
        # Watch for completed notebook conversions to trigger interpretation
        self._watch([NotebookConvert])
        # Ensure actions are executed in order
        self.rc.react_mode = RoleReactMode.BY_ORDER

    async def _observe(self, ignore_memory=False) -> int:
        """Override observation behavior to always ignore memory.
        
        This ensures fresh interpretation of code each time, preventing
        stale or cached interpretations.
        
        Returns:
            int: Result of the observation
        """
        return await super()._observe(ignore_memory=True)