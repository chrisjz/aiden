FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
&& rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=${POETRY_VERSION} python3 -
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the project files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-interaction --no-ansi

# Copy relevant project files
COPY ./aiden ./aiden
COPY ./config/brain ./config/brain

# Run the application
CMD ["uvicorn", "aiden.api.brain:app", "--host", "0.0.0.0", "--port", "8000"]
