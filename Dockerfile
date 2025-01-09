FROM python:3.10-slim

RUN python3 -m pip install pip numpy matplotlib \
    bokeh==3.2.2 panel openvisuspy ipykernel
RUN python3 -m pip install OpenVisusNoGui==2.2.128 

WORKDIR /usr/src/channels_dashboard/
COPY slac.py ./
COPY raw ./raw
COPY idx ./idx
COPY metadata ./metadata

ENV BOKEH_ALLOW_WS_ORIGIN="*"

EXPOSE 10325

CMD ["python3", "-m", "panel", "serve", "slac.py", "--address", "0.0.0.0" ,"--allow-websocket-origin", "*", "--port", "10325"]

