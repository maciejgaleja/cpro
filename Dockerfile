FROM python:latest

WORKDIR /usr/src/cpro
COPY ./requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir -r /opt/requirements.txt

RUN groupadd -g 1000 user
RUN useradd -u 1000 user -g user

CMD /bin/bash
