FROM node:18.8.0-alpine AS cssbuild

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run css-prod
CMD ["npm", "run", "css-dev"]

FROM python:3.10-slim-bullseye AS basebuild

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y install libmaxminddb0 libgdal28 \
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
