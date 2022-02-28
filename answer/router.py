from re import match
import os
import docker
from hashlib import sha256
from urllib.parse import quote, unquote
from timeout_decorator import timeout, TimeoutError
from problems.models import problems
from time import sleep
from answer.schemas import ProblemAnswer, ProblemAnswerResult
from fastapi import APIRouter, Depends, HTTPException
from databases import Database, backends
from utils.dbutils import get_connection
import json
import subprocess
from subprocess import PIPE

from random import choices
from string import ascii_letters, digits

from typing import Tuple
from .models import answers_table
import sys
sys.path.append('../')


router = APIRouter()

def split_command(COMMAND: str) -> list:
    # cmd = '''cat $(echo '/etc/passwd')| tr ':' '|' | grep $(echo zsh | tr 'z' 'ba') | sort '''
    cmd = COMMAND

    dq_in = False
    sq_in = False
    bq_in = False
    par_in = False

    dq_count = 0
    sq_count = 0
    bq_count = 0
    par_count = 0

    no_eval_str = ""
    no_eval_str_list = []

    for c in list(cmd):
        if c == '"':
            if dq_in == True:
                dq_count -= 1
            else:
                dq_count += 1
        if c == '\'':
            if sq_in == True:
                sq_count -= 1
            else:
                sq_count += 1
        if c == '(':
            par_count += 1
        if c == ')':
            par_count -= 1
        if c == '`':
            if bq_in == True:
                bq_count -= 1
            else:
                bq_count += 1

        if dq_count % 2 == 1:
            dq_in = True
        else:
            dq_in = False

        if sq_count % 2 == 1:
            sq_in = True
        else:
            sq_in = False

        if bq_count % 2 == 1:
            bq_in = True
        else:
            bq_in = False

        if par_count > 0:
            par_in = True
        else:
            par_in = False


        if dq_in == True or sq_in == True:
            no_eval_str += c
        elif dq_in == False and sq_in == False:
            if no_eval_str != "":
                no_eval_str_list.append(no_eval_str)
            no_eval_str = ""


    # print(cmd)
    # cat $(echo '/etc/passwd')| tr ':' '|' | grep $(echo zsh | tr 'z' 'ba') | sort
    # print(no_eval_str_list)
    # ["(echo '/etc/passwd'", "':", "'|", "(echo zsh | tr 'z' 'ba'"]

    cmd_list = []
    for nes in no_eval_str_list:
        cmd_split = cmd.split(nes, 1)
        cmd_list.append(cmd_split[0])
        cmd = cmd_split[1]

    cmd_list.append(cmd)

    # print(cmd_list)
    # ['cat $', ')| tr ', "' ", "' | grep $", ') | sort ']

    for idx, nes in enumerate( no_eval_str_list ):
        cmd_list[idx] += nes[0]
        no_eval_str_list[idx] = nes[1:]


    # print(no_eval_str_list)
    # ["echo '/etc/passwd'", ':', '|', "echo zsh | tr 'z' 'ba'"]
    # print(cmd_list)
    # ['cat $(', ")| tr '", "' '", "' | grep $(", ') | sort ']

    nested_list = [[]]

    for cl in cmd_list:
        if '|' in cl:
            splcl = cl.split('|')
            nested_list[-1].append(splcl[0])
            for splclelm in splcl[1:]:
                nested_list.append([splclelm])
        else:
            nested_list[-1].append(cl)

    # nested_list
    # [['cat $(', ')'], [" tr '", "' '", "' "], [' grep $(', ') '], [' sort ']]

    cmd_list = []
    nesl_idx = 0
    for cmdelm in nested_list:
        newcmd = cmdelm[0]
        if cmdelm.__len__() > 1:
            for idx in range(cmdelm.__len__() - 1):
                newcmd += no_eval_str_list[nesl_idx] + cmdelm[idx + 1]
                nesl_idx += 1
        cmd_list.append(newcmd)

    return cmd_list
    # ["cat $(echo '/etc/passwd')", " tr ':' '|' ", " grep $(echo zsh | tr 'z' 'ba') ", ' sort ']


def generate_json_command(COMMAND: str) -> str:

    command_list = split_command(COMMAND)

    execute_command = ""
    create_jq_command = '''echo '{"stdout":['''
    SH = '''{"__result_idx__":''["'"$(cat __result_file__ | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/", "/g')"'"]''},'''

    NUM_CMD = len(command_list)
    for idx, command in enumerate(command_list):
        uni_command_resultfiledir_include_endofslash = "/tmp/"
        uni_command_resultfilename = f"{uni_command_resultfiledir_include_endofslash}result_{idx}"
        if idx == NUM_CMD - 1:
            # trailing leading spaces.
            # cuz pyyaml loads without holding spaces...
            execute_command += f"{command}" + ' | awk \'{$1=$1}; 1\' ' + f" | tee {uni_command_resultfilename}"
        else:
            execute_command += f"{command} | tee {uni_command_resultfilename}"
        create_jq_command += SH.replace('__result_idx__', str(idx)).replace('__result_file__', uni_command_resultfilename)
        # if idx > (NUM_CMD - 2): break
        execute_command += "|"

    execute_command = f"{execute_command[:-1]}" + " >/dev/null " + " ; "

    create_jq_command = create_jq_command[:-1]
    create_jq_command += ''']}' | jq'''

    # print(create_jq_command)

    return execute_command + create_jq_command + f'; rm {uni_command_resultfiledir_include_endofslash}result_*'


