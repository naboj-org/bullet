#!/bin/env python3
import platform
import subprocess
import shlex
import shutil
import sys
import os
import logging


PREFIX = "\033[0;30m\033[47m"
RESET = "\033[0m"
CWD = os.getcwd()

PYTHON = "python" if platform.system() == "Windows" else "python3"

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
    logging.info("(Re)creating virtualenv")
    shutil.rmtree("venv") if os.path.exists("venv") else None
    run(f"{PYTHON} -m venv venv")
    logging.info("Installing dependencies")
    run("venv/bin/pip install -U pip")
    run("venv/bin/pip install -r requirements.txt")

    logging.info("Installing NPM dependencies")
    run("npm install")

    logging.info("Building development CSS")
    run("npm run css-dev")

    logging.info("Rebuilding containers")
    run("docker-compose build")
    reset()


def cmd(*args):
    if len(args) == 0:
        logging.error("Please specify command to run.")
        raise SystemExit(1)
    run(f"docker-compose run --rm bullet-web python manage.py {' '.join(args)}")


handlers = {
    "start": (start, "Start Bullet system"),
    "reset": (reset, "Reset everything"),
    "update": (update, "Rebuild images and reset"),
    "cmd": (cmd, "Run command in container"),
}

if len(sys.argv) == 1:
    print("Usage: ./bullet.py [command]")
    print("Available commands:")
    for name, handler in handlers.items():
        print(f" * {name} : {handler[1]}")
    raise SystemExit(1)

command = sys.argv[1].strip().lower()
if command in handlers:
    handlers[command][0](*sys.argv[2:])
else:
    logging.error(f"Unknown command {command}.")
