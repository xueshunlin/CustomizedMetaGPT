#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from pathlib import Path

import typer

from metagpt.const import CONFIG_ROOT
from metagpt.utils.project_repo import ProjectRepo

app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)

def generate_repo(
    investment=3.0,
    n_round=5,
    code_review=True,
    run_tests=True,
    project_path=""
) -> ProjectRepo:
    """Run the startup logic for code modularization. Can be called from CLI or other Python scripts.
    
    Args:
        investment (float): Dollar amount to invest in the AI company
        n_round (int): Number of rounds for the simulation
        code_review (bool): Whether to enable code review
        run_tests (bool): Whether to enable QA testing
        project_path (str): Directory path of project to modularize
        
    Returns:
        ProjectRepo: Repository containing the modularized code
    """
    # Import required modules
    from metagpt.config2 import config
    from metagpt.context import Context
    from metagpt.roles import (
        Initializer,
        NotebookConverter, 
        CodeInterpreter,
        Architect,
        Engineer,
        ProjectManager,
        QaEngineer
    )
    
    from metagpt.team import Team

    # Update config with project path and create context
    config.update_via_cli(project_path)
    ctx = Context(config=config)

    # Initialize AI company team
    company = Team(context=ctx)
    
    # Hire core roles for modularization
    company.hire(
        [   
            Initializer(),  # Sets up project structure
            NotebookConverter(),  # Converts notebooks to Python files
            CodeInterpreter(),  # Analyzes and interprets code
            Architect(),  # Designs modular architecture
            ProjectManager(),  # Manages modularization tasks
        ]
    )

    # Add engineers with optional code review
    company.hire([Engineer(n_borg=5, use_code_review=code_review)])

    # Add QA if testing is enabled
    if run_tests:
            company.hire([QaEngineer()])
            if n_round < 15:
                n_round = 15  # Ensure enough rounds for QA actions

    # Fund and start the company
    company.invest(investment)
    company.run_project("New Project Started.")
    asyncio.run(company.run(n_round=n_round))

    return ctx.repo


@app.command("", help="Start a new project.")
def startup(
    investment: float = typer.Option(default=5.0, help="Dollar amount to invest in the AI company."),
    n_round: int = typer.Option(default=8, help="Number of rounds for the simulation."),
    code_review: bool = typer.Option(default=False, help="Whether to use code review."),
    run_tests: bool = typer.Option(default=False, help="Whether to enable QA for adding & running tests."),
    project_path: str = typer.Option(
        default="./workspace",
        help="Specify the directory path of the old version project to fulfill the incremental requirements.",
    ),
    init_config: bool = typer.Option(default=False, help="Initialize the configuration file for MetaGPT."),
):
    """Run a startup for code modularization. Be a boss."""
    if init_config:
        copy_config_to()
        return

    return generate_repo(
        investment,
        n_round,
        code_review,
        run_tests,
        project_path
    )


# Default configuration template for MetaGPT
DEFAULT_CONFIG = """# Full Example: https://github.com/geekan/MetaGPT/blob/main/config/config2.example.yaml
# Reflected Code: https://github.com/geekan/MetaGPT/blob/main/metagpt/config2.py
# Config Docs: https://docs.deepwisdom.ai/main/en/guide/get_started/configuration.html
llm:
  api_type: "openai"  # or azure / ollama / groq etc.
  model: "gpt-4-turbo"  # or gpt-3.5-turbo
  base_url: "https://api.openai.com/v1"  # or forward url / other llm url
  api_key: "YOUR_API_KEY"
"""


def copy_config_to():
    """Initialize the configuration file for MetaGPT by copying default config."""
    target_path = CONFIG_ROOT / "config2.yaml"

    # Create target directory if it doesn't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing config file if present
    if target_path.exists():
        backup_path = target_path.with_suffix(".bak")
        target_path.rename(backup_path)
        print(f"Existing configuration file backed up at {backup_path}")

    # Write new config file
    target_path.write_text(DEFAULT_CONFIG, encoding="utf-8")
    print(f"Configuration file initialized at {target_path}")


if __name__ == "__main__":
    app()
