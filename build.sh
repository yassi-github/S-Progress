#!/bin/bash
# build.sh

# usage:
#     build.sh [SUBCMD]
#
#     SUBCMD:
#         build: build packages outputs to ./bin/
#         clean: remove build files (`bin/*` and `go.sum`)
#         exec [cmd]: execute any commands
#         test [dir]: run go test
#         deploy: deploy by compose

SUBCMD="$1"
shift
ARGS="$@"

CMD_NAME="sprogress"

# go command by docker.
go() {
  docker run -i --rm \
	-v $(realpath "${HOME}")/go:/go \
	-v $(realpath "${HOME}")/.ssh:/root/.ssh \
	-v $(realpath "${PWD}"):${PWD} \
	-w $(realpath "${PWD}") \
	golang:latest \
	sh -c "go $@ ; echo \$? > /tmp/EXITCODE && chown $(id -u) ./* ; chgrp $(id -g) ./* ; cat /tmp/EXITCODE"
}

exec_go_with_stdoutput() {
	ARGS="$@"

	tmpfile="/tmp/${RANDOM}"
	STDOUT=$(go "${ARGS}" 2>${tmpfile})
	STDERR=$(cat ${tmpfile})
	rm -f ${tmpfile}

	# ignore exitcode
	[[ "${STDOUT}" =~ ^[0-9]*$ ]] || echo "${STDOUT}" | sed "$ d"
	# stderr if exists
	[[ "${STDERR}" != "" ]] && echo "${STDERR}" >&2

	# exitcode is the lastline of stdout
	exit $(echo "${STDOUT}" | tail -n 1)
}

deploy() {
    docker build -t alpine-cmd alpine-cmd

    mkdir -p docker_conf/nginx/ssl
    mkdir -p answer/script_files
    cd docker_conf/nginx/ssl
    openssl req -x509 -sha256 -nodes -days 3650 -newkey rsa:2048 -subj /CN=localhost -keyout server.key -out server.crt
    chown `echo $USER` .
    cd ../../..

    docker compose up -d --build
}

case ${SUBCMD} in
	"build" )
		exec_go_with_stdoutput 'get -u ./... && go mod tidy && go build -buildvcs=false -o bin/ ./...'
	;;

    "try" )
        ./build.sh build && ./bin/try ${ARGS}
    ;;

    "run" )
        ./build.sh build && ./bin/${CMD_NAME} ${ARGS}
    ;;

	"clean" )
		rm -rf go.sum bin/* gen
	;;

	"exec" )
		exec_go_with_stdoutput "${ARGS}"
	;;

	"test" )
		exec_go_with_stdoutput 'get -u ./... && go mod tidy && go test -v $(go list -m)/'${ARGS}
	;;

	"testall" )
		exec_go_with_stdoutput 'get -u ./... && go mod tidy && go test -v ./...'
	;;

	"format" )
		exec_go_with_stdoutput 'fmt ./...'
	;;

	"deploy" )
		deploy
	;;

	"buf" )
		buf lint && buf generate
	;;

	"sqlc" )
		docker run --rm -v $(pwd):/src -w /src -u 1000:1000 sqlc/sqlc ${ARGS}
	;;

	"itest" )
		docker run --rm -it -v $(pwd):/code/ --network s_progress_network itest:latest ${ARGS:-"./itest/"}
	;;
esac
