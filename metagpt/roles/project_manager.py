#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 15:04
@Author  : alexanderwu
@File    : project_manager.py

This module defines the ProjectManager role responsible for analyzing and organizing
modularized code tasks from Jupyter notebooks. The ProjectManager coordinates with
other roles like the Architect and Engineer to ensure proper code organization and implementation.
"""


from metagpt.actions import WriteTasks
from metagpt.actions.design_api import WriteExtractionDesign
from metagpt.roles.role import Role
from metagpt.roles.role import RoleReactMode


class ProjectManager(Role):
    """Project Manager role that analyzes and organizes modularization tasks.
    
    This role is responsible for:
    1. Analyzing modularized design files lists from Architect
    2. Creating prioritized task lists for implementation
    3. Distributing the tasks to Engineer for code implementation
    """

    # Basic role configuration
    name: str = "Eve"  # Name of the PM role
    profile: str = "Project Manager"  # Role profile description
    goal: str = (
        "Analyze and integrate the modularized file list derived from a Jupyter notebook, consolidating it into "
        "a coherent, prioritized set of tasks."
    )
    # Ensure communication matches user's language preference
    constraints: str = "use same language as user requirement"

    def __init__(self, **kwargs) -> None:
        """Initialize the Project Manager role with necessary actions and configurations.
        
        Args:
            **kwargs: Additional keyword arguments passed to parent Role class
        """
        super().__init__(**kwargs)

        # Set up actions this role can perform
        self.set_actions([WriteTasks])  # Primary action for task organization
        self._watch([WriteExtractionDesign])  # Monitor design extraction process
        self.rc.react_mode = RoleReactMode.BY_ORDER  # Process actions sequentially