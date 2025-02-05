from metagpt.actions.prepare_documents import PrepareEvaluatorDocuments
from metagpt.actions import ChunkInspection
from metagpt.logs import logger
from metagpt.roles.role import Role, RoleReactMode


class Inspector(Role):
    """Inspector role that manages code context retrieval for evaluation.
    
    This role is responsible for:
    1. Extracting code chunks from original Jupyter Notebooks
    2. Finding corresponding modularized script sections from the RAG system
    3. Providing paired code contexts to evaluators for comparison
    4. Ensuring evaluators have proper context for assessment
    """
    
    name: str = "Galvin"  # Name of the inspector role
    profile: str = "Inspector"  # Role profile description
    goal: str = "Extract the Jupytor Notebook chunk respectively and the relative modularized scripts from the RAG to provide as code context for the evaluators"

    def __init__(self, *args, **kwargs):
        """Initialize the Inspector role with necessary actions and configurations.
        
        Args:
            *args: Variable length argument list passed to parent Role class
            **kwargs: Arbitrary keyword arguments passed to parent Role class
        """
        super().__init__(*args, **kwargs)
        
        # Set up actions this role can perform
        self.set_actions([ChunkInspection])  # Primary action for code chunk inspection
        self._watch({PrepareEvaluatorDocuments})  # Monitor document preparation process
        self.rc.react_mode = RoleReactMode.BY_ORDER  # Process actions sequentially
    
    async def _observe(self, ignore_memory=False) -> int:
        """Override observation behavior to always ignore memory.
        
        The inspector needs fresh context each time rather than relying on memory
        of previous operations.
        
        Args:
            ignore_memory: Boolean flag to ignore role memory (always True for Inspector)
            
        Returns:
            int: Number of new messages observed
        """
        return await super()._observe(ignore_memory=True)