#!/bin/sh

# Start the Ollama service in the background
ollama start &

# Wait for the Ollama service to be fully initialized
sleep 5

# Run Ollama with the specified model
ollama run "$MODEL_COGNITIVE"