def random_name(n: int) -> str:
    return ''.join(choices(ascii_letters + digits, k=n))


# シェルスクリプトの実行可能ファイルを作成する
# ファイルへの相対パスが返る
def create_script_file(script: str) -> str:
    # ok
    # raise HTTPException(status_code=400, detail=generate_json_command(script))
    gened_json_script: str = generate_json_command(script)
    # raise HTTPException(status_code=407, detail=gened_json_script.replace('\n', '\\n'))

    # スクリプトファイルを格納するディレクトリへの相対パス(main.pyから見た相対パス？)
    workingdir: str = 'answer/script_files'
    # ファイル名はランダム
    filename: str = random_name(10)
    # ファイルへのパス
    script_file_path: str = f'{workingdir}/{filename}'
    # スクリプトを書き込む
    with open(script_file_path, 'w') as file:
        # なんか最後の改行が消えることがよくある。なんで？？？
        # file.write(f"#!/bin/bash\n{gened_json_script}\n\n")
        # file.write(f"#!/bin/bash\n{gened_json_script}")
        # file.writelines(["#!/bin/bash", f"{gened_json_script.encode('unicode_escape').decode('utf-8')}"])
        # {"detail":"ls | tee /tmp/result_0 >/dev/null ; echo '{\"stdout\":[{\"0\":''[\"'\"$(head /tmp/result_0 | sed -e ':a' -e 'N' -e '$!ba' -e \"s/\\\
        # /\\\\\", \\\\\"/g\" | awk '{print substr($0, 1, length($0)-4)}')\"'\"]''}]}' | jq; rm /tmp/result_*"}
        # 改行エスケープできてねえし
        # raw 文字列という方法 not escape newline.
        file.write(f"#!/bin/bash\n{gened_json_script.encode('unicode_escape').decode('utf-8')}")
    # io wait
    # sleep(1)
    os.chmod(script_file_path, 0o777)
    return script_file_path


# yes command benchmark
# timeout 10s -> 23s
# timeout 5s -> 22s
# timeout 2s -> 10s
# timeout 1s -> 5s
@timeout(5)
def docker_run_container(client: docker.models.containers.Container, host_projectdir: str, command_file_path: str, name: str) -> bytes:
    # ホストのカレントディレクトリ(マウント元)
    host_projectdir: str = os.getenv('HOSTPWD')
    # io が遅いせいで実行ファイルが認識されていない？1秒待ってみる。-> Internal server error.
    # sleep(1)
    # コンテナの作成
    try:
    # subprocess.run(f'docker run --net="none" --pids-limit=500 -d --name="routerpytest1" -v {host_projectdir}/answer/script_files/:/script_files/ alpine-cmd {command_file_path}', shell=True)
        # container = client.containers.run(image="alpine-cmd", command=f"{command_file_path} ; rm {command_file_path}", detach=True, name=name, volumes={f'{host_projectdir}/answer/script_files/': {'bind': '/script_files/', 'mode': 'rw'}})
        container = client.containers.run(image="alpine-cmd", command=f"{command_file_path} ; rm {command_file_path}", detach=True, network_disabled=True, mem_limit='128m', pids_limit=500,
                                          cpu_period=50000, cpu_quota=25000, ulimits=[docker.types.Ulimit(name='fsize', soft=1000000, hard=10000000)],
                                          runtime="runsc", name=name, volumes={f'{host_projectdir}/answer/script_files/': {'bind': '/script_files/', 'mode': 'rw'}})
        # container_obj = container.get(name)
        # sleep(2)
        # raise HTTPException(status_code=401, detail=container.status)
    except docker.errors.ContainerError as exc:
        # 実行エラー。ファイルの実行ができない場合。なかなか起きないはず。
        container = exc.container
        raise HTTPException(status_code=444, detail=container.logs().decode())
    # コマンド実行失敗時、エラーが取れない。別の場所でエラーが発生している？
    # except:
    #     import sys
    #     raise HTTPException(status_code=444, detail=sys.exc_info())
    # raise HTTPException(status_code=444, detail=sys.exc_info())
    
    # container state が Exited になるまで待つ
    # client.containers.get(name).status なら、リアルタイムのstatusを取得できる
    # container.status は、run時のstatusを保持している

    # sleep(2)
    while client.containers.get(name).status == 'running':
        sleep(0.1)

    # error含めてlogs()で拾う
    exec_script_result: bytes = container.logs()
    # exec_script_result: str = subprocess.run(f'docker logs {name}', shell=True, stdout=PIPE, stderr=PIPE, text=True)
    
    # cat
    # ok
    # raise HTTPException(status_code=444, detail=exec_script_result.decode())
    
    # 拾ったら削除する
    container.remove(force=True)
    return exec_script_result


