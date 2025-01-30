#!/bin/bash

# Download docker image
docker image pull ollama/ollama

# Install conda env
conda env create -f env.yaml