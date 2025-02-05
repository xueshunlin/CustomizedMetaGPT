#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/14 15:28
@Author  : alexanderwu
@File    : project_management_an.py
"""
from typing import List, Optional

from metagpt.actions.action_node import ActionNode

REQUIRED_PACKAGES = ActionNode(
    key="Required packages",
    expected_type=Optional[List[str]],
    instruction="Provide required third-party packages in requirements.txt format.",
    example=["flask==1.1.2", "bcrypt==3.2.0"],
)

REQUIRED_OTHER_LANGUAGE_PACKAGES = ActionNode(
    key="Required Other language third-party packages",
    expected_type=List[str],
    instruction="List down the required packages for languages other than Python.",
    example=["No third-party dependencies required"],
)

INTEGRATION_ANALYSIS = ActionNode(
    key="Integration Analysis",
    expected_type=List[dict],
    instruction="""Integrate the decomposed files from the provided list. Review each file's information carefully to identify and combine files with overlapping or similar functionalities. Consolidate redundant files into single, logically organized files to improve efficiency and readability while ensuring NO FUNCTIONALITY IS LOST OR OMITTED.

    Ensure:
    1. Based on any correlated description, similar or related files or functions across files should be grouped together into a single file.
    2. Provide a explicit description for each integrated file, explaining its primary purpose.
    3. YOU MUST List the functions for each file, ensuring each function corresponds to the overall functionality and purpose of the file.
    4. While integrating, you MUST retain all the details and functionality of the original files. Every feature or component from the original files must be accounted for and included in the consolidated structure.
    5. Collect and include ALL constants scattered across different files when integrated into a single file.
    6. Ensure the code structure is logical, modular, and well-documented to enhance readability and maintainability.
    7. **YOU MUST INCLUDE** a `main.py` file. This file will act as the central entry point for the project, orchestrating the application's flow. It should integrate and demonstrate the functionality of all other consolidated files.
    """,
    example=[
        {
            "file": "src/data_processing.py",
            "description": "Handles data preprocessing, including normalization, missing value handling, feature encoding, and other data preparation steps...",
            "constants": [
                {"name": "API_KEY", "value": "YOUR_API_KEY_HERE", "purpose": "API key for external data access"},
                {"name": "DATA_DIR", "value": "./data/", "purpose": "Directory for input data files"}
            ],
            "functions": [
                {"signature:": "handle_missing_values(dataframe: DataFrame) -> DataFrame", "description": "Cleans the input DataFrame by handling missing values through..."},
                {"signature": "normalize_data(dataframe: DataFrame) -> DataFrame", "description": "Normalizes numerical columns in the DataFrame to a uniform scale..."},
            ],
        },
        {
            "file": "main.py",
            "description": "Entry point for the project, orchestrates the flow of the application and coordinates all integrated functions.",
            "constants": [
                {"name": "...", "value": "...", "purpose": "..."}
            ],
            "functions": [
                {"signature": "run_app() -> None", "description": " ... "},
                {"signature": "....", "description": " ... "},
            ],
        },
    ]
)



REFINED_LOGIC_ANALYSIS = ActionNode(
    key="Refined Logic Analysis",
    expected_type=List[List[str]],
    instruction="Review and refine the logic analysis by merging the Legacy Content and Incremental Content. "
    "Provide a comprehensive list of files with classes/methods/functions to be implemented or modified incrementally. "
    "Include dependency analysis, consider potential impacts on existing code, and document necessary imports.",
    example=[
        ["src/game.py", "Contains Game class and ... functions"],
        ["src/main.py", "Contains main function, from game import Game"],
        ["src/new_feature.py", "Introduces NewFeature class and related functions"],
        ["utils/utils.py", "Modifies existing utility functions to support incremental changes"],
    ],
)

TASK_LIST = ActionNode(
    key="Task list",
    expected_type=List[str],
    instruction="Arrange the tasks into a list of filenames, prioritized by dependency order.",
    example=["src/game.py", "src/main.py"],
)

REFINED_TASK_LIST = ActionNode(
    key="Refined Task list",
    expected_type=List[str],
    instruction="Review and refine the combined task list after the merger of Legacy Content and Incremental Content, "
    "and consistent with Refined File List. Ensure that tasks are organized in a logical and prioritized order, "
    "considering dependencies for a streamlined and efficient development process. ",
    example=["new_feature.py", "utils", "game.py", "main.py"],
)

FULL_API_SPEC = ActionNode(
    key="Full API spec",
    expected_type=str,
    instruction="Describe all APIs using OpenAPI 3.0 spec that may be used by both frontend and backend. If front-end "
    "and back-end communication is not required, leave it blank.",
    example="openapi: 3.0.0 ...",
)

SHARED_KNOWLEDGE = ActionNode(
    key="Shared Knowledge",
    expected_type=str,
    instruction="Detail any shared knowledge, like common utility functions or configuration variables.",
    example="`game.py` contains functions shared across the project.",
)

REFINED_SHARED_KNOWLEDGE = ActionNode(
    key="Refined Shared Knowledge",
    expected_type=str,
    instruction="Update and expand shared knowledge to reflect any new elements introduced. This includes common "
    "utility functions, configuration variables for team collaboration. Retain content that is not related to "
    "incremental development but important for consistency and clarity.",
    example="`new_module.py` enhances shared utility functions for improved code reusability and collaboration.",
)


ANYTHING_UNCLEAR_PM = ActionNode(
    key="Anything UNCLEAR",
    expected_type=str,
    instruction="Mention any unclear aspects in the project management context and try to clarify them.",
    example="Clarification needed on how to start and initialize third-party libraries.",
)

NODES = [
    REQUIRED_PACKAGES,
    REQUIRED_OTHER_LANGUAGE_PACKAGES,
    INTEGRATION_ANALYSIS,
    TASK_LIST,
    ANYTHING_UNCLEAR_PM,
]

REFINED_NODES = [
    REQUIRED_PACKAGES,
    REQUIRED_OTHER_LANGUAGE_PACKAGES,
    REFINED_LOGIC_ANALYSIS,
    REFINED_TASK_LIST,
    FULL_API_SPEC,
    REFINED_SHARED_KNOWLEDGE,
    ANYTHING_UNCLEAR_PM,
]

PM_NODE = ActionNode.from_children("PM_NODE", NODES)
REFINED_PM_NODE = ActionNode.from_children("REFINED_PM_NODE", REFINED_NODES)
