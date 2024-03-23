# AIden (AI Denizen)

AIden aims to create a virtual AI entity with a structure and functionality inspired by the human brain. Utilizing a hierarchical API, AIden is designed to mimic various brain regions and sensory systems, allowing for the processing of auditory, visual, olfactory, gustatory, and tactile information. The project leverages various machine learning models, including OpenAI's Whisper for speech recognition and LLaVA for visual understanding, to enable AIden to interact with and respond to its virtual environment in a human-like manner. With endpoints representing different brain areas such as the hippocampus, neocortex, and amygdala, AIden is a step towards creating a more intelligent and intuitive AI denizen that can learn, perceive, and make decisions in a complex world.

## Setup

### Prerequisites

To run the simulation locally, you will need the following:

* Python 3.11
* Docker
* Docker Compose

### Environment variables

Make a copy of `.env.template` called `.env` and update any required values.

## Usage

Start all services for the AIden AI:
```shell
docker compose up
```

Run the Unity simulation.
