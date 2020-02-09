FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y cmake make gcc zlib1g-dev libffi-dev git
RUN apt-get install -y libssl-dev
RUN apt-get install -y net-tools wget

WORKDIR /usr/src
RUN wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz
RUN chmod -R 777 /usr/src

RUN tar xf Python-3.7.4.tgz
WORKDIR /usr/src/Python-3.7.4
RUN ./configure --enable-shared --prefix=/usr
RUN make -j16
RUN make install

WORKDIR /usr/src/
RUN rm -rf ./Python*

WORKDIR /usr/src/cpro
COPY ./requirements.txt /opt/requirements.txt
RUN pip3 install --no-cache-dir -r /opt/requirements.txt

ENTRYPOINT ["/bin/bash", "-c"]
CMD ["bash"]
