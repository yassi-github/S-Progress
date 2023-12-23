FROM ubuntu:20.04

RUN apt update && apt install -y \
    curl wget \
    python3-pip python3-dev python3-passlib python3-jwt \
    libssl-dev libffi-dev zlib1g-dev libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install Docker from Docker Inc. repositories.
RUN curl -sSL https://get.docker.com/ | sh

# install gvisor
RUN ( set -e; ARCH=$(uname -m); URL=https://storage.googleapis.com/gvisor/releases/release/latest/${ARCH}; wget ${URL}/runsc ${URL}/runsc.sha512 ${URL}/containerd-shim-runsc-v1 ${URL}/containerd-shim-runsc-v1.sha512; sha512sum -c runsc.sha512 -c containerd-shim-runsc-v1.sha512; rm -f *.sha512; chmod a+rx runsc containerd-shim-runsc-v1; mv runsc containerd-shim-runsc-v1 /usr/local/bin; ) \
    && /usr/local/bin/runsc install

WORKDIR /fastapi
# COPY requirements.txt ./requirements.txt
# RUN pip install -r requirements.txt

COPY docker_conf/app/entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
