# Contributing to AIden

Thank you for your interest in contributing to AIden! Your contributions help
us improve this advanced virtual AI entity. Below are guidelines to help you
get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Features](#suggesting-features)
  - [Improving Documentation](#improving-documentation)
  - [Submitting Code Changes](#submitting-code-changes)
- [Development Setup](#development-setup)
- [Style Guide](#style-guide)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

Please read and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure
a welcoming and inclusive environment for everyone involved in the project.

## How Can I Contribute?

### Reporting Bugs

If you encounter any issues or unexpected behavior, please report them via
the [GitHub Issues](https://github.com/chrisjz/aiden/issues) page. When
reporting a bug, please include:

- A clear and descriptive title.
- Steps to reproduce the issue.
- Expected and actual behavior.
- Screenshots, logs, or any other relevant information.

### Suggesting Features

We welcome feature requests! If you have an idea for improving AIden, please
open a [GitHub Issue](https://github.com/chrisjz/aiden/issues) and label it
as a "Feature Request". Be sure to include:

- A detailed description of the feature.
- The problem it solves or the enhancement it provides.
- Any potential implementation ideas.

### Improving Documentation

We value clear, concise, and up-to-date documentation. If you notice areas
that need improvement or want to contribute to the documentation, feel free to:

- Suggest changes via a
[GitHub Issue](https://github.com/chrisjz/aiden/issues).
- Submit a pull request with your proposed changes.

### Submitting Code Changes

We welcome code contributions! Please follow these steps to submit your code:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Write clear and descriptive commit messages.
4. Follow the project's coding style and guidelines.
5. Submit a pull request, linking it to relevant issues or feature requests.

## Development Setup

To set up your development environment:

**Clone the Repository**:

```bash
git clone https://github.com/chrisjz/aiden/aiden.git
cd aiden
```

**Install Dependencies**:

Use Poetry for Python dependencies:

```bash
poetry install
```

Install Unity and the required packages to work on the Unity project.

**Run Tests**:

Run all tests to ensure your environment is properly set up:

```bash
poetry run pytest
```

In Unity, run the tests using the Unity Test Runner.

## Style Guide

Please adhere to the following guidelines:

- **Python**:
  - Follow PEP 8 for Python code style.
  - Use type hints where appropriate.
  - Run linting checks using `poetry run pre-commit run --all-files`.

- **C#**:
  - Follow standard C# coding conventions (e.g., naming conventions,
  code formatting).
  - Use `var` when the type is evident from the right-hand side.
  - Keep methods short and focused; consider breaking down complex methods.

## Commit Messages

Write clear and concise commit messages. Follow these guidelines:

- Use the imperative mood in the subject line (e.g., "Add new feature"
instead of "Added new feature").
- Limit the subject line to 50 characters.
- Provide additional context in the body if necessary.

## Pull Request Process

1. **Fork and Branch**: Always work in a branch derived from
`main` or `develop`.
2. **Test Your Changes**: Ensure all tests pass and your code is
well-covered by unit tests.
3. **Submit a Pull Request**: Include a clear description of the
changes and link it to relevant issues.
4. **Review Process**: Be responsive to feedback during the review process.
The maintainers will review your PR, request changes if necessary, and merge
it once approved.

## Thank You

Thank you for considering contributing to AIden. We appreciate your support in
helping us advance the field of artificial intelligence and cognitive science.
Together, we can build something amazing!
