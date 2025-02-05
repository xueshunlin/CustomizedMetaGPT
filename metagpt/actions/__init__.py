#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:44
@Author  : alexanderwu
@File    : __init__.py
"""
from enum import Enum

from metagpt.actions.action import Action
from metagpt.actions.action_output import ActionOutput
from metagpt.actions.add_requirement import UserRequirement
from metagpt.actions.debug_error import DebugError
from metagpt.actions.design_api_review import DesignReview
from metagpt.actions.project_management import WriteTasks
from metagpt.actions.research import CollectLinks, WebBrowseAndSummarize, ConductResearch
from metagpt.actions.prepare_documents import PrepareDocuments_Predefined_Requirement, PrepareEvaluatorDocuments
from metagpt.actions.speak import Speak
from metagpt.actions.chunk_inspection import ChunkInspection
from metagpt.actions.run_code import RunCode
from metagpt.actions.summarize import Summarize
from metagpt.actions.review import Review
from metagpt.actions.score import Score
from metagpt.actions.search_and_summarize import SearchAndSummarize
from metagpt.actions.notebook_convert import NotebookConvert
from metagpt.actions.code_intepretation import CodeIntepretation
from metagpt.actions.write_code import WriteCode
from metagpt.actions.write_code_review import WriteCodeReview
from archive.write_prd import WritePRD
from archive.write_prd_review import WritePRDReview
from metagpt.actions.write_test import WriteTest


class ActionType(Enum):
    """All types of Actions, used for indexing."""

    ADD_REQUIREMENT = UserRequirement
    WRITE_PRD = WritePRD
    WRITE_PRD_REVIEW = WritePRDReview
    DESIGN_REVIEW = DesignReview
    WRTIE_CODE = WriteCode
    WRITE_CODE_REVIEW = WriteCodeReview
    WRITE_TEST = WriteTest
    RUN_CODE = RunCode
    DEBUG_ERROR = DebugError
    WRITE_TASKS = WriteTasks
    SEARCH_AND_SUMMARIZE = SearchAndSummarize
    COLLECT_LINKS = CollectLinks
    WEB_BROWSE_AND_SUMMARIZE = WebBrowseAndSummarize
    CONDUCT_RESEARCH = ConductResearch
    NOTEBOOK_CONVERT = NotebookConvert
    CODE_INTERPRETATION = CodeIntepretation
    CHUNK_INSPECTION = ChunkInspection
    SPEAK = Speak
    PREPARE_DOCUMENTS = PrepareDocuments_Predefined_Requirement
    PREPARE_EVALUATOR_DOCUMENTS = PrepareEvaluatorDocuments
    REVIEW = Review
    SUMMARIZE = Summarize
    SCORE = Score



__all__ = [
    "ActionType",
    "Action",
    "ActionOutput",
    "UserRequirement",
    "DebugError",
    "DesignReview",
    "WriteTasks",
    "CollectLinks",
    "WebBrowseAndSummarize",
    "ConductResearch",
    "PrepareDocuments_Predefined_Requirement",
    "PrepareEvaluatorDocuments",
    "Speak",
    "ChunkInspection",
    "RunCode",
    "Summarize",
    "Review",
    "SearchAndSummarize",
    "NotebookConvert",
    "CodeIntepretation",
    "WriteCode",
    "WriteCodeReview",
    "WritePRD",
    "WritePRDReview",
    "WriteTest",
    "ExecuteNbCode",
    "WriteAnalysisCode",
    "WritePlan",
    "Score"
]
