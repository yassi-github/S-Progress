FROM ubuntu:20.04
# ENV DEBIAN_FRONTEND=noninteractive
# ENV HOME /root
# ENV PYTHONPATH /fastapi
# ENV PYTHON_VERSION 3.8.5
# ENV PYTHON_ROOT $HOME/local/python-$PYTHON_VERSION
# ENV PATH $PYTHON_ROOT/bin:$PATH

RUN apt update && apt install -y \
    curl \
    python3-pip python3-dev python3-passlib python3-jwt \
    libssl-dev libffi-dev zlib1g-dev libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# RUN echo "ja_JP UTF-8" > /etc/locale.gen \
#     && locale-gen

WORKDIR /fastapi
# ADD . /fastapi_spro/
COPY requirements.txt /fastapi/requirements.txt
RUN pip3 install -r requirements.txt
