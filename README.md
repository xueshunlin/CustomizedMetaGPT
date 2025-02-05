# CustomizedMetaGPT
This is a customized MetaGPT project tailored for fast conversion of prototype/research level codes into professional/production level codes. For more details, please refer to [MetaGPT Online Document](https://docs.deepwisdom.ai/main/en/)

## Table of Contents
- [Core Concept](#core-concept)
- [Structure](#structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Tutorial](#tutorial)
- [Installation](#installation)
- [Configuration](#configuration)
- [License](#license)

## Core Concept

<details>
<summary>Motivation</summary>

This project addresses a critical need in the project development workflow: the transformation of prototype/research-level code (typically in Jupyter Notebooks) into production-ready, modular code. This motivation is achieved in several key aspects of the project:

1. **Notebook Decomposition**: The project specifically targets the challenge of breaking down monolithic Jupyter Notebooks into maintainable modules, so that the developers can work on individual components more effectively.

2. **Automated Modularization**: The system employs a sophisticated LLM multi-agent approach to analyze and modularize code, with specialized pre-defined roles and actions.

3. **Quality-Focused Architecture**: The system implements multiple techniques to improve the quality of the modularized code, including e.g. the integration of RAG system to improve the regeneration accuracy, the built-in evaluation workflow with multiple standards to check the result code quality.
</details>

<details>
<summary>Key Components</summary>

The system architecture combines several innovative components and technical approaches to achieve its goals.           

1. **Modularization Company**
- Orchestrates the entire code modularizing process
- Coordinates multiple AI agents for different aspects of code analysis and transformation
- Store relative documentation generated during the process

2. **Evaluation Company**
- Provides independent assessment of modularized code
- Ensures quality standards are met
- Validates the effectiveness of the modularization work

3. **RAG Integration**
- Utilizes Retrieval-Augmented Generation for context-aware code understanding, and bypass the limitation of the LLM context length
- Maintains knowledge continuity throughout the modularization process
- Serves as the foundation for Evaluation Company by enabling direct chunk-to-module comparisons between original and modularized code

4. **LLM as a Judge Integration**
- Overcome the difficulties in systematic evaluation framework for assessing LLM-generated code quality
- Enables multi-agent debate mechanism to mitigate single-perspective limitations
- Applies structured evaluation standards through specialized scoring rubrics

The system is designed to be both flexible and robust, capable of handling various types of research code while maintaining the original functionality and logic of the source material. It emphasizes the production of clean, well-documented, and maintainable code that follows professional software engineering practices.
</details>

## Tutorial
To see the detail workflow of the modularization process, please refer to the [Workflow details](metagpt/README.md)

You are encouraged to check this [CustomizedMetagpt demo](https://drive.google.com/file/d/1BVGVU5Lxb5P764i410a14s3wWxIeXxvv/view?usp=sharing) to check for the operation details

## Structure
The project repo's structure is arranged as follows:

```bash
CustomizedMetaGPT/
├── assests/                             # Static resources used in readme
├── logs/                                # Directory for log files and debugging information
├──🔹metagpt/                            # **Main package source code directory**
│   ├── actions/                         # Action implementations for different tasks
│   ├── configs/                         # Configuration files and settings
│   ├── document_store/                  # Document storage and management
│   ├── environment/                     # Environment setup and management
│   ├── memory/                          # Memory management components
│   ├── prompts/                         # LLM prompt templates and definitions
│   ├── provider/                        # Service provider implementations
│   ├── rag/                             # Retrieval-Augmented Generation components
│   ├── roles/                           # Role definitions and behaviors
│   ├── strategy/                        # Strategy implementations
│   ├── tools/                           # Utility tools and helpers
│   └── utils/                           # General utility functions
├── .gitignore                           # Git ignore rules for version control
├── LICENSE                              # Project license information (Apache 2.0)
├── README.md                            # Project documentation and getting started guide
├── requirements.txt                     # Python package dependencies
├── ruff.toml                            # Configuration for the Ruff Python linter
└── setup.py                             # Python package setup and installation script
```

## Prerequisites

Ensure you have the following installed:

- Anaconda environment
- OpenAI API key (or other avaliable LLM API keys)

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/IHPC-Quantum/CustomizedMetaGPT.git
   cd CustomizedMetaGPT
   ```

2. Create and activate a virtual environment:

   ```bash
   conda create --name customizedmetagpt python=3.9
   conda activate customizedmetagpt
   ```

3. Install dependencies:

   ```bash
   pip install -e .
   pip install -e .[rag] #RAG modules(for Bash)
   pip install -e '.[rag]' #RAG modules(for zsh)
   ```

## Configuration

Before running the script, ensure you have a valid configuration for MetaGPT.

1. Initialize the configuration file:

   ```bash
   customizedmetagpt --init-config
   ```

2. Edit the `config2.yaml` file located in `~/.config/metagpt/` (or the equivalent directory on your system), and add your API key:

   ```yaml
    llm:
    api_type: 'openai'  # Options: openai, azure, ollama, groq, etc.
    model: 'gpt-4-turbo'  # Options: gpt-4-turbo, gpt-3.5-turbo, etc.
    base_url: 'https://api.openai.com/v1'  # Use OpenAI or a custom LLM endpoint.
    api_key: 'YOUR_API_KEY'  # Replace with your actual API key.
    # proxy: 'YOUR_LLM_PROXY_IF_NEEDED'  # Optional: Set a proxy if required.
    # pricing_plan: 'YOUR_PRICING_PLAN'  # Optional: Specify if different from the `model`.
    ```

    This configuration ensures that your API credentials are securely stored locally and used correctly when interacting with the LLM.

## Quick Start

### Run Modularization Company to modularize your prototype code

Use the following command to start a automated modularizing:

```bash
python modularization_company.py
```

You can customize the execution with various options:

```bash
python modularization_company.py  --investment 5.0 --n-round 8 --code-review False --run-tests False --project_path "/Your/Prototype/Path"
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--investment` | Investment amount (default: 5.0) |
| `--n-round` | Number of simulation rounds (default: 8)(one role takes one round to finish its task) |
| `--code-review` | Enable code review (default: False) |
| `--run-tests` | Enable QA testing (default: False) |
| `--project-path` | Path to your prototype repo for modularization|
| `--init-config` | Initialize MetaGPT config file |

> [!NOTE]
> 1. You must prepare a the repo of the prototype code first, indicated by the `--project-path` option.
> 2. This command cannot run twice as the documentations would be generated during the first time, which would stop the second execution. Make sure you cleaned up all generated docs, or reassign the address of the project if you want to test the modularization of a repo for multiple times.

## Run Evaluation Company to evaluate the modularization outcome
Use the following command to start the evaluation on modularized codes:

```bash
python evaluation_company.py
```
You can also customize this execution with the options supported below:

| Option | Description |
|--------|-------------|
| `--investment` | Investment amount (default: 5.0) |
| `--total-rounds` | Number of simulation rounds (default: 8)(one role takes one round to finish its task) |
| `--evaluation-rounds` | Number of evaluation rounds (default: 3) (for each evaluation, there would be 3 rounds)|
| `--project-path` | Path to your prototype repo for modularization|

## License

This project is licensed under the Apache 2.0 License.
