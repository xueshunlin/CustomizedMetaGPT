#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 19:26
@Author  : alexanderwu
@File    : design_api.py
@Modified By: mashenquan, 2023/11/27.
            1. According to Section 2.2.3.1 of RFC 135, replace file data in the message with the file name.
            2. According to the design in Section 2.2.3.5.3 of RFC 135, add incremental iteration functionality.
@Modified By: mashenquan, 2023/12/5. Move the generation logic of the project name to WritePRD.
"""
import json
from pathlib import Path
from typing import Optional
from metagpt.utils.file_repository import FileRepository

from metagpt.actions import Action, ActionOutput
from metagpt.actions.design_api_an import (
    DATA_STRUCTURES_AND_INTERFACES,  # For defining class diagrams and interfaces
    DECOMPOSE_DESIGN_NODE,          # For breaking down design into components
    PROGRAM_CALL_FLOW,             # For sequence diagrams showing program flow
    REFINED_DATA_STRUCTURES_AND_INTERFACES,  # For updating existing structures
    REFINED_DESIGN_NODE,           # For refining existing designs
    REFINED_PROGRAM_CALL_FLOW,     # For updating program flows
)
from metagpt.const import DATA_API_DESIGN_FILE_REPO, SEQ_FLOW_FILE_REPO
from metagpt.logs import logger
from metagpt.schema import Document, Documents, Message
from metagpt.utils.mermaid import mermaid_to_file

# Template for combining existing design with new requirements
# Used when updating/refining existing system designs
NEW_REQ_TEMPLATE = """
### Legacy Content
{old_design}

### New Requirements
{context}
"""

class WriteExtractionDesign(Action):
    """
    Action class responsible for creating and managing system design documentation.
    This includes handling both new designs and updates to existing ones based on
    changed PRD documents.
    """
    name: str = ""
    i_context: Optional[str] = None
    desc: str = (
        "Based on the PRD, think about the system design, and design the corresponding APIs, "
        "data structures, library tables, processes, and paths. Please provide your design, feedback "
        "clearly and in detail."
    )

    async def run(self, with_messages: Message):
        """
        Main execution method that processes PRD changes and updates system designs accordingly.
        Identifies changed PRDs and design documents, then regenerates design content as needed.
        """
        # Track changes in PRD and system design documents
        changed_prds = self.repo.docs.prd.changed_files
        changed_system_designs = self.repo.docs.system_design.changed_files

        # Process changed PRDs and regenerate corresponding design documents
        changed_files = Documents()
        for filename in changed_prds.keys():
            doc = await self._update_system_design(filename=filename)
            changed_files.docs[filename] = doc
            
        if not changed_files.docs:
            logger.info("Nothing has changed.")
        return ActionOutput(content=changed_files.model_dump_json(), instruct_content=changed_files)

    async def _new_system_design(self, context):
        """Creates a new system design based on provided context and notebook content."""
        node = await DECOMPOSE_DESIGN_NODE.fill(context=context+" \n## notebook content: "+self.i_context, llm=self.llm)
        return node

    async def _merge(self, prd_doc, system_design_doc):
        """Merges existing system design with new requirements from updated PRD."""
        context = NEW_REQ_TEMPLATE.format(old_design=system_design_doc.content, context=prd_doc.content)
        node = await REFINED_DESIGN_NODE.fill(context=context, llm=self.llm)
        system_design_doc.content = node.instruct_content.model_dump_json()
        return system_design_doc

    async def _update_system_design(self, filename) -> Document:
        """
        Updates system design documentation for a given PRD file.
        Generates new design content and saves associated diagrams.
        """
        prd = await self.repo.docs.prd.get(filename)
        system_design = await self._new_system_design(context=prd.content)
        doc = await self.repo.docs.system_design.save(
            filename=FileRepository.new_filename() + ".json",
            content=system_design.instruct_content.model_dump_json(),
            dependencies={prd.root_relative_path},
        )
        # Generate and save associated diagrams
        await self._save_data_api_design(doc)
        await self._save_seq_flow(doc)
        return doc

    async def _save_data_api_design(self, design_doc):
        """Saves class diagram visualizations from the system design."""
        m = json.loads(design_doc.content)
        data_api_design = m.get(DATA_STRUCTURES_AND_INTERFACES.key) or m.get(REFINED_DATA_STRUCTURES_AND_INTERFACES.key)
        if not data_api_design:
            return
        pathname = self.repo.workdir / DATA_API_DESIGN_FILE_REPO / Path(design_doc.filename).with_suffix("")
        await self._save_mermaid_file(data_api_design, pathname)
        logger.info(f"Save class view to {str(pathname)}")

    async def _save_seq_flow(self, design_doc):
        """Saves sequence diagram visualizations from the system design."""
        m = json.loads(design_doc.content)
        seq_flow = m.get(PROGRAM_CALL_FLOW.key) or m.get(REFINED_PROGRAM_CALL_FLOW.key)
        if not seq_flow:
            return
        pathname = self.repo.workdir / Path(SEQ_FLOW_FILE_REPO) / Path(design_doc.filename).with_suffix("")
        await self._save_mermaid_file(seq_flow, pathname)
        logger.info(f"Saving sequence flow to {str(pathname)}")

    async def _save_mermaid_file(self, data: str, pathname: Path):
        """Utility method to save Mermaid diagram files."""
        pathname.parent.mkdir(parents=True, exist_ok=True)
        await mermaid_to_file(self.config.mermaid.engine, data, pathname)