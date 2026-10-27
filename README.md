# Murphy's Laws Random Quote API

![ci-cd](https://github.com/iamgnlc/flask-murphy-api/actions/workflows/ci-cd.yml/badge.svg)

Returns random Murphy's Law quote(s). Store on a Redis cache backend conditionally. Built with Flask.

All workflow commands are PDM scripts defined in `pyproject.toml` under `[tool.pdm.scripts]` — run them with `pdm run <script>`. PDM runs them inside the project virtualenv automatically, no activation step needed.

## Getting Started

### Create virtual env

```sh
python3 -m venv .venv

. .venv/bin/activate
```

### Install dependencies

```sh
pdm run install
```

**NOTE:** Installs `requirements-dev.txt`, which includes the runtime dependencies from `requirements.txt` plus dev tools (pytest, ruff, coverage).

### Run app in dev

```sh
pdm run dev
```

### Run app in prod

```sh
pdm run start
```

### Tests

```sh
pdm run test
```

### Lint

```sh
pdm run lint
```

**NOTE:** It uses `ruff`.

### Format

```sh
pdm run format
```

**NOTE:** It uses `black`.

## Documentation

- [AGENTS.md](AGENTS.md) — context and working instructions for AI coding agents
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the app is structured and why
- [docs/API.md](docs/API.md) — endpoints, parameters, responses, headers, and errors

---

[![author](https://img.shields.io/badge/author-iamgnlc-blueviolet)](https://github.com/iamgnlc)
