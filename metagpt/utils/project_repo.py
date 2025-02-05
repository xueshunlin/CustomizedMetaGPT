#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/8
@Author  : mashenquan
@File    : project_repo.py
@Desc    : Wrapper for GitRepository and FileRepository of project.
    Implementation of Chapter 4.6 of https://deepwisdom.feishu.cn/wiki/CUK4wImd7id9WlkQBNscIe9cnqh
"""
from __future__ import annotations

from pathlib import Path

from metagpt.const import (
    SCRIPTS_FILE_REPO,
    DOCS_FILE_REPO,
    PRDS_FILE_REPO,
    REQUIREMENT_FILENAME,
    SYSTEM_DESIGN_FILE_REPO,
    TASK_FILE_REPO,
    TEST_CODES_FILE_REPO,
    TEST_OUTPUTS_FILE_REPO,
    EVAL_SUMMARIZATIONS_FILE_REPO,
)
from metagpt.utils.file_repository import FileRepository
from metagpt.utils.git_repository import GitRepository


class DocFileRepositories(FileRepository):
    prd: FileRepository
    code_interpretation: FileRepository
    system_design: FileRepository
    task: FileRepository
    eval_summarizations: FileRepository

    def __init__(self, git_repo):
        super().__init__(git_repo=git_repo, relative_path=DOCS_FILE_REPO)

        self.prd = git_repo.new_file_repository(relative_path=PRDS_FILE_REPO)
        self.system_design = git_repo.new_file_repository(relative_path=SYSTEM_DESIGN_FILE_REPO)
        self.eval_summarizations = self._git_repo.new_file_repository(relative_path=EVAL_SUMMARIZATIONS_FILE_REPO)
        self.task = git_repo.new_file_repository(relative_path=TASK_FILE_REPO)


class ProjectRepo(FileRepository):
    def __init__(self, root: str | Path | GitRepository):
        if isinstance(root, str) or isinstance(root, Path):
            git_repo_ = GitRepository(local_path=Path(root))
        elif isinstance(root, GitRepository):
            git_repo_ = root
        else:
            raise ValueError("Invalid root")
        super().__init__(git_repo=git_repo_, relative_path=Path("."))
        self._git_repo = git_repo_
        self.docs = DocFileRepositories(self._git_repo)
        self.scripts = self._git_repo.new_file_repository(relative_path=SCRIPTS_FILE_REPO)
        self.tests = self._git_repo.new_file_repository(relative_path=TEST_CODES_FILE_REPO)
        self.test_outputs = self._git_repo.new_file_repository(relative_path=TEST_OUTPUTS_FILE_REPO)
        self._srcs_path = None
        self.code_files_exists()

    def __str__(self):
        repo_str = f"ProjectRepo({self._git_repo.workdir})"
        docs_str = f"Docs({self.docs.all_files})"
        return f"{repo_str}\n{docs_str}"

    @property
    async def requirement(self):
        return await self.docs.get(filename=REQUIREMENT_FILENAME)

    @property
    def git_repo(self) -> GitRepository:
        return self._git_repo

    @property
    def workdir(self) -> Path:
        return Path(self.git_repo.workdir)

    @property
    def srcs(self) -> FileRepository:
        if not self._srcs_path:
            raise ValueError("Project Path do not exist!")
        return self._git_repo.new_file_repository(self._srcs_path)

    def code_files_exists(self) -> bool:
        git_workdir = self.git_repo.workdir
        src_workdir = git_workdir / git_workdir.name
        if not src_workdir.exists():
            return False
        code_files = self.with_src_path(path=git_workdir / git_workdir.name).srcs.all_files
        if not code_files:
            return False
        return bool(code_files)

    def with_src_path(self, path: str | Path) -> ProjectRepo:
        try:
            self._srcs_path = Path(path).relative_to(self.workdir)
        except ValueError:
            self._srcs_path = Path(path)
        return self

    @property
    def src_relative_path(self) -> Path | None:
        return self._srcs_path
