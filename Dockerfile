FROM node:current-alpine3.11 AS cssbuild

WORKDIR /app

COPY package.json postcss.config.js tailwind.config.js css/app.css ./

RUN npm install
RUN npx tailwindcss -i app.css -o app-built.css

FROM python:3.9-alpine AS basebuild

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN apk update \
    && apk add --virtual build-deps gcc musl-dev \
    && apk add libc-dev libffi-dev make \
    && apk add postgresql-dev openssl-dev bash

COPY ./bullet .

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY --from=cssbuild /app/app-built.css ./static/app.css

# Heroku
FROM basebuild AS herokubuild

CMD gunicorn bullet.wsgi --bind 0.0.0.0:$PORT --log-level DEBUG --access-logfile - --log-file -