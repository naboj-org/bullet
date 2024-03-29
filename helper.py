#!/bin/env python3
import logging
import os
import platform
import shlex
import shutil
import subprocess
import sys

PREFIX = "\033[0;30m\033[47m"
RESET = "\033[0m"
CWD = os.getcwd()

PYTHON = "python" if platform.system() == "Windows" else "python3"
PIP = "./venv/Scripts/pip.exe" if platform.system() == "Windows" else "venv/bin/pip"

logging.basicConfig(
    level=logging.INFO,
    format=f"{PREFIX}[%(levelname)s] %(asctime)s: %(message)s{RESET}",
)


def run(cmd, *args, **kwargs):
    logging.debug(f"Running: {cmd}")
    subprocess.run(
        shlex.split(cmd),
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=True,
        *args,
        **kwargs,
    )


def exec(cmd, *args, **kwargs):
    logging.debug(f"Exec: {cmd}")
    os.execlp(shlex.split(cmd)[0], *shlex.split(cmd))


# Handlers


def start(*args):
    logging.info("Starting containers")
    exec("docker-compose up")


def reset(*args):
    logging.info("Deleting containers and volumes")
    run("docker-compose down -v")


def update_python(*args):
    logging.info("Removing old pipenv")
    try:
        run(f"{PYTHON} -m pipenv --rm")
    except subprocess.CalledProcessError:
        logging.info("No old pipenv")

    update()


def update(*args):
    if not os.path.exists(".env"):
        shutil.copyfile(".env.example", ".env")

    logging.info("Installing dependencies")
    try:
        run(f"{PYTHON} -m pipenv install")
    except subprocess.CalledProcessError:
        logging.info("Try installing one more time")
        run(f"{PYTHON} -m pipenv install")

    logging.info("Rebuilding containers")
    run("docker-compose build")
    reset()
    create_superuser()
    generatedata()


def cmd(*args):
    if len(args) == 0:
        logging.error("Please specify command to run.")
        raise SystemExit(1)
    run(f"docker-compose run --rm web python manage.py {' '.join(args)}")


def create_superuser(*args):
    run("docker-compose run --rm web /app/dev_setup.sh")


def generatedata(*args):
    logging.info("Remove uploads folder")
    os.makedirs("bullet/uploads")
    logging.info("generate new data")
    run("docker-compose run --rm web python manage.py generatedata")


handlers = {
    "start": (start, "Start Bullet system"),
    "reset": (reset, "Reset everything"),
    "update": (update, "Rebuild images and reset"),
    "update_python": (update_python, "Rebuild python virtual environment"),
    "generatedata": (generatedata, "Generate testing data"),
    "cmd": (cmd, "Run command in container"),
}

if len(sys.argv) == 1:
    print("Usage: ./helper.py [command]")
    print("Available commands:")
    for name, handler in handlers.items():
        print(f" * {name} : {handler[1]}")
    raise SystemExit(1)

command = sys.argv[1].strip().lower()
if command in handlers:
    handlers[command][0](*sys.argv[2:])
else:
    logging.error(f"Unknown command {command}.")
