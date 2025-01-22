# Activate Virtual Environment using Poetry

## Installation

1. Install Poetry if not installed already:
pip install poetry

2. Configure Poetry to create virtual environments in the current directory:
poetry config virtualenvs.in-project true

## Setup Virtual Environment

1. (Optional) Install dependencies without creating a root source:
poetry install --no-root

2. Activate the virtual environment:
poetry shell

## Install Dependencies

- Install testing dependencies:
poetry add pytest-asyncio pytest --group test

- Install development dependencies:
poetry add isort pre-commit --group dev

- Install a main dependency (e.g., FastAPI):
poetry add fastapi

## Remove Dependencies

To remove a dependency from a specific group:
poetry remove pytest --group test

## Install Pre-commit Hooks

1. Install pre-commit hooks:
pre-commit install

2. Run pre-commit hooks locally:
pre-commit run --all-files
