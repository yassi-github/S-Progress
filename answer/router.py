from time import sleep
from answer.schemas import ProblemAnswer, ProblemAnswerResult
from fastapi import APIRouter, Depends
from databases import Database, backends
from utils.dbutils import get_connection

from random import choices
from string import ascii_letters, digits

from typing import Container, Tuple
from .models import answers_table
import sys
sys.path.append('../')
from problems.models import problems

from timeout_decorator import timeout, TimeoutError
import subprocess

import docker
import os
import base64
from re import match

router = APIRouter()


def random_name(n: int) -> str:
   return ''.join(choices(ascii_letters + digits, k=n))


# シェルスクリプトの実行可能ファイルを作成する  
# ファイルへの相対パスが返る
def create_script_file(script: str) -> str:
    # スクリプトファイルを格納するディレクトリへの相対パス(main.pyから見た相対パス？)
    workingdir: str = 'answer/script_files'
    # ファイル名はランダム
    filename: str = random_name(10)
    # ファイルへのパス
    script_file_path: str = f'{workingdir}/{filename}'
    # スクリプトを書き込む
    with open(script_file_path, 'w') as file:
        file.writelines('\n'.join(["#!/bin/bash", script]))
    os.chmod(script_file_path, 0o777)
    return script_file_path

# timeout 10s
@timeout(10)
def docker_run_container(client: docker.models.containers.Container, host_projectdir: str, command: str, name: str) -> bytes:
    # ホストのカレントディレクトリ(マウント元)
    host_projectdir: str = os.getenv('HOSTPWD')
    # コンテナの作成
    try:
        container = client.containers.run(image="alpine-cmd", command=command, detach=True, network_disabled=True, mem_limit='128m', pids_limit=100, runtime="runsc", name=name, volumes={f'{host_projectdir}/answer/script_files/': {'bind': '/script_files/', 'mode': 'rw'}})
    except docker.errors.ContainerError as exc:
        # 実行エラー。ファイルの実行ができない場合。なかなか起きないはず。
        container = exc.container

    # container state が Exited になるまで待つ
    # client.containers.get(name).status なら、リアルタイムのstatusを取得できる
    # container.status は、run時のstatusを保持している
    while client.containers.get(name).status == 'running':
        sleep(0.1)

    # error含めてlogs()で拾う
    exec_script_result: bytes = container.logs()
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
    EXECUTE_COMMAND: str = f'./../script_files/{script_file_name}'
    container_name = random_name(10)
    
    try:
        exec_script_result: bytes = docker_run_container(client, host_projectdir, EXECUTE_COMMAND, container_name)
    except TimeoutError:
        exec_script_result: bytes = b'TIME OUT!!'
        client.containers.get(container_name).remove(force=True)
    

    # 結果の文字列を整える。スクリプトがエラーとなった場合(ファイル名云々が表示された場合)それを消す。
    exec_script_result_list = exec_script_result.decode().split('\n')
    for idx, line in enumerate(exec_script_result_list):
        if match(r'/script_files/[a-zA-Z0-9]+: line \d+: ', line):
            # 最初のファイル名表示を消す
            exec_script_result_list[idx] = ': '.join((line.split(': ')[2:]))

    exec_script_result_str: str = '\n'.join(exec_script_result_list)
    
    # base64 string にエンコード
    b64_script_result: str = base64.b64encode(exec_script_result_str.encode()).decode()
    return b64_script_result


# ファイル作成と実行とファイル削除 実行結果が返る
def run_script(script: str) -> str:
    script_file_path: str = create_script_file(script)
    b64_script_result: str = execute_container(script_file_path)
    os.remove(script_file_path)
    return b64_script_result


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
    b64_script_result: str = run_script(script)
    # 正答を抽出
    correct_answer_record: backends.postgres.Record  = await find_correct_answer(problem_id, database)
    # databases.backends.postgres.Record は items()をdictにすることで辞書形式に展開できる
    b64_correct_answer: str = dict(correct_answer_record.items())['correct_ans']
    # 同じか検証(isにしたらidを比較するので失敗する！)
    is_correct: bool = b64_script_result == b64_correct_answer
    return (is_correct, b64_script_result)


# scriptを受付
@router.post("/problems/{problem_id}/answer", response_model=ProblemAnswerResult)
async def answer_regist(problem_id: int, answer: ProblemAnswer, database: Database = Depends(get_connection)):
    # insert into answers_table という命令。valuesはdatabase.executeの引数で指定
    query = answers_table.insert()
    values = answer.dict()
    # 正誤判定
    is_correct, b64_command_result = await assert_answer(base64.b64decode(values["script"].encode()).decode(), problem_id, database)
    # 問題idと正誤の項目を追加
    values['problem_id'] = problem_id
    values['is_correct'] = is_correct
    values['result'] = b64_command_result
    # SQL実行
    ret = await database.execute(query, values)
    return values
