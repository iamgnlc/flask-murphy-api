# Murphy's Laws Random Quote API

![example workflow](https://github.com/iamgnlc/flask-murphy-api/actions/workflows/ci-cd.yml/badge.svg)

## Getting Started

```sh
python3 -m venv .venv

. .venv/bin/activate
```

## Install dependencies

```sh
pip install -r requirements.txt
```

Or

```sh
yarn setup
```

## Run app in dev

```sh
flask --app app/main.py --debug run
```

Or

```sh
yarn dev
```

## Run app in prod

```sh
python server.py
```

Or

```sh
yarn start
```

**NOTE:** It uses `waitress` server.

## Tests

```sh
pytest
```

---

![author](https://img.shields.io/badge/author-iamgnlc-blueviolet)
