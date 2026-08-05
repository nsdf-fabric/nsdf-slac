ARG PLATFORM=linux/amd64

FROM --platform=$PLATFORM python:3.10-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/nexus-dashboard/

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

FROM --platform=$PLATFORM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/nexus-dashboard/

COPY --from=builder /usr/src/nexus-dashboard/.venv /usr/src/nexus-dashboard/.venv
COPY nexus-dashboard.py uploaded_files.txt ./

ENV PATH="/usr/src/nexus-dashboard/.venv/bin:$PATH"
EXPOSE 8000

ENTRYPOINT [ "panel", "serve", "nexus-dashboard.py" ]
