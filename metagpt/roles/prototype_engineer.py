
from metagpt.roles.role import Role, RoleReactMode
from metagpt.actions.summarize_code import SummarizeCode


class prototype_engineer(Role):
    """
    Represents a prototype engineer role responsible for developing and testing prototypes.

    Attributes:
        name (str): Name of the prototype engineer.
        profile (str): Role profile, default is 'Prototype Engineer'.
        goal (str): Goal of the prototype engineer.
        constraints (str): Constraints or limitations for the prototype engineer.
    """

    name: str = "Charlie"
    profile: str = "Prototype Engineer"
    goal: str = "Focuses on reading and understanding the initial prototypes and extracting the core logic and functionality"
    constraints: str = "utilize the same language as the user requirements for seamless communication"
    todo_action: str = ""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.set_actions([SummarizeCode])
        self._watch([])
        self.rc.react_mode = RoleReactMode.BY_ORDER
        self.todo_action = ""

    async def _observe(self, ignore_memory=False) -> int:
        return await super()._observe(ignore_memory=True)