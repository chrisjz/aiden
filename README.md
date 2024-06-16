# AIden (AI Denizen)

AIden is an advanced virtual AI entity designed to simulate the complex
structure and functionality of the human brain. This project constructs
a hierarchical API that mirrors the organization of different brain regions,
enabling AIden to process and integrate sensory data such as auditory, visual,
olfactory, gustatory, and tactile inputs.

Leveraging most recent machine learning models, AIden incorporates
Ollama-compatible models for advanced language and visual understanding,
OpenAI's Whisper for accurate speech recognition and other swappable models.
This allows AIden to interact with its environment in nuanced and human-like
ways. Key components of the system include virtual representations of the
hippocampus for memory, the neocortex for sensory perception, and the amygdala
for emotional responses, making AIden capable of learning from, perceiving,
and responding to complex stimuli in its environment.

Our aim is to develop AIden into a highly intelligent and intuitive AI that
can function dynamically within virtual environments, learning and adapting
in real-time. This project invites contributors who are passionate about
advancing the frontiers of artificial intelligence and cognitive science to
collaborate in creating an advanced, interactive virtual being.

## Setup

### Prerequisites

To run the simulation locally, you will need the following:

* Python 3.11
* Docker
* Docker Compose

### Environment variables

Make a copy of `.env.template` called `.env` and update any required values.

Explanation of the more ambiguous environment variables:

| Name       | Details                                                                                                                                                                 | Default       |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| AGENT_ID   | Identifier of the default AI agent. Determines which Agent is active, if not overriden elsewhere. Brain-related interactions map to this agent, such as memory storage. | 1<sup>1</sup> |
| AGENT_NAME | Name of the default AI agent.                                                                                                                                           | AIden         |

> <sup>1</sup> The ID "0" is treated as a catch-all in this system,
and shouldn't be used.

## Usage

### Starting Services

You can start specific services of the AIden AI using profiles. Profiles allow
you to choose which services to run and whether to use CPU or GPU resources.

* **Start all default services with GPU support:**

```shell
docker compose --profile auditory-gpu --profile cognitive-gpu --profile vocal-gpu up -d
```

* **Start all default services in CPU-only mode:**

```shell
docker compose --profile auditory-cpu --profile cognitive-cpu --profile vocal-cpu up -d
```

You can also have any combination of CPU and GPU services.

For the Vocal API, you will need to create a personal access token on GitHub
to access the Coqui.ai TTS Docker image. Follow the instructions in the
GitHub documentation to create a token:
[Creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
Once you have your token, use it to log in to the GitHub Container
Registry before building the image:

* **Linux/macOS:**

```shell
export CR_PAT="your_personal_access_token_here"
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
```

* **Windows (PowerShell):**

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

* **Stop all default services with GPU support:**

```shell
docker compose --profile auditory-gpu --profile cognitive-gpu --profile vocal-gpu stop
```

* **Stop all default services in CPU-only mode:**

```shell
docker compose --profile auditory-cpu --profile cognitive-cpu --profile vocal-cpu stop
```

### Service Notes

* The services are optional and can be started individually or in combination
based on your requirements.
* You can choose between CPU and GPU profiles for the `vision-api` and
`cognitive-api` services depending on your hardware and performance needs.
* The `auditory-api` service does not have separate CPU and GPU profiles.

### Starting Simulation

Run the Unity simulation to interact with the virtual environment and AIden.

#### Controls

* **Open/Close Menu:** Press the "`" (backtick) key to open and close the
prompt panel for interacting with AIden.
* **Movement:** Use the WASD keys or arrow keys to move in the simulation.
* **Jump:** Press the spacebar to jump.
* **Interact:** Press the "E" key or left-click with the mouse to interact
with certain objects in the environment.
* **Look Around:** Use the mouse to control the camera and look around in
the simulation.

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
