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


def update(*args):
    if not os.path.exists(".env"):
        shutil.copyfile(".env.example", ".env")

    logging.info("Installing dependencies")
    run(f"{PYTHON} -m pipenv install")

    logging.info("Installing NPM dependencies")
    run("npm install", shell=platform.system() == "Windows")

    logging.info("Building development CSS")
    run("npm run css-dev", shell=platform.system() == "Windows")

    logging.info("Rebuilding containers")
    run("docker-compose build")
    reset()
    create_superuser()


def cmd(*args):
    if len(args) == 0:
        logging.error("Please specify command to run.")
        raise SystemExit(1)
    run(f"docker-compose run --rm web python manage.py {' '.join(args)}")


def create_superuser(*args):
    run("docker-compose run --rm web python manage.py migrate")
    run(
        "docker-compose run -e DJANGO_SUPERUSER_PASSWORD=admin --rm web python manage.py createsuperuser "
        "--username=admin --email=admin@localhost --no-input"
    )


handlers = {
    "start": (start, "Start Bullet system"),
    "reset": (reset, "Reset everything"),
    "update": (update, "Rebuild images and reset"),
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
