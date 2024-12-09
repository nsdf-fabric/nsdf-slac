FROM python:3.10-slim

RUN python3 -m pip install pip numpy matplotlib \
   bokeh==3.2.2 panel

WORKDIR /usr/src/channels_dashboard/

COPY *.npz *.py ./
COPY mid ./mid

ENV BOKEH_ALLOW_WS_ORIGIN="*"

EXPOSE 10325

CMD ["python3", "-m", "panel", "serve", "slacd.py", "--address", "0.0.0.0", "--allow-websocket-origin", "*", "--port", "10325"]

