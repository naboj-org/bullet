# Installation

## Windows

System requirements:
- [Python 3.12](https://www.python.org/downloads/) or newer (I strongly recommend checking "Add Python to PATH" when installing)
- [UV](https://docs.astral.sh/uv/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Linux

System requirements:
- Python 3.12 or newer
- [UV](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)

## Installing virtual environment

First, we need to set up the virtual environment, for which we use UV. To create the virtual environment, simply run:

```shell
uv sync --dev
```

## Running

Now, you can start the docker containers with:

```shell
docker compose up
```

You can now visit bullet on http://localhost:8000 or http://math.localhost:8000.
You can also log in as admin with email `admin@naboj.org` and password `admin`.

In case you want to update the containers (e.g. after changing packages), you can use:

```shell
docker compose up --build
```

## Running `manage.py` commands

If you need to run a `manage.py` commands, you can do so with:

```shell
docker compose run --rm web ./manage.py migrate
```

## Pre-commit hooks

We use `pre-commit` to run some code checks (black + isort) before commiting.
If you have `pre-commit` installed system-wide, you can install the git hooks with:

```shell
pre-commit install
```

If you don't have `pre-commit` installed system-wide, you can use the one from UV with:

```shell
uv run pre-commit install
```

Now, let's look at your [code editor](02-ide.md).
