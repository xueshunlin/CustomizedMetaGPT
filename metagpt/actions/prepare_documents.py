#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/11/20
@Author  : mashenquan
@File    : prepare_documents.py
@Desc: PrepareDocuments Action: initialize project folder and add new requirements to docs/requirements.txt.
        RFC 135 2.2.3.5.1.
"""
import shutil
from pathlib import Path
from typing import Optional

from metagpt.actions import Action, ActionOutput
from metagpt.const import REQUIREMENT_FILENAME, EVAL_RAG_ENGINE_DIR
from metagpt.schema import Documents
from metagpt.utils.file_repository import FileRepository
from metagpt.utils.git_repository import GitRepository
from metagpt.utils.project_repo import ProjectRepo
import json

from metagpt.rag.engines import SimpleEngine
from metagpt.rag.schema import LLMRankerConfig, FAISSRetrieverConfig

# Pre-defined Product Requirement Document (PRD) template for modularization work
# Contains language, programming language, goals, user stories and requirements
PRE_DEFINED_DOCUMENT = {
    "Language": "en_us",
    "Programming Language": "Python", 
    "Original Requirements": "Decompose the notebook into distinct, modular components to facilitate modular development, ease of maintenance, and improved scalability.",
    "Product Goals": [
        "Enable modular development by decomposing the Jupyter Notebook",
        "Ensure each component is independently functional and testable", 
        "Facilitate easier maintenance and scalability of the codebase"
    ],
    "User Stories": [
        "As a developer, I want to decompose a large Jupyter Notebook into smaller, modular Python scripts so that I can work on individual components more effectively, identify bugs faster, and improve specific sections of code without affecting the entire notebook",
        "As a project manager, I want to break down the monolithic Jupyter Notebook into separate modules, such as data preprocessing, model training, and visualization, so I can assign these distinct parts to different team members, optimizing parallel development and reducing bottlenecks in the workflow.",
        "As a quality assurance tester, I want to have access to the decomposed components of the Jupyter Notebook in isolated scripts or modules, so I can test each part individually, ensuring that they meet functionality and performance criteria before integrating them back into the larger system."
    ],
    "Requirement Pool": [
        ["P0", "Decompose the notebook into modules, e.g., data downloading, data loading, data processing, data visualization."],
        ["P1", "Ensure each module can run independently and interact with others as needed."],
        ["P1", "Maintain the original logic of the notebook and reuse existing code wherever possible to ensure consistency and avoid breaking the functionality."],
        ["P2", "Develop a clear interface for modules to communicate data and errors between each other."],
        ["P3", "Document the purpose and functionality of each module for developer reference."]
    ]
}

class PrepareDocuments_Predefined_Requirement(Action):
    """PrepareDocuments with predefined requirements for modularization work: initialize project folder"""

    name: str = "PrepareDocuments_Predefined_Requirement"
    i_context: Optional[str] = None  # Input context for the action

    @property
    def config(self):
        """Access configuration from context"""
        return self.context.config

    def _init_repo(self):
        """Initialize the Git environment and project repository
        Creates project directory if it doesn't exist or cleans it if it does"""
        if not self.config.project_path:
            name = self.config.project_name or FileRepository.new_filename()
            path = Path(self.config.workspace.path) / name
        else:
            path = Path(self.config.project_path)
        if path.exists() and not self.config.inc:
            shutil.rmtree(path)
        self.config.project_path = path
        self.context.git_repo = GitRepository(local_path=path, auto_init=True)
        self.context.repo = ProjectRepo(self.context.git_repo)

    async def run(self, with_messages, **kwargs):
        """Create and initialize the workspace folder, initialize the Git environment.
        Saves predefined PRD document to the repository."""
        self._init_repo()

        # Write the predefined requirements to the PRD
        new_prd_doc = await self.repo.docs.prd.save(
            filename=FileRepository.new_filename() + ".json", 
            content=json.dumps(PRE_DEFINED_DOCUMENT, indent=4)
        )
        return Documents.from_iterable(documents=[new_prd_doc]).to_action_output()
    
class PrepareEvaluatorDocuments(Action):
    """PrepareDocuments Action: initialize project folder and prepare evaluation documents"""

    name: str = "PrepareEvaluatorDocuments"
    i_context: Optional[str] = None
    _use_llm_ranker: bool = True  # Flag to enable/disable LLM ranking

    @property
    def config(self):
        """Access configuration from context"""
        return self.context.config

    def _init_repo(self):
        """Initialize the Git environment for evaluation
        Requires project path to be set"""
        if self.config.project_path:
            path = Path(self.config.project_path)
        else:
            assert False, "Project path is required for Evaluator!"

        self.config.project_path = path
        self.context.git_repo = GitRepository(local_path=path, auto_init=True)
        self.context.repo = ProjectRepo(self.context.git_repo)

    async def run(self, with_messages, **kwargs):
        """Initialize workspace and create RAG engine from source files(modularized works)
        Stores engine in evaluation directory"""
        self._init_repo()

        # Create nodes from source files for RAG engine
        src_dir = self.repo.srcs.workdir
        nodes = await SimpleEngine.from_docs_to_nodes(
            input_files=[Path(src_dir) / dir for dir in self.repo.srcs.all_files if not dir.endswith('.DS_Store')], 
            enable_chunking=False
        )

        # Configure and create RAG engine
        ranker_configs = [LLMRankerConfig()] if self._use_llm_ranker else None
        engine = SimpleEngine.from_nodes_to_engine(
            nodes=nodes,
            retriever_configs=[FAISSRetrieverConfig()],
            ranker_configs=ranker_configs,
        )

        # Save RAG engine for future use
        pathname = self.repo.workdir / EVAL_RAG_ENGINE_DIR
        pathname.mkdir(parents=True, exist_ok=True)
        engine.persist(pathname)

        
