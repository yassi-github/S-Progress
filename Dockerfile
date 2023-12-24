FROM debian:bookworm

RUN apt update && \
    apt install -y wget && \
    rm -rf /var/lib/apt/lists/*

# Install Docker from Docker Inc. repositories.
RUN curl -sSL https://get.docker.com/ | sh

# install gvisor
RUN ( set -e; ARCH=$(uname -m); URL=https://storage.googleapis.com/gvisor/releases/release/latest/${ARCH}; wget ${URL}/runsc ${URL}/runsc.sha512 ${URL}/containerd-shim-runsc-v1 ${URL}/containerd-shim-runsc-v1.sha512; sha512sum -c runsc.sha512 -c containerd-shim-runsc-v1.sha512; rm -f *.sha512; chmod a+rx runsc containerd-shim-runsc-v1; mv runsc containerd-shim-runsc-v1 /usr/local/bin; ) \
    && /usr/local/bin/runsc install

WORKDIR /spro
COPY --from=s-progress-builder /s-progress /usr/local/bin/s-progress
COPY . .

CMD ["/usr/local/bin/s-progress"]
