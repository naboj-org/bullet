FROM node:24-alpine AS cssbuild

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && \
    pnpm install

COPY bullet ./bullet
COPY css ./css
RUN pnpm run build
CMD ["pnpm", "run", "watch"]

FROM ghcr.io/trojsten/django-docker:v6

USER root
RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt install -y libmaxminddb0 gettext librsvg2-bin build-essential \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*
USER appuser

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY --chown=appuser:appuser ./bullet .
COPY --chown=appuser:appuser ./CHANGELOG.md .
COPY --chown=appuser:appuser --from=cssbuild /app/bullet/web/static/app.css ./web/static/

RUN SECRET_KEY=none python manage.py collectstatic --no-input

ENV BASE_START=/app/start.sh
