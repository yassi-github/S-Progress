FROM fullstorydev/grpcurl:latest AS grpcurl

FROM bats/bats

RUN apk add --no-cache jq iproute2 nmap-ncat curl

COPY --from=grpcurl /bin/grpcurl /usr/local/bin/grpcurl