# コンテナを作成してファイルを実行し、結果を返す
def execute_container(script_file_path: str) -> str:

    client = docker.from_env()

    # ホストのカレントディレクトリ(マウント元)
    host_projectdir: str = os.getenv('HOSTPWD')
    # バインドしたファイルを実行するコマンド
    script_file_name: str = script_file_path.split('/')[-1]
    # ファイルを実行
    EXECUTE_COMMAND: str = f'/script_files/{script_file_name}'
    # EXECUTE_COMMAND: str = f'./../script_files/{script_file_name}'
    container_name = random_name(10)


    try:
        exec_script_result: bytes = docker_run_container(
            client, host_projectdir, EXECUTE_COMMAND, container_name)
    except TimeoutError:
        timeouted_container = client.containers.get(container_name)
        # TIMEOUTした時点でのlogsを取得する
        exec_script_result: bytes = timeouted_container.logs()
        # print(exec_script_result)
        timeouted_container.remove(force=True)

    # ok
    # raise HTTPException(status_code=444, detail=exec_script_result.decode())

    # resultが多すぎる(8191 bytes)を超えるとエラーになるし、処理が重くなるため
    # 8191 bytes の超過分を切り出す
    BYTE_LIMIT = 8191
    # へんなとこで切り出すとエラーとなるのでエラーが出なくなるところを探す
    while True:
        try:
            exec_script_result[:BYTE_LIMIT].decode()
            # 成功したらbreak
            break
        except UnicodeDecodeError:
            BYTE_LIMIT -= 1

    exec_script_result = exec_script_result[:BYTE_LIMIT]

    # 結果の文字列を整える。スクリプトがエラーとなった場合(ファイル名云々が表示された場合)それを消す。
    exec_script_result_list = exec_script_result.decode().split('\n')
    for idx, line in enumerate(exec_script_result_list):
        if match(r'/script_files/[a-zA-Z0-9]+: line \d+: ', line):
            # 最初のファイル名表示を消す
            exec_script_result_list[idx] = ': '.join((line.split(': ')[2:]))

    exec_script_result_str: str = '\n'.join(exec_script_result_list)

    # ok
    # raise HTTPException(status_code=444, detail=exec_script_result_str)

    # url parsent encode
    # urip_script_result: str = quote(exec_script_result_str)
    # return urip_script_result
    return exec_script_result_str


# ファイル作成と実行とファイル削除 実行結果が返る
def run_script(script: str) -> str:
    script_file_path: str = create_script_file(script)
    urip_script_result: str = execute_container(script_file_path)
    os.remove(script_file_path)
    # ok
    # raise HTTPException(status_code=444, detail=urip_script_result)

    return urip_script_result


# 問題テーブルから正答を持ってくる
async def find_correct_answer(problem_id: int, database: Database) -> str:
    query = problems.select().where(problems.columns.id == problem_id)
    # database coroutine object
    # ↓
    # databases.backends.postgres.Record object
    return await database.fetch_one(query)


# answerを検証
async def assert_answer(script: str, problem_id: int, database: Database) -> Tuple[bool, str]:
    # 実行
    urip_script_result: str = run_script(script)
    # 最後の出力結果のみを抽出
    json_loaded = json.loads(urip_script_result)
    LEN_JSON_CMD = len(json_loaded['stdout'])
    latest_stdout: str = '\n'.join(json_loaded['stdout'][LEN_JSON_CMD - 1][f"{LEN_JSON_CMD - 1}"])
    # 正答を抽出

    # ok
    # raise HTTPException(status_code=444, detail=latest_stdout)
    
    correct_answer_record: backends.postgres.Record = await find_correct_answer(problem_id, database)
    # databases.backends.postgres.Record は items()をdictにすることで辞書形式に展開できる
    # 正答はsha256で保存している
    sha256_correct_answer: str = dict(
        correct_answer_record.items())['correct_ans']
    # 同じか検証(isにしたらidを比較するので失敗する！)
    is_correct: bool = sha256(
        # unquote(urip_script_result).encode()).hexdigest() == sha256_correct_answer
        f'{latest_stdout}\n'.encode()).hexdigest() == sha256_correct_answer
    return (is_correct, urip_script_result)


# scriptを受付
@router.post("/problems/{problem_id}/answer", response_model=ProblemAnswerResult)
async def answer_regist(problem_id: int, answer: ProblemAnswer, database: Database = Depends(get_connection)):
    # insert into answers_table という命令。valuesはdatabase.executeの引数で指定
    query = answers_table.insert()
    values = answer.dict()

    # scriptが空 もしくは 8191バイト以上だとエラー
    if not values['script'] or len(values['script'].encode()) > 8191:
        raise HTTPException(status_code=400, detail="Illegal size script.")

    # 正誤判定
    is_correct, urlq_command_result = await assert_answer(unquote(values["script"]), problem_id, database)

    # byte_command_result: bytes = unquote(urlq_command_result).encode()

    # 問題idと正誤の項目を追加
    values['problem_id'] = problem_id
    values['is_correct'] = is_correct

    # urlエンコードして返却
    values['result'] = quote(urlq_command_result)
    ret = await database.execute(query, values)
    # 結果を返す
    return values
