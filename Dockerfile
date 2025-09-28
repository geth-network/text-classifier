FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim AS base

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UVICORN_HOST="0.0.0.0" \
    UVICORN_PORT="8000" \
    UVICORN_WORKERS=1

RUN apt update && apt install tini -y && \
    apt clean && \
    apt autoremove -y && \
    rm -rf /root/.cache && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /etc/apt/sources.list*

FROM base AS build
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project
COPY src/ src/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked

FROM build AS runtime
EXPOSE 8000
ENTRYPOINT ["tini", "-g", "--"]
CMD ["uv", "run", "uvicorn", "--factory", "text_classifier.main:create_app", "--no-access-log", "--log-level", "error"]
