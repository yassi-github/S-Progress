from .models import problems
from .schemas import Problem
from utils.dbutils import get_connection
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from starlette.requests import Request
from databases import Database
from sqlalchemy.sql.schema import Table
from typing import List


import sys
sys.path.append('../')


router = APIRouter()


# problemsを全件検索して「ProblemSummary」のリストをjsonにして返す。
@router.get("/problems", response_model=List[Problem])
async def problems_findall(request: Request, database: Database = Depends(get_connection)):
    query = problems.select()
    return await database.fetch_all(query)


# problemsをidで検索して「Problem」をjsonにして返す。
@router.get("/problems/{problem_id}", response_model=Problem)
async def users_findone(problem_id: int, database: Database = Depends(get_connection)):
    query = problems.select().where(problems.columns.id == problem_id)
    return await database.fetch_one(query)


@router.get("/problems/{problem_id}/file")
async def serve_problem_file(problem_id: int):
    return FileResponse(path=f'alpine-cmd/problem_files/q_{problem_id}.txt', media_type='application/octet-stream', filename=f'q_{problem_id}.txt')

# update problems
@router.get("/problems/update")
async def update_problem(request: Request, database: Database = Depends(get_connection)):
    yamlconf_tuple_of_list = read_yaml.get_data_from_yaml('conf.yaml')
    # query = users.update().where(users.columns.id == user.id)
    # values = get_users_insert_dict(user)
    # ret = await database.execute(query, values)
    # return {**user.dict()}

# values = []
for tuple_idx: int, tuple_elem: list in enumerate(yamlconf_tuple_of_list):
    # ReadFromYAMLName
    if tuple_idx == 0:
        for idx, elem in tuple_elem:
            value[idx]['title'] = elem.title
            value[idx]['description'] = elem.description
    # ReadFromYAMLAnswer
    if tuple_idx == 1:
        for idx, elem in tuple_elem:
            value[idx]['shell'] = elem.shell
            value[idx]['result'] = elem.result
    # ReadFromYAMLHint
    if tuple_idx == 2:
        for idx, elem in tuple_elem:
            value[idx]['hint1'] = elem.hint1
            value[idx]['hint2'] = elem.hint2


# query_raw = "insert into my_problems (id, title, text, correct_ans) values (:id, :title, :description, :correct_ans) on duplicate key update title=values(`title`), text=values(`text`), corrent_ans=(`correct_ans`)"
# values = [
#    {"id": "1", "title": "hogehoge_title1", "text": "hugahuga_text1", "correct_ans": "piyopiyo_ans1"},
#    {"id": "2", "title": "hogehoge_title2", "text": "hugahuga_text2", "correct_ans": "piyopiyo_ans2"},
# ]
# await database.execute_many(query=query_raw, values=values)
