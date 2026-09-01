FROM python:3.10-slim

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install wheel numpy panda matplotlib jupyter ipywidgets bokeh ipywidgets-bokeh panel ipympl pandas patchelf psycopg[binary]
RUN python3 -m pip install --upgrade OpenVisus

ENV APP_HOME=/app
WORKDIR ${APP_HOME}

COPY catalog.py ./
COPY umn_catalog.png ./
COPY postgres_catalog/migrations ./postgres_catalog/migrations

ENV BOKEH_RESOURCES=cdn
ENV PYTHONUNBUFFERED=True

# For development run with --autoreload
CMD ["python3", "-m", "panel", "serve", "catalog.py"]