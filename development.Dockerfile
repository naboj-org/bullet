FROM python:3.9-alpine

WORKDIR /usr/src/bullet

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk add --no-cache --virtual build-deps curl gcc g++ libc-dev libffi-dev make postgresql-dev postgresql-client openssl-dev bash

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/bullet/requirements.txt
RUN pip install -r requirements.txt

COPY /bullet /usr/src/bullet/

ENTRYPOINT ["/usr/src/bullet/entrypoint.sh"]
