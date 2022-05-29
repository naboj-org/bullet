FROM node:current-alpine AS cssbuild

WORKDIR /app

COPY . .

RUN npm install
RUN npm run css-prod

FROM python:3.10-slim-bullseye AS basebuild

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --dev --deploy

COPY ./bullet .
COPY --from=cssbuild /app/bullet/web/static/app.css ./web/static/app.css

# Heroku
FROM basebuild AS herokubuild

CMD gunicorn bullet.wsgi --bind 0.0.0.0:$PORT --log-level DEBUG --access-logfile - --log-file -
