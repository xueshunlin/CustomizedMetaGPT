#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module implements the evaluation company functionality for assessing modularized code quality.
It orchestrates a team of AI agents to evaluate code modularization results through multiple rounds
of assessment and scoring.
"""

import asyncio
from pathlib import Path

import agentops
import typer

from metagpt.const import CONFIG_ROOT
from metagpt.utils.project_repo import ProjectRepo

app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)

def generate_repo(
    investment=3.0,
    total_rounds=5,
    evaluation_rounds=3,
    project_path=""
) -> ProjectRepo:
    """Run the evaluation company logic to assess modularized code quality.
    
    Args:
        investment (float): Budget allocation for the evaluation process
        total_rounds (int): Total number of rounds to run the evaluation
        evaluation_rounds (int): Number of rounds specifically for evaluation discussions
        project_path (str): Path to the project being evaluated
        
    Returns:
        ProjectRepo: Repository containing evaluation results and artifacts
    """
    from metagpt.config2 import config
    from metagpt.context import Context
    from metagpt.roles import (
        evaluation_initializer,
        Inspector
    )

    from metagpt.team import Team

    # Initialize agentops for tracking if API key provided
    if config.agentops_api_key != "":
        agentops.init(config.agentops_api_key, tags=["software_company"])

    # Update configuration with CLI parameters
    config.update_via_cli(project_path, evaluation_rounds)
    ctx = Context(config=config)

    # Create and configure the evaluation team
    company = Team(context=ctx)
    company.hire(
        [   
            evaluation_initializer(),  # Initializes evaluation environment
            Inspector()               # Coordinates evaluation process
        ]
    )

    # Start evaluation process
    company.invest(investment)
    company.run_project("New Project Started.")
    asyncio.run(company.run(n_round=total_rounds))

    # Clean up agentops session
    if config.agentops_api_key != "":
        agentops.end_session("Success")

    return ctx.repo


@app.command("", help="Start a new project.")
def startup(
    investment: float = typer.Option(default=5.0, help="Dollar amount to invest in the AI company."),
    total_rounds: int = typer.Option(default=8, help="Number of rounds for the simulation."),
    evaluation_rounds: int = typer.Option(default=3, help="Number of rounds for the evaluation."),
    project_path: str = typer.Option(
        default="./workspace",
        help="Specify the directory path of the old version project to fulfill the incremental requirements.",
    ),
    init_config: bool = typer.Option(default=False, help="Initialize the configuration file for MetaGPT."),
):
    """CLI entry point to run an evaluation company.
    
    This function provides command-line interface to:
    1. Initialize MetaGPT configuration
    2. Start evaluation process with specified parameters
    """
    if init_config:
        copy_config_to()
        return

    return generate_repo(
        investment,
        total_rounds,
        evaluation_rounds,
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
    """Initialize the configuration file for MetaGPT.
    
    This function:
    1. Creates config directory if needed
    2. Backs up existing config file if present
    3. Writes default configuration template
    """
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
