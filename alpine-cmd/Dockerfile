FROM alpine:latest

RUN apk add bash

SHELL [ "/bin/bash", "-c" ]
# /hostpwd/alpine-cmd/problem_files
#ARG PROBLEMFILESPATH
ENV PROBLEMFILES=/problem_files

# copy problem_files to container
# COPY ${PROBLEMFILESPATH}/* ${PROBLEMFILES}/

# permit write files
#RUN chmod -R 444 ${PROBLEMFILES}/

RUN addgroup -g 61000 user \
    && adduser -G user -s /bin/bash -u 61000 -D user

COPY problem_files/ ${PROBLEMFILES}/
# +x 権限つけないとcdもlsもpermission deniedになる
# directoryには+x権限が必要。ファイルはreadでおｋ
RUN chmod -R 445 ${PROBLEMFILES}/
USER user

# problem fileをパスしたら、exテストファイルを試す
# パスしたというよりエラーが出なかった？ら、problem fileをいじろうとしてない(root権限のファイルをchown,chmod,writeしようとしてない)のでprobが自オーナーファイルを実行してもいじられることはない
# direectory: mode: 500, owner: prob, name: extest
# files: mode: 400, owner: prob, name: exq.txt
# のように用意して、実行ファイルをprob権限で、ファイルパスをexテストのやつに書き換えて行う。

