#!/bin/bash
cd python
source .venv/bin/activate
uv sync
pip install ipykernel
python -m ipykernel install --user --name=langchain-examples --display-name "LangChain Examples"
jupyter lab
