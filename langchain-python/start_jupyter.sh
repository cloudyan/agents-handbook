#!/bin/bash
cd langchain-python
source .venv/bin/activate
uv sync
pip install ipykernel
python -m ipykernel install --user --name=agents-handbook --display-name "Agents Handbook"
jupyter lab
