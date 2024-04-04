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
  docker compose --profile auditory-gpu --profile cognitive-gpu --profile vision-gpu --profile vocal-gpu up -d
  ```

- **Start all services in CPU-only mode:**
  ```shell
  docker compose --profile auditory-cpu --profile cognitive-cpu --profile vision-cpu --profile vocal-cpu up -d
  ```

You can also have any combination of CPU and GPU services.

For the Vocal API, you will need to create a personal access token on GitHub to access the Coqui.ai TTS Docker image. Follow the instructions in the GitHub documentation to create a token: [Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token). Once you have your token, use it to log in to the GitHub Container Registry before building the image:

- **Linux/macOS:**
  ```shell
  export CR_PAT="your_personal_access_token_here"
  echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
  ```

- **Windows (PowerShell):**
  ```powershell
  $env:CR_PAT = "your_personal_access_token_here"
  echo $env:CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
  ```

Replace `your_personal_access_token_here` with your personal access token and `USERNAME` with your GitHub username.

> **_NOTE:_** When you first start a service with a new model, you may experience longer response times as the model is loaded into memory. Subsequent requests should be faster. However, if the service is not used for a while, the model may be unloaded, resulting in longer response times again when the service is next used.

### Stopping Services

To stop services, you need to use the same profiles that were used to start them. For example:

- **Stop all services with GPU support:**
  ```shell
  docker compose --profile auditory-gpu --profile cognitive-gpu --profile vision-gpu --profile vocal-gpu stop
  ```

- **Stop all services in CPU-only mode:**
  ```shell
  docker compose --profile auditory-cpu --profile cognitive-cpu --profile vision-cpu --profile vocal-cpu stop
  ```

### Service Notes

- The services are optional and can be started individually or in combination based on your requirements.
- You can choose between CPU and GPU profiles for the `vision-api` and `cognitive-api` services depending on your hardware and performance needs.
- The `auditory-api` service does not have separate CPU and GPU profiles.

### Starting Simulation

Run the Unity simulation to interact with the virtual environment and AIden.

#### Controls

- **Open/Close Menu:** Press the "`" (backtick) key to open and close the prompt panel for interacting with AIden.
- **Movement:** Use the WASD keys or arrow keys to move in the simulation.
- **Jump:** Press the spacebar to jump.
- **Interact:** Press the "E" key or left-click with the mouse to interact with certain objects in the environment.
- **Look Around:** Use the mouse to control the camera and look around in the simulation.
