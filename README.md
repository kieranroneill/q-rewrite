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
* [2. Usage](#-2-usage)
  - [2.1. Manual](#21-manual)
    - [2.1.1. Requirements](#211-requirements)
    - [2.1.2. Setup](#212-setup)
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

## 🪄 2. Usage

### 2.1. Manual

#### 2.1.1. Requirements

- [Python v3.13+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

<sup>[Back to top ^][table-of-contents]</sup>

#### 2.1.2. Setup

1. Set up the Python virtual environment and install dependencies:

```shell
uv sync
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

> ⚠️ **NOTE:** The default model used is the model declared in [`.env.dev`](./.env.dev) in the `OLLAMA_MODEL` value.

To use a different model, create an `.env` file (use [`.env.example`](./.env.example) as a reference) and change the `OLLAMA_MODEL` value to the desired model.

> 💡 **TIP:** For a list of available models, see Ollama's [model library](https://ollama.com/library).

<sup>[Back to top ^][table-of-contents]</sup>

## 📑 4. Appendix

### 4.1. Useful commands

| Command                           | Description                                            |
|-----------------------------------|--------------------------------------------------------|
| `uv run ./scripts/start_model.py` | Starts the model locally via Docker.                   |
| `uv run pytest`                   | Run unit tests.                                        |
| `uv sync`                         | Sets up virtual environment and installs dependencies. |

<sup>[Back to top ^][table-of-contents]</sup>

## 📄 5. License

Please refer to the [LICENSE][license] file.

<sup>[Back to top ^][table-of-contents]</sup>

<!-- links -->

[license]: ./LICENSE
[table-of-contents]: #table-of-contents
