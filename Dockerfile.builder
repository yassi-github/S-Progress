FROM golang:bookworm

RUN apt update && apt install -y \
    libssl-dev libffi-dev zlib1g-dev libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /builder
COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY . .
# to static link: -ldflags "-linkmode 'external' -extldflags '-static'"
RUN go build -v -o / ./...

# do nothing
ENTRYPOINT ["echo"]
