#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 14:43
@Author  : alexanderwu
@File    : architect.py

This module implements the Architect role in the modularization workflow, which is responsible for:
1. Analyzing and designing modular system architecture from notebook content
2. Creating scalable and maintainable component structures
3. Ensuring proper decomposition of monolithic code into independent modules
4. Integrating with RAG (Retrieval Augmented Generation) for context-aware design
"""

from metagpt.actions import WritePRD
from metagpt.actions.design_api import WriteExtractionDesign
from metagpt.roles.role import Role
from metagpt.actions import CodeIntepretation
from metagpt.rag.engines import SimpleEngine
from metagpt.rag.schema import FAISSIndexConfig
from metagpt.schema import Message
from metagpt.const import RAG_ENGINE_DIR

class Architect(Role):
    """
    Represents an Architect role in the software development process.
    
    The Architect is a key role in the modularization workflow that:
    - Analyzes code chunks stored in the RAG database
    - Designs modular system architecture for code decomposition
    - Creates documentation for component interfaces and dependencies
    - Ensures architectural decisions align with project requirements
    
    Attributes:
        name (str): Name of the architect, defaults to "Bob"
        profile (str): Role profile identifier
        goal (str): Primary objective of creating modular, scalable architecture
        constraints (str): Guidelines for architectural decisions
    """

    name: str = "Bob"
    profile: str = "Architect"
    goal: str = "Design a modular, scalable, and maintainable system architecture that effectively decomposes the notebook content into independent components, ensuring usability and alignment with the original functionality."
    constraints: str = (
        "make sure the architecture is simple enough and use appropriate open source "
        "libraries. Use same language as user requirement"
    )

    def __init__(self, **kwargs) -> None:
        """
        Initialize the Architect role with specific actions and event watchers.
        Sets up RAG integration for context-aware architectural decisions.
        """
        super().__init__(**kwargs)
        # Initialize the architect with WriteExtractionDesign action for modularization
        self.set_actions([WriteExtractionDesign])
        
        # Watch for code interpretation events to inform architectural decisions
        self._watch({CodeIntepretation})
    
    async def _act(self):
        """
        Execute the architect's main workflow:
        1. Set up RAG engine with FAISS index for efficient retrieval
        2. Process code chunks from document store
        3. Generate modular design for each code segment
        4. Create and store architectural documentation
        
        Returns:
            Message: Status message about architectural design completion
        """
        # Initialize RAG engine with FAISS index for code context retrieval
        pathname = self.git_repo.workdir / RAG_ENGINE_DIR
        config = FAISSIndexConfig(persist_path= pathname)
        engine = SimpleEngine.from_index(index_config=config)

        write_summary = []

        # Process each code chunk from document store
        docs  = engine.retriever._docstore.docs
        for node in docs:
            content = docs[node].text
            write_summary.append(WriteExtractionDesign(i_context = content, context=self.context))  

        # Execute design tasks for each code segment
        for todo in write_summary:
            await todo.run(self.rc.history)

        # Create completion message
        msg = Message(content="", role=self.profile, cause_by=self.rc.todo, sent_from=self)
    
        self.rc.memory.add(msg)

        return msg

