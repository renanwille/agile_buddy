#!/bin/bash

# Execute the docker image
docker run -d --rm -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Activate the conda environment
conda activate agile_buddy

# Start the app
python agile_buddy.py
