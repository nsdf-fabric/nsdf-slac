FROM python:3.10-slim

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install wheel numpy panda matplotlib jupyter ipywidgets bokeh ipywidgets-bokeh panel ipympl pandas clickhouse-driver patchelf psycopg[binary]
RUN python3 -m pip install --upgrade OpenVisus

ENV APP_HOME=/app
WORKDIR ${APP_HOME}

COPY run.py ./
COPY umn_schema.png ./

ENV BOKEH_RESOURCES=cdn
ENV PYTHONUNBUFFERED=True

# For development run with --autoreload
CMD ["python3", "-m", "panel", "serve", "run.py", "--autoreload", "--address", "0.0.0.0" ,"--allow-websocket-origin", "*", "--port", "10002", "--prefix", "catalog/"]
