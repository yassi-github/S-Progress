FROM alpine:latest

RUN apk add bash jq

SHELL [ "/bin/bash", "-c" ]
ENV PROBLEMFILES=/problem_files

RUN addgroup -g 61000 user \
    && adduser -G user -s /bin/bash -u 61000 -D user

COPY problem_files/ ${PROBLEMFILES}/
# +x 権限つけないとcdもlsもpermission deniedになる
# directoryには+x権限が必要。ファイルはreadでおｋ
RUN chmod -R 445 ${PROBLEMFILES}/
USER user
WORKDIR ${PROBLEMFILES}
