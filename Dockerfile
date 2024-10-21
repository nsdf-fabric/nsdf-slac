FROM python:3.10-slim

RUN python3 -m pip install pip numpy matplotlib \
    bokeh==3.2.2 panel openvisuspy ipykernel python-dotenv
RUN python3 -m pip install OpenVisusNoGui==2.2.128 
RUN python3 -m pip install boto3==1.35.99

WORKDIR /usr/src/channels_dashboard/
COPY slac.py ./
COPY utils.py ./
COPY uploaded_files.txt ./
COPY idx ./idx

ENV BOKEH_ALLOW_WS_ORIGIN="*"

EXPOSE 10042

CMD ["python3", "-m", "panel", "serve", "slac.py", "--address", "0.0.0.0" ,"--allow-websocket-origin", "*", "--port", "10042"]
