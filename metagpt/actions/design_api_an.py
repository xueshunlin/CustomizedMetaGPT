#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/12 22:24
@Author  : alexanderwu
@File    : design_api_an.py
"""
from typing import List, Optional

from metagpt.actions.action_node import ActionNode
from metagpt.utils.mermaid import MMC1, MMC2

IMPLEMENTATION_APPROACH = ActionNode(
    key="Implementation approach",
    expected_type=str,
    instruction="Analyze the difficult points of the requirements, select the appropriate open-source framework",
    example="We will ...",
)

REFINED_IMPLEMENTATION_APPROACH = ActionNode(
    key="Refined Implementation Approach",
    expected_type=str,
    instruction="Update and extend the original implementation approach to reflect the evolving challenges and "
    "requirements due to incremental development. Outline the steps involved in the implementation process with the "
    "detailed strategies.",
    example="We will refine ...",
)

DECOMPOSE_IMPLEMENTATION_APPROACH = ActionNode(
    key="Decompose Implementation approach",
    expected_type=str,
    instruction="Understand and Analyze the difficult points of decomposing this Jupyter Notebook into smaller modules. Select appropriate libraries or frameworks like pandas, requests, etc. to facilitate the modularization.",
    example="This Notebook is about ..., the difficult points are ..., we will use pandas to ...",
)

PROJECT_NAME = ActionNode(
    key="Project name", expected_type=str, instruction="The project name with underline", example="game_2048"
)

FILE_LIST = ActionNode(
    key="File list",
    expected_type=List[str],
    instruction="""
    Provide relative paths for all scripts. Organize scripts into separate directories based on functionality to maintain a clean, modular project structure. 
    Ensure:
    1. A `main.py` or `app.py` is included as the entry point, ideally in the root directory or a `src/` directory.
    2. Utility scripts and core logic are placed in a `utils/` or `core/` folder.
    3. Models or data-related scripts are placed in a `models/` or `data/` folder.
    4. Any additional folders based on the project's needs.
    """,
    example=[
        "src/main.py",
        "src/core/game_logic.py",
        "src/core/engine.py",
        "src/utils/file_manager.py", 
        "src/utils/logger.py",
        "src/models/player.py",
        "src/models/enemy.py",
        "data/level_data.py",
        "data/weapon_data.py"  
    ],
)

DECOMPOSE_FILE_LIST = ActionNode(
    key="File list",
    expected_type=List[dict],
    instruction="""
    Provide relative paths for all scripts from the current notebook chunk that will be decomposed into each file.
    Organize the scripts into separate directories based on functionality to maintain a clean, modular project structure. 
    Ensure:
    1. Utility scripts and core logic are placed in a `utils/` or `core/` folder.
    2. Models or data-related scripts are placed in a `models/` or `data/` folder.
    3. Any additional folders based on the project's needs.
    4. Include any possible related functions in every modularized file.
    5. store all constants or immutable/pre-defined values extracted from the notebook, the variable should match the original name in the notebook, rememeber you NEED TO COLLECT ALL reasonable constants.
    6. Provide a clear and comprehensive description of each file's purpose accordingly, do not include any non-existing contents.
    7. Clearly specify each file's dependencies on other project files or external packages.
    8. Provide all content in the format of string.
    """,
    example=[
    {
        "file": "core/xxxx.py",
        "description": "Handles data preprocessing tasks, including missing value handling, ...",
        "functions": [
            "handle_missing_values(data: DataFrame) -> DataFrame",
            "normalize_data(data: DataFrame) -> DataFrame",
            "encode_features(data: DataFrame) -> DataFrame"
        ],
        "constants": [
                {"name": "API_KEY", "value": "YOUR_API_KEY_HERE", "purpose": "API key for external data access"},
                {"name": "DATA_DIR", "value": "./data/", "purpose": "Directory for input data files"}
            ],
        "dependencies": ["raw_data.csv"]
    },
    {
        "file": "models/xxx.py",
        "description": "Defines the training loop and model optimization steps for the machine learning pipeline.",
        "functions": [
            "train_model(model: Model, data: DataLoader) -> Model",
            "save_model(model: Model, path: str) -> None"
        ],
        "constants": [],
        "dependencies": ["core/xxx.py"]
    },
    ]
)


REFINED_FILE_LIST = ActionNode(
    key="Refined File list",
    expected_type=List[str],
    instruction="Update and expand the original file list including only relative paths. Up to 2 files can be added."
    "Ensure that the refined file list reflects the evolving structure of the project.",
    example=["main.py", "game.py", "new_feature.py"],
)

# optional,because low success reproduction of class diagram in non py project.
DATA_STRUCTURES_AND_INTERFACES = ActionNode(
    key="Data structures and interfaces",
    expected_type=Optional[str],
    instruction="Use mermaid classDiagram code syntax, including classes, method(__init__ etc.) and functions with type"
    " annotations, CLEARLY MARK the RELATIONSHIPS between classes, and comply with PEP8 standards. "
    "The data structures SHOULD BE VERY DETAILED and the API should be comprehensive with a complete design.",
    example=MMC1,
)

REFINED_DATA_STRUCTURES_AND_INTERFACES = ActionNode(
    key="Refined Data structures and interfaces",
    expected_type=str,
    instruction="Update and extend the existing mermaid classDiagram code syntax to incorporate new classes, "
    "methods (including __init__), and functions with precise type annotations. Delineate additional "
    "relationships between classes, ensuring clarity and adherence to PEP8 standards."
    "Retain content that is not related to incremental development but important for consistency and clarity.",
    example=MMC1,
)

PROGRAM_CALL_FLOW = ActionNode(
    key="Program call flow",
    expected_type=Optional[str],
    instruction="Use sequenceDiagram code syntax, COMPLETE and VERY DETAILED, using CLASSES AND API DEFINED ABOVE "
    "accurately, covering the CRUD AND INIT of each object, SYNTAX MUST BE CORRECT.",
    example=MMC2,
)

REFINED_PROGRAM_CALL_FLOW = ActionNode(
    key="Refined Program call flow",
    expected_type=str,
    instruction="Extend the existing sequenceDiagram code syntax with detailed information, accurately covering the"
    "CRUD and initialization of each object. Ensure correct syntax usage and reflect the incremental changes introduced"
    "in the classes and API defined above. "
    "Retain content that is not related to incremental development but important for consistency and clarity.",
    example=MMC2,
)

ANYTHING_UNCLEAR = ActionNode(
    key="Anything UNCLEAR",
    expected_type=str,
    instruction="Mention unclear project aspects, then try to clarify it.",
    example="Clarification needed on third-party API integration, ...",
)

NODES = [
    IMPLEMENTATION_APPROACH,
    # PROJECT_NAME,
    FILE_LIST,
    DATA_STRUCTURES_AND_INTERFACES,
    PROGRAM_CALL_FLOW,
    ANYTHING_UNCLEAR,
]

DECOMPOSE_DESIGN_NODE = [
    DECOMPOSE_FILE_LIST
]

REFINED_NODES = [
    REFINED_IMPLEMENTATION_APPROACH,
    REFINED_FILE_LIST,
    REFINED_DATA_STRUCTURES_AND_INTERFACES,
    REFINED_PROGRAM_CALL_FLOW,
    ANYTHING_UNCLEAR,
]

DESIGN_API_NODE = ActionNode.from_children("DesignAPI", NODES)
DECOMPOSE_DESIGN_NODE = ActionNode.from_children("ExtractionDesignAPI", DECOMPOSE_DESIGN_NODE)
REFINED_DESIGN_NODE = ActionNode.from_children("RefinedDesignAPI", REFINED_NODES)
