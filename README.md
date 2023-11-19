# Murphy's Laws Random Quote API

![ci-cd](https://github.com/iamgnlc/flask-murphy-api/actions/workflows/ci-cd.yml/badge.svg)

Returns random Murphy's Law quote(s). Store on a Redis cache backend conditionally. Built with Flask.

## Getting Started

### Create virtual env

```sh
python3 -m venv .venv

. .venv/bin/activate
```

### Install dependencies

```sh
make install
```

### Run app in dev

```sh
make dev
```

### Run app in prod

```sh
make start
```

### Tests

```sh
make test
```

### Lint

```sh
make lint
```

**NOTE:** It uses `ruff`.

### Format

```sh
make format
```

**NOTE:** It uses `black`.

---

[![author](https://img.shields.io/badge/author-iamgnlc-blueviolet)](https://github.com/iamgnlc)
