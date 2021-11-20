FROM node:current-alpine AS cssbuild

WORKDIR /app

COPY . .

RUN npm install
RUN npm run css-prod

FROM python:3.9-alpine AS basebuild

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

COPY ./bullet .
COPY --from=cssbuild /app/bullet/web/static/app.css ./web/static/app.css

RUN apk update \
    && apk add --virtual build-deps curl gcc musl-dev \
    && apk add libc-dev libffi-dev make \
    && apk add postgresql-dev openssl-dev bash

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --dev --deploy


# Heroku
FROM basebuild AS herokubuild

CMD gunicorn bullet.wsgi --bind 0.0.0.0:$PORT --log-level DEBUG --access-logfile - --log-file -
