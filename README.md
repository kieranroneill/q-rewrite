<div align="center">

[![License: CC0 1.0 Universal](https://img.shields.io/badge/License-CC0%201.0%20Universal-lightgrey.svg)](https://creativecommons.org/publicdomain/zero/1.0/)

</div>

<h1 align="center">
  Q-REWRITE: Quantum Rewriting Engine with Reproducible Invariant Testing and Evaluation
</h1>

<p align="center">
  Uses a small language model (SLM) to produce compiler-like rewrites using verifier-mediated tools to reduce the hardware-aware cost of QAOA circuits.
</p>

---

### Table of contents

* [1. Overview](#-1-overview)
  - [1.1. Abstract](#11-abstract)
  - [1.2. Project structure](#12-project-structure)
* [2. Usage](#-2-usage)
  - [2.1. Requirements](#21-requirements)
  - [2.2. Setup](#22-setup)
  - [2.3. Using Jupyter Notebook](#23-using-jupyter-notebook)
  - [2.4. Using Script](#24-using-script)
* [3. Development](#-3-development)
    - [3.1. Requirements](#31-requirements)
    - [3.2. Starting Model Locally](#32-starting-model-locally)
* [4. Appendix](#-4-appendix)
  - [4.1. Useful commands](#41-useful-commands)
* [5. License](#-5-license)

## 🔭 1. Overview

### 1.1. Abstract

TBC...

<sup>[Back to top ^][table-of-contents]</sup>

### 1.2. Project structure

```text
.
├─ build/
│   ├── package/                            <-- Images, scripts and configurations for the Docker services
│   │   ├── <service>/
│   │   │   └── Dockerfile
│   │   └── ...
│   └── ...
├─ deployments/                             <-- Container orchestration (Docker Compose) configurations
│   └── compose.development.yml
├─ examples/                                <-- QASM circuit examples
│   ├── 01_a_very_unoptimized_circuit.qasm
│   └── ...
├─ src/                                     <-- Source code files
│   ├── q_rewrite/
│   │   ├── clients/                        <-- The model client used to handle the raw requests to the model
│   │   │   └── ...
│   │   ├── constants/
│   │   │   └── ...
│   │   ├── dtos/                           <-- Data transfer objects
│   │   │   └── ...
│   │   ├── enums/
│   │   │   └── ...
│   │   ├── optimizers/                     <-- The optimizers handle the main loop
│   │   │   └── ...
│   │   ├── tools/                          <-- Various internal tools
│   │   │   └── ...
│   │   ├── verifiers/                      <-- The verifiers ensure the proposed circuit is equivalent and determines the cost reduction, if any
│   │   │   └── ...
│   │   └── __init__/py
├─ test/                                    <-- Testing files (uses the same structure as the source code)
│   └── q_rewrite/
│        └── ...
├── .dockerignore                           <-- Instructs Docker to ignore files/directories
├── .editorconfig                           <-- Platform/editor-agnostic configuration file
├── .env.dev                                <-- Configration variables to run the development environment
├── .env.example                            <-- An explanation of the environment variables
├── .gitignore                              <-- Files/directories ignored in git commits
├── .python-version                         <-- The required Python version to run the project
├── LICENSE                                 <-- Project license
├── pyproject.toml                          <-- Python project configuration file
├── pytest.ini                              <-- pytest configuration file
├── README.md
├── uv.lock                                 <-- uv lock file
└── ...
```

<sup>[Back to top ^][table-of-contents]</sup>

## 🪄 2. Usage

### 2.1. Requirements

- [Python v3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

<sup>[Back to top ^][table-of-contents]</sup>

### 2.2. Setup

1. Set up the Python virtual environment and install dependencies:

```shell
uv sync
```

2. Create an `.env` file at the project root (use [`.env.example`](./.env.example) as a reference) and change the values to point to the desired model.

<sup>[Back to top ^][table-of-contents]</sup>

### 2.3. Using Jupyter Notebook

You can run the examples using the Jupyter notebook [file](./examples.ipynb).

This will help load the optimizer and conveniently visualize the before/after quantum circuits (using Qiskit).

<sup>[Back to top ^][table-of-contents]</sup>

### 2.4. Using Script

To run a custom QASM file, you can use the [main.py](./main.py) to pass the path as an argument:

```shell
uv run main.py "/path/to/qasm/file.qasm"
```

<sup>[Back to top ^][table-of-contents]</sup>

## 🛠️ 3. Development

### 3.1. Requirements

- [Docker](https://docs.docker.com/engine/install/)
- [Python v3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

<sup>[Back to top ^][table-of-contents]</sup>

### 3.2. Starting Model Locally

To start the model locally via Docker run:

```shell
uv run ./scripts/start_model.py
```

> ⚠️ **NOTE:** The default model is declared in [`.env.dev`](./.env.dev) in the `MODEL` value.

To use a different model, create an `.env` file (use [`.env.example`](./.env.example) as a reference) and change the `MODEL` value to the desired model.

> 💡 **TIP:** For a list of available models, see Ollama's [model library](https://ollama.com/library).

<sup>[Back to top ^][table-of-contents]</sup>

## 📑 4. Appendix

### 4.1. Useful commands

| Command                                               | Description                                            |
|-------------------------------------------------------|--------------------------------------------------------|
| `uv run ./scripts/start_model.py`                     | Starts the model locally via Docker.                   |
| `uv run main.py "./examples/<example_filename>.qasm"` | Run example QASM circuit.                              |
| `uv run pytest`                                       | Run unit tests.                                        |
| `uv sync`                                             | Sets up virtual environment and installs dependencies. |

<sup>[Back to top ^][table-of-contents]</sup>

## 📄 5. License

Please refer to the [LICENSE][license] file.

<sup>[Back to top ^][table-of-contents]</sup>

<!-- links -->

[license]: ./LICENSE
[table-of-contents]: #table-of-contents
