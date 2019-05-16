FROM python:latest

WORKDIR /usr/src/cpro
COPY ./requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir -r /opt/requirements.txt
CMD /bin/bash
