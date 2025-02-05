from metagpt.actions import UserRequirement, PrepareDocuments_Predefined_Requirement, PrepareEvaluatorDocuments
from metagpt.roles.role import Role, RoleReactMode
from metagpt.utils.common import any_to_name


class Initializer(Role):
    """Role responsible for initializing project repository with predefined requirements
    
    This class sets up the initial project structure and documents based on a 
    predefined Product Requirement Document (PRD).
    """
    
    name: str = "Jojo"  # Name identifier for the role
    profile: str = "Initializer"  # Role profile description
    goal: str = "Initialize the project repository with the pre-defined PRD(Product Requirement Document) and required documents"
    todo_action: str = ""  # Placeholder for next action to be taken

    def __init__(self, **kwargs) -> None:
        """Initialize the Initializer role
        
        Sets up actions and watches for user requirements in sequential mode
        """
        super().__init__(**kwargs)

        # Set the action to prepare predefined requirement documents
        self.set_actions([PrepareDocuments_Predefined_Requirement])
        # Watch for any user requirements(from round 0)
        self._watch([UserRequirement])
        # Set reaction mode to sequential order
        self.rc.react_mode = RoleReactMode.BY_ORDER

    async def _observe(self, ignore_memory=False) -> int:
        """Override observation behavior to always ignore memory
        
        Returns:
            int: Result of the parent class observation
        """
        return await super()._observe(ignore_memory=True)
    

class evaluation_initializer(Role):
    """Role responsible for initializing evaluation-related components
    
    This class sets up the RAG (Retrieval Augmented Generation) engine
    for modularized files to enable evaluation.
    """

    name: str = "Kelvin"  # Name identifier for the role
    profile: str = "Evaluation_Initializer"  # Role profile description 
    goal: str = "Initialize the project repository with building up modularized files' RAG engine"
    todo_action: str = ""  # Placeholder for next action to be taken

    def __init__(self, **kwargs) -> None:
        """Initialize the evaluation initializer role
        
        Sets up actions and watches for user requirements in sequential mode
        """
        super().__init__(**kwargs)

        # Set the action to prepare evaluator documents
        self.set_actions([PrepareEvaluatorDocuments])
        # Watch for any user requirements
        self._watch([UserRequirement])
        # Set reaction mode to sequential order
        self.rc.react_mode = RoleReactMode.BY_ORDER

    async def _observe(self, ignore_memory=False) -> int:
        """Override observation behavior to always ignore memory
        
        Returns:
            int: Result of the parent class observation
        """
        return await super()._observe(ignore_memory=True)
