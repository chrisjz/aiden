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

### Starting Services

You can start specific services of the AIden AI using profiles. Profiles allow you to choose which services to run and whether to use CPU or GPU resources.

- **Start all services with GPU support:**
  ```shell
  docker compose --profile vision-gpu --profile cognitive-gpu up -d
  ```

- **Start all services in CPU-only mode:**
  ```shell
  docker compose --profile vision-cpu --profile cognitive-cpu up -d
  ```

- **Start only the auditory service:**
  ```shell
  docker compose --profile auditory up -d
  ```

- **Start the vision service with GPU support:**
  ```shell
  docker compose --profile vision-gpu up -d
  ```

- **Start the cognitive service in CPU-only mode:**
  ```shell
  docker compose --profile cognitive-cpu up -d
  ```

### Stopping Services

To stop services, you need to use the same profiles that were used to start them. For example:

- **Stop all services with GPU support:**
  ```shell
  docker compose --profile vision-gpu --profile cognitive-gpu stop
  ```

- **Stop all services in CPU-only mode:**
  ```shell
  docker compose --profile vision-cpu --profile cognitive-cpu stop
  ```

- **Stop only the auditory service:**
  ```shell
  docker compose --profile auditory stop
  ```

- **Stop the vision service with GPU support:**
  ```shell
  docker compose --profile vision-gpu stop
  ```

- **Stop the cognitive service in CPU-only mode:**
  ```shell
  docker compose --profile cognitive-cpu stop
  ```

### Service Notes

- The services are optional and can be started individually or in combination based on your requirements.
- You can choose between CPU and GPU profiles for the `vision-api` and `cognitive-api` services depending on your hardware and performance needs.
- The `auditory-api` service does not have separate CPU and GPU profiles.

### Starting Simulation

Run the Unity simulation.
