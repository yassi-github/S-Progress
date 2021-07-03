from answer.schemas import ProblemAnswer, ProblemAnswerResult
from fastapi import APIRouter, Depends
from databases import Database
from utils.dbutils import get_connection

from random import choices
from string import ascii_letters, digits

from .models import answers


router = APIRouter()


def random_name(n: int) -> str:
   return ''.join(choices(ascii_letters + digits, k=n))


# シェルスクリプトの実行可能ファイルを作成する
def create_script_file(script: str) -> str:
    workingdir: str = 'script_files'
    filename: str = random_name(10)
    with open(filename, 'w') as file:
        file.write(script)
    script_file_path: str = workingdir + '/' + filename
    return script_file_path


# コンテナを作成してファイルを実行し、結果を返す
def create_container(script_file_path: str) -> str:
    # test: fake result
    script_result: str = '321cba'
    return script_result


# 実行して結果を返す
def run_script(script: str) -> str:
    script_file_path = create_script_file(script)
    script_result: str = create_container(script_file_path)
    return script_result


# 問題テーブルから正答を持ってくる
def find_correct_answer(problem_id: int) -> str:
    # test: fake answer
    correct_answer: str = '321cba'
    return correct_answer


# answerを検証
# ArgType: Table ? UserCreate ? Union? dict?
# RetType: same above
def assert_answer(answer: dict, problem_id: int) -> bool:
    script: str = answer['script']
    problem_id: int = problem_id
    script_result: str = run_script(script)
    correct_answer: str = find_correct_answer(problem_id)
    is_correct: bool = script_result is correct_answer
    return is_correct


# scriptを受付
@router.post("/problems/{problem_id}/answer", response_model=ProblemAnswerResult)
async def answer_regist(problem_id: int, answer: ProblemAnswer, database: Database = Depends(get_connection)):
    query = answers.insert()
    values = answer.dict()
    is_correct = assert_answer(values, problem_id)
    values['problem_id'] = problem_id
    values['is_correct'] = is_correct
    ret = await database.execute(query, values)
    return values
