#!/bin/bash
# build.sh

# usage:
#     [CMD_NAME=<cmd-name>] build.sh [SUBCMD]
#
# PREREQUIREMENTS:
# This saves downloaded packages by mounting GOPATH directory.
# To crate mount directory, run:
# ```sh
# docker create --name go-cp golang:latest
# docker cp go-cp:/go ~/go
# docker rm go-cp
# chmod -R 755 ~/go
# ```

SUBCMD="$1"
shift
ARGS="$@"

# go command by docker.
# add GOPRIVATE if u use private repo package.
# e.g. --env GOPRIVATE="github.com/yassi-github/dotsyaml"
go() {
    docker run --rm \
        -v $(realpath "${HOME}")/go:/go \
        -v $(realpath "${HOME}")/.ssh:/root/.ssh \
        -v $(realpath "${HOME}")/.cache:/root/.cache \
        -v $(realpath "${PWD}"):${PWD} \
        -w $(realpath "${PWD}") \
        golang:latest \
        sh -c "go $@ ; echo \$? && chown -R $(id -u) . ; chgrp -R $(id -g) ."
}

exec_go_with_stdoutput() {
    ARGS="$@"

    tmpfile_err="/tmp/${RANDOM}"
    tmpfile_rc="/tmp/${RANDOM}"
    # separate std{out,err} into tmpfile and output stdout(excluding lastline; rc) to terminal with non-blocking.
    go "${ARGS}" 2> >(tee ${tmpfile_err} >&2) | tee >(tail -n1 > ${tmpfile_rc}) | sed '$ d'
    RC=$(cat ${tmpfile_rc})
    STDERR=$(cat ${tmpfile_err})
    rm -f ${tmpfile_rc} ${tmpfile_err}
    if [[ "${STDERR}" != "" ]]; then
        # change string color to Yellow if interactive terminal
        if tty >/dev/null 2>&1; then
            printf "\033[33m"
            endis_import "${STDERR}"
            printf "\033[m"
        else
            endis_import "${STDERR}"
        fi
    fi

    exit ${RC}

}

endis_import() {
    input=$1
    enable_list=$(echo "${input}" | grep "undefined")
    disable_list=$(echo "${input}" | grep "imported and not used" | awk '{print $1}')
    #enable_import "${enable_list}"
    disable_import "${disable_list}"
}

## enable_import
# `subpkg/template.go:14:9: undefined: log`
#enable_import() {
#    list=$1
#    for line in ${list}; do
#        target_file=$(echo "${line}" | awk -F':' '{print $1}')
#        target_linenum=$(echo "${line}" | awk -F':' '{print $2}')
#        target_package=$(echo "${line}" | awk -F':' '{print $5}' | awk $1=$1)
#        target_file_import=$(grep -zoP 'import[\s\S]*?\)' ${target_file})
# [WIP]
#    done
#}

# disable_import "./main.go:4:4: "
disable_import() {
    list=$1
    for line in ${list}; do
        target_file=$(echo "${line}" | awk -F':' '{print $1}')
        target_linenum=$(echo "${line}" | awk -F':' '{print $2}')
        # comment out with "// "
        sed -i "${target_linenum}s%^\([ \t]*\)%\1// %" ${target_file}
        echo "Commented out: ${target_file}:${target_linenum}"
    done
}

deploy() {
    docker build -t s-progress-shell s-progress-shell

    mkdir -p docker_conf/nginx/ssl
    mkdir -p answer/script_files
    cd docker_conf/nginx/ssl
    openssl req -x509 -sha256 -nodes -days 3650 -newkey rsa:2048 -subj /CN=localhost -keyout server.key -out server.crt
    chown `echo $USER` .
    cd ../../..

    docker compose -p s-progress up -d --build
}

# [a,b,c] -> [b,c]
# usage:
# shifted_array=$( shift_array "${array[@]}" )
shift_array() {
    local array=( ${1} )
    if [ ${#array[@]} -lt 1 ]; then
        # no enough length
        echo ${array[@]}
        return 1
    fi

    for i in $( seq 2 ${#array[@]} ); do
        array[$(( ${i} - 2 ))]=${array[$(( ${i} - 1 ))]}
    done
    array[$(( ${#array[@]} - 1 ))]=""
    array=( ${array[@]} )

    echo ${array[@]}
}

run() {
    case ${SUBCMD} in
        "buf" )
            cd ./proto
            buf lint && buf generate
            cd ..
        ;;

        "sqlc" )
            docker run --rm -v $(pwd):/src -w /src -u 1000:1000 sqlc/sqlc ${ARGS}
        ;;

        "deploy" )
            deploy
        ;;

        "clean" )
            rm -f go.sum ./bin/*
        ;;

        # run <keyword> [args ...]
        #   keyword: a piece of binary name to run. if keyword is not unique or not provided, target binary will be top of asc sort.
        # for example, "run c localhost:13333" would run "./bin/client localhost:13333"
        # and "run s" and also "run r" would run "./bin/server" (because both "s" and "r" is uniqly contained in "server" (never appear in "client"))
        "run" )
            _argsarr=( ${ARGS} )
            runcmd="${_argsarr[0]}"
            CMD_NAME="$(echo "$([ -d ./cmd ] && ls ./cmd/ || exec_go_with_stdoutput list -f \'{{if eq .Name \"main\"}}{{.Dir}}{{end}}\' -buildvcs=false ./... | xargs -i{} basename {} )" | grep "${runcmd}" | head -n1)"
            ARGS=$( shift_array "${_argsarr[@]}" )

            echo -e "run \`./bin/${CMD_NAME} ${ARGS}\` ...\n"
            ./bin/${CMD_NAME} ${ARGS}
        ;;

        "fmt" )
            exec_go_with_stdoutput 'fmt ./...'
        ;;

        "exec" )
            exec_go_with_stdoutput ${ARGS}
        ;;

        "test" )
           exec_go_with_stdoutput 'get -u ./... && go mod tidy && go test -v ./...'
        ;;

        "utest" )
            exec_go_with_stdoutput 'get -u ./... && go mod tidy && go test -v $(go list -m)/'${ARGS}
        ;;

        "itest" )
            tty 2>/dev/null 1>&2 && TTY_OPT="-t" || TTY_OPT=""
            docker run --rm ${TTY_OPT} -v $(pwd):/code/ --network s_progress_network itest:latest ${ARGS:-"./itest/"}
        ;;

        "help" )
            echo "usage:
    build.sh [SUBCMD=build]
    SUBCMD:
$(cat ./build.sh | tr '\n'  '\0' | grep -ao "case.*esac" | tr '\0' '\n' | grep -o '^ \+".*" )' | sed 's/\(.*\) )/    \1/g')
"
        ;;

        "build" )
            exec_go_with_stdoutput 'get -u ./... && go mod tidy && go build -v -buildvcs=false -o bin/ ./...'
        ;;

        * )
            ./build.sh build
        ;;
    esac
}

run
