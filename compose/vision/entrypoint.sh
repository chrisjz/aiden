#!/bin/sh

# Check if the Vision API is enabled
if [ "$ENABLE_VISION_API" = "true" ]; then
    # Start the Ollama service in the background
    ollama start &

    # Wait for the Ollama service to be fully initialized
    sleep 5

    # Run your desired command with the specified model
    ollama run "$MODEL_VISION"
else
    echo "Vision API is disabled"
    # Keep the container running without starting the Vision API
    tail -f /dev/null
fi
