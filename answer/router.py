from answer.schemas import ProblemAnswer, ProblemAnswerResult
from fastapi import APIRouter, Depends
from databases import Database
from utils.dbutils import get_connection

from random import choices
from string import ascii_letters, digits

from .models import answers_table

import docker
import os

router = APIRouter()


def random_name(n: int) -> str:
   return ''.join(choices(ascii_letters + digits, k=n))


# シェルスクリプトの実行可能ファイルを作成する
# ファイルへの相対パスが返る
def create_script_file(script: str) -> str:
    # スクリプトファイルを格納するディレクトリへの相対パス
    workingdir: str = 'answer/script_files'
    # ファイル名はランダム
    filename: str = random_name(10)
    # ファイルへのパス
    script_file_path: str = f'{workingdir}/{filename}'
    # スクリプトを書き込む
    with open(script_file_path, 'w') as file:
        file.write(script)
    return script_file_path


# コンテナを作成してファイルを実行し、結果を返す
def execute_container(script_file_path: str) -> str:

    client = docker.from_env()

    # script_file_path = "test.sh"
    # host_projectdir = "/home/vagrant/S-Progress"
    
    # ホストのカレントディレクトリ(マウント元)
    host_projectdir = os.getenv('HOSTPWD')
    # command = f'dmesg'
    # バインドしたファイルを実行するコマンド
    script_file_name = script_file_path.split('/')[-1]
    # EXECUTE_COMMAND = f'ls -la script_files'
    EXECUTE_COMMAND = f'source script_files/{script_file_name}'
    # 実行結果(バイナリ型で返る)
    command_result = client.containers.run(image="alpine-cmd", command=f'"{EXECUTE_COMMAND}"', network_disabled=True, mem_limit='128m', pids_limit=100, runtime="runsc", remove=True, volumes={f'{host_projectdir}/answer/script_files/': {'bind': '/script_files/', 'mode': 'rw'}})
    # stringにデコード
    script_result: str = command_result.decode()
    return script_result


# ファイル作成と実行とファイル削除 実行結果が返る
def run_script(script: str) -> str:
    script_file_path = create_script_file(script)
    script_result: str = execute_container(script_file_path)
    os.remove(script_file_path)
    return script_result


# 問題テーブルから正答を持ってくる
def find_correct_answer(problem_id: int) -> str:
    # test: fake answer
    # 実行結果は最後に改行されるので、最後は改行する
    correct_answer: str = '321cba\n'
    return correct_answer


# answerを検証
# ArgType: Table ? UserCreate ? Union? dict?
# RetType: same above
def assert_answer(script: str, problem_id: int) -> bool:
    # 実行
    script_result: str = run_script(script)
    # 正答を抽出
    correct_answer: str = find_correct_answer(problem_id)
    # 同じか検証(isにしたらidを比較するので失敗する！)
    is_correct: bool = script_result == correct_answer
    return is_correct


# scriptを受付
@router.post("/problems/{problem_id}/answer", response_model=ProblemAnswerResult)
async def answer_regist(problem_id: int, answer: ProblemAnswer, database: Database = Depends(get_connection)):
    # insert into answers_table という命令。valuesはdatabase.executeの引数で指定
    query = answers_table.insert()
    values = answer.dict()
    # 正誤判定
    is_correct = assert_answer(values["script"], problem_id)
    # 問題idと正誤の項目を追加
    values['problem_id'] = problem_id
    values['is_correct'] = is_correct
    # SQL実行
    ret = await database.execute(query, values)
    return values
