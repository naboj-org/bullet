# Installation

## Windows

System requirements:
- [Python 3.6](https://www.python.org/downloads/) or newer (I strongly recommend checking "Add Python to PATH" when installing)
- [Docker Desktop]https://www.docker.com/products/docker-desktop)

## Linux

System requirements:
- Python 3.6 or newer
- [Docker](https://docs.docker.com/engine/install/)
- docker-compose

## Running

You need to create your `.env` file in `bullet` directory. The easiest way to do that it to copy `.env.example`.

Now, you can update and start the development server:

```shell
./bullet.py update
./bullet.py start
```

You should run the commands above whenever you pull new commits from our repository.

## Running arbitrary `manage.py` commands

If you need to run a `manage.py` command, you can use this "shortcut":

```shell
./bullet.py run migrate
```

Now, let's look at your [code editor](02-ide.md).
