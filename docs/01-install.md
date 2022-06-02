# Installation

## Windows

System requirements:
- [Python 3.10](https://www.python.org/downloads/) or newer (I strongly recommend checking "Add Python to PATH" when installing)
- [Pipenv](https://pypi.org/project/pipenv/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Linux

System requirements:
- Python 3.10 or newer
- [Pipenv](https://pypi.org/project/pipenv/)
- [Docker](https://docs.docker.com/engine/install/)
- [docker-compose](https://docs.docker.com/compose/install/)

## Running

Now, you can update and start the development server:

```shell
./helper.py update
./helper.py start
```

You can now visit bullet on http://localhost:8000 or http://math.localhost:8000.
You can also log in as admin with username `admin` and password `admin`.

You should run the commands above whenever you pull new commits from our repository.

## Running arbitrary `manage.py` commands

If you need to run a `manage.py` command, you can use this "shortcut":

```shell
./helper.py cmd migrate
```

## Pre-commit hooks

We use `pre-commit` to run some code checks (black + isort) before commiting. Install them using:

```shell
pipenv run pre-commit install
```

Now, let's look at your [code editor](02-ide.md).
