FROM python:3.10-slim
COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/channels_dashboard/

COPY pyproject.toml ./
COPY uv.lock ./
RUN uv sync --locked

COPY slac.py ./
COPY utils.py ./
COPY uploaded_files.txt ./

ENV BOKEH_ALLOW_WS_ORIGIN="*"

EXPOSE 10042

CMD ["uv", "run", "panel", "serve", "slac.py", "--address", "0.0.0.0" ,"--allow-websocket-origin", "*", "--port", "10042", "--prefix", "/darkmatter"]
