<h1 align="center">
  <img alt="AIden logo"
  src="Assets/Project/Textures/Logo/logo-border.png" width="160" />
</h1>

[![Demo video of AIden in action](https://img.youtube.com/vi/ZUk2MBOdZ-s/maxresdefault.jpg)](https://www.youtube.com/watch?v=ZUk2MBOdZ-s)

AIden is an advanced virtual AI entity designed to simulate the complex
structure and functionality of the human brain.

- **Core Features**:
  - **Hierarchical API**: Mirrors the organization of different brain
  regions, enabling AIden to process and integrate various sensory data
  types (auditory, visual, olfactory, gustatory, tactile).
  - **Machine Learning Integration**:
    - **Ollama-compatible models** for advanced language and visual
    understanding.
    - **OpenAI's Whisper** for accurate speech recognition.
    - **Swappable models** for flexibility in AI capabilities.
  - **Cognitive Model**: Incorporates virtual representations of key
  brain regions:
    - **Hippocampus** for memory.
    - **Thalamus** for sensory perception.
    - **Prefrontal Cortex** for decision-making.

- **Capabilities**:
  - AIden interacts with its environment in nuanced and human-like ways,
  capable of learning from, perceiving, and responding to complex stimuli.
  - Real-time adaptation and learning within virtual environments.

- **Project Goals**:
  - To develop AIden into a highly intelligent and intuitive AI capable
  of dynamic functioning within virtual environments.

- **Additional Points**:
  - **Virtual Environment Integration**: The project includes a Unity 3D
  simulation where AIden interacts with a virtual environment. There is also
  a 2D simulation using a grid-based system which runs in a terminal.
  - **Advanced Sensory Processing**: AIden uses models like OpenAI's Whisper
  and LLaVA for sensory data processing and integration.
  - **Modular Design**: The project leverages a modular architecture, allowing
  for easy updates and improvements to AIden’s cognitive and sensory processing
  capabilities.

## Setup

### Prerequisites

To run the simulation locally, you will need the following:

- Python 3.11
- Docker
- Docker Compose
- Unity 2022

### Environment variables

Make a copy of `.env.template` called `.env` and update any required values.

## Usage

### Starting Services

You can start specific services of the AIden AI using profiles. Profiles allow
you to choose which services to run and whether to use CPU or GPU resources.

- **Start all default services with GPU support:**

```shell
docker compose --profile auditory-ambient-gpu --profile auditory-language-gpu --profile cognitive-gpu --profile vision-gpu --profile vocal-gpu up -d
```

- **Start all default services in CPU-only mode:**

```shell
docker compose --profile auditory-ambient-cpu --profile auditory-language-cpu --profile cognitive-cpu --profile vision-cpu --profile vocal-cpu up -d
```

> **_RECOMMENDATIONS:_**
>
> - You will want at least the `cognitive` and
`vision` services running for the simulation.
This will enable the AI agent to at least process thoughts
and see their environment.
> - If you're running locally with only one GPU, use the GPU for the
`cognitive` and `vision` services, and your CPU for the `auditory-ambient`.
The `auditory-ambient` service performs well on just a CPU, and overall
the performance will be better particularly when running the Unity simulation.
> - If your machine cannot run more than one model, set `COGNITIVE_MODEL`
to a multi-modal model such as `bakllava`, change `VISION_API_PORT`
to match `COGNITIVE_API_PORT` and spin up only the `cognitive` service.

The services are optional and can be started individually or in combination
based on your requirements.
You can also have any combination of CPU and GPU services.

For the Vocal API, you will need to create a personal access token on GitHub
to access the Coqui.ai TTS Docker image. Follow the instructions in the
GitHub documentation to create a token:
[Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
Once you have your token, use it to log in to the GitHub Container
Registry before building the image:

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

Replace `your_personal_access_token_here` with your personal access token
and `USERNAME` with your GitHub username.

> **_NOTE:_** When you first start a service with a new model, you may
experience longer response times as the model is loaded into memory.
Subsequent requests should be faster. However, if the service is not
used for a while, the model may be unloaded, resulting in longer response
times again when the service is next used.

### Stopping Services

To stop services, you need to use the same profiles that were used to start
them. For example:

- **Stop all default services with GPU support:**

```shell
docker compose --profile auditory-ambient-gpu --profile auditory-language-gpu --profile cognitive-gpu --profile vision-gpu --profile vocal-gpu stop
```

- **Stop all default services in CPU-only mode:**

```shell
docker compose --profile auditory-ambient-cpu --profile auditory-language-cpu --profile cognitive-cpu --profile vision-cpu --profile vocal-cpu stop
```

### Starting Simulation

Run the Unity simulation to interact with the virtual environment and AIden.

Open Unity and navigate to the following scene to start the
simulation: `Assets/Project/Scenes/Home.unity`.

An executable of the simulation will be provided in the future
for different operating systems.

#### Controls

- **Open/Close Main Menu:** Press the ESC key to open and close
the main menu.
- **Movement:** Use the WASD keys or arrow keys to move in the simulation.
- **Jump:** Press the spacebar to jump.
- **Chat with AI Agent:** Press the "T" key to chat with AIden using text input.
You need to be close to AIden to initiate the chat.
- **Interact:** Press the "E" key or left-click with the mouse to interact
with certain objects in the environment.
- **Look Around:** Use the mouse to control the camera and look around in
the simulation.
- **Switch perspective** Press TAB to switch between controlling
the player or observing through AIden.

## Development

### Pre-commit Hooks

Pre-commit hooks are used to automatically check and format code
before committing.

Install pre-commit hooks for this project:

```shell
poetry run pre-commit install
```

If the `dotnet-format` hook doesn't work, you will need to download the
`.NET SDK` version specified in the error output.

Pre-commit hooks will now run automatically on each `git commit`. You can
also manually run the hooks on all files with:

```shell
poetry run pre-commit run --all-files
```

## Contributing

We welcome contributions from the community!
Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on
how to get involved.
