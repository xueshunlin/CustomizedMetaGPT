# Import required actions and utilities for notebook conversion
from metagpt.actions.prepare_documents import PrepareDocuments_Predefined_Requirement
from metagpt.actions import NotebookConvert
from metagpt.logs import logger
from metagpt.roles.role import Role, RoleReactMode


class NotebookConverter(Role):
    """A role responsible for converting Jupyter notebooks into modular Python scripts.
    
    This role is part of the modularization process that helps transform monolithic 
    Jupyter notebooks into maintainable Python modules. It works by extracting Python 
    code from notebooks and saving it as .py files in the notebook directory.
    """
    
    name: str = "Ken"  # Name identifier for the role
    profile: str = "NotebookConverter"  # Role profile description
    goal: str = "Extract the python code from the notebook and save it to a .py file in the notebook directory"
    
    def __init__(self, *args, **kwargs):
        """Initialize the NotebookConverter role.
        
        Sets up the role with NotebookConvert action and watches for document preparation
        requirements. Uses BY_ORDER reaction mode to ensure sequential processing.
        """
        super().__init__(*args, **kwargs)
        
        # Set the primary action for notebook conversion
        self.set_actions([NotebookConvert])
        # Watch for document preparation requirements
        self._watch({PrepareDocuments_Predefined_Requirement})
        # Set reaction mode to process actions in order
        self.rc.react_mode = RoleReactMode.BY_ORDER
    
    async def _observe(self, ignore_memory=False) -> int:
        """Override the base observe method to always ignore memory.
        
        This ensures fresh processing of notebooks without caching,
        preventing stale conversions.
        
        Returns:
            int: Status code of the observation
        """
        return await super()._observe(ignore_memory=True)