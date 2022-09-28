FROM node:18.9.1-alpine AS cssbuild

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run css-prod
CMD ["npm", "run", "css-dev"]

FROM python:3.10-slim-bullseye
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y install libmaxminddb0 gettext \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --dev --deploy

COPY ./bullet .
COPY --from=cssbuild /app/bullet/web/static/app.css ./web/static/app.css

CMD ["gunicorn", "bullet.wsgi", "--access-logfile", "-", "--log-file", "-", "--workers", "4"]
