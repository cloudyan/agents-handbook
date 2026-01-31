#!/bin/bash
cd langchain-python
source .venv/bin/activate
uv sync
pip install ipykernel
python -m ipykernel install --user --name=agent-recipes --display-name "Agents Handbook"
jupyter lab
