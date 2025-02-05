#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/01/27
@Author  : MetaGPT Team
@File    : summarizer.py
@Desc    : Role responsible for summarizing evaluation results in the modularization process

This module implements the Summarizer role which:
1. Receives evaluation results from evaluators and reviewers
2. Synthesizes and summarizes the key findings and scores
3. Saves summaries to the project documentation
4. Helps track the quality and progress of code modularization
"""

from metagpt.logs import logger
from metagpt.roles.role import Role
from metagpt.actions import Summarize
from metagpt.schema import Message
from datetime import datetime
from pathlib import Path
from metagpt.utils.git_repository import GitRepository
from metagpt.utils.project_repo import ProjectRepo


class Summarizer(Role):
    """Role that summarizes evaluation results from code modularization reviews.
    
    This role synthesizes feedback from multiple evaluators to provide:
    - Overall assessment of modularization quality
    - Key strengths and areas for improvement
    - Recommendations for further enhancements
    
    The summaries are saved as markdown files in the project's eval_summarizations directory.
    """

    # Path to the project being evaluated
    project_path: str = ""
    
    # Main objective of this role
    goal: str = "summarize the final evaluation results",
    
    # Path where summarization results will be stored
    summarizer_project_path: str = ""

    def __init__(
        self,
        name: str,
        profile: str,
        project_path: str,
        **kwargs,
    ):
        """Initialize the Summarizer role.

        Args:
            name (str): Name identifier for this role instance
            profile (str): Description of the role's responsibilities
            project_path (str): Path to the project being evaluated
            **kwargs: Additional role configuration options
        """
        super().__init__(name=name, profile=profile, **kwargs)
        self.summarizer_project_path = project_path
        self.set_actions([Summarize])
        self.name = name

    async def _observe(self) -> int:
        """Monitor for new evaluation messages that need summarizing.
        
        Returns:
            int: Number of new messages to process
        """
        await super()._observe()
        # Only process messages specifically sent to this summarizer
        self.rc.news = [msg for msg in self.rc.news if self.name in msg.send_to]
        return len(self.rc.news)

    async def _act(self) -> Message:
        """Process evaluation messages and generate summary.
        
        This method:
        1. Logs the current action being taken
        2. Retrieves evaluation history
        3. Generates summary of evaluations
        4. Saves summary to project documentation
        5. Returns summary as a message
        
        Returns:
            Message: Contains the generated summary and metadata
        """
        logger.info(f"{self._setting}: ready to {self.rc.todo}")
        todo = self.rc.todo

        # Get full history of evaluation messages
        memories = self.rc.env.history

        # Generate summary from evaluation history
        rsp = await todo.run(context=memories, name=self.name)

        # Create filename with timestamp for the summary
        summary_filename = f"summary_{datetime.now().isoformat()}.md"

        # Initialize git repo and project structure
        self.context.git_repo = GitRepository(local_path=Path(self.summarizer_project_path), auto_init=True)
        self.context.repo = ProjectRepo(self.context.git_repo)

        # Save summary to evaluation documentation
        await self.context.repo.docs.eval_summarizations.save(
            filename=summary_filename,
            content=rsp
        )

        # Create message containing summary
        msg = Message(
            content=rsp,
            role=self.profile,
            cause_by=todo,
            sent_from=self.name,
            send_to=self.send_to,
        )

        # Store message in role's memory
        self.rc.memory.add(msg)

        return msg