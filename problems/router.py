from .models import problems
from .schemas import Problem
from utils.dbutils import get_connection
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from starlette.requests import Request
from databases import Database
from sqlalchemy.sql.schema import Table
from typing import List
from .read_yaml import *
# import .read_yaml as ry
import hashlib

import sys
sys.path.append('../')


router = APIRouter()


# problemsを全件検索して「ProblemSummary」のリストをjsonにして返す。
@router.get("/problems", response_model=List[Problem])
async def problems_findall(request: Request, database: Database = Depends(get_connection)):
    # query = problems.select()
    query = 'SELECT * FROM problems ORDER BY "id"'
    return await database.fetch_all(query)

# update problems
@router.get("/problems-update")
async def update_problem(database: Database = Depends(get_connection)):
    # yamlconf_tuple_of_list = read_yaml.get_data_from_yaml('conf.yaml')
    # yamlconf_tuple_of_list = ry.get_data_from_yaml('conf.yaml')
    yamlconf_tuple_of_list = get_data_from_yaml('problems/conf.yaml')
    # query = users.update().where(users.columns.id == user.id)
    # values = get_users_insert_dict(user)
    # ret = await database.execute(query, values)
    # return {**user.dict()}

    # 問題ごとの情報を格納する辞書を作成
    values = [{} for _ in range(len(yamlconf_tuple_of_list[0]))]
    for tuple_idx, tuple_elem in enumerate(yamlconf_tuple_of_list):
        # ReadFromYAMLName
        if tuple_idx == 0:
            for idx, elem in enumerate(tuple_elem):
                defaultProblemLen = 1
                values[idx]['id'] = idx + defaultProblemLen + 1
                values[idx]['title'] = elem.title
                values[idx]['text'] = elem.description
        # ReadFromYAMLAnswer
        if tuple_idx == 1:
            for idx, elem in enumerate(tuple_elem):
                values[idx]['shell'] = elem.shell
                values[idx]['correct_ans'] = hashlib.sha256(elem.result.encode()).hexdigest()
        # ReadFromYAMLHint
        if tuple_idx == 2:
            # return tuple_elem
            for idx, elem in enumerate(tuple_elem):
                values[idx]['hint1'] = elem.hint1
                values[idx]['hint2'] = elem.hint2
        
        # return yamlconf_tuple_of_list[2][0].hint2
    # return values
    # 反映されない。valuesの値のクォートがシングルクォートにならないから？手動ではいける

    # query_raw = "INSERT INTO problems(id, title, text, correct_ans) VALUES (:id, :title, :text, :correct_ans)"
    # query_raw = 'INSERT INTO problems (id, title, text, correct_ans) VALUES (:id, :title, :description, :result)'
    query_raw = 'INSERT INTO problems (id, title, text, hint1, hint2, shell, correct_ans) VALUES (:id, :title, :text, :hint1, :hint2, :shell, :correct_ans) ON CONFLICT ON CONSTRAINT "problems_id_key" DO UPDATE SET title = :title, text = :text, hint1 = :hint1, hint2 = :hint2, shell = :shell, correct_ans = :correct_ans'
    # values = [
    #    {"id": 7, "title": "hogehoge_title1", "text": "hugahuga_text1", "correct_ans": "piyopiyo_ans1"},
    #    {"id": 8, "title": "hogehoge_title2", "text": "hugahuga_tex_2", "correct_ans": "piyopiyo_as_2"},
    # ]
    # values = {"id": 4, "title": "hogehoge_title2", "text": "hugahuga_text2", "correct_ans": "piyopiyo_ans2"}

    await database.execute_many(query=query_raw, values=values)
    return "problems updated."

# problemsをidで検索して「Problem」をjsonにして返す。
@router.get("/problems/{problem_id}", response_model=Problem)
async def users_findone(problem_id: int, database: Database = Depends(get_connection)):
    query = problems.select().where(problems.columns.id == problem_id)
    return await database.fetch_one(query)


@router.get("/problems/{problem_id}/file")
async def serve_problem_file(problem_id: int):
    return FileResponse(path=f'alpine-cmd/problem_files/q_{problem_id}.txt', media_type='application/octet-stream', filename=f'q_{problem_id}.txt')


@router.get("/problems/{problem_id}/hint1")
async def users_findone(problem_id: int, database: Database = Depends(get_connection)):
    query = 'SELECT hint1 FROM problems WHERE id = :id'
    return await database.fetch_one(query=query, values={"id": problem_id})

@router.get("/problems/{problem_id}/hint2")
async def users_findone(problem_id: int, database: Database = Depends(get_connection)):
    query = 'SELECT hint2 FROM problems WHERE id = :id'
    return await database.fetch_one(query=query, values={"id": problem_id})

@router.get("/problems/{problem_id}/answer")
async def users_findone(problem_id: int, database: Database = Depends(get_connection)):
    query = 'SELECT shell FROM problems WHERE id = :id'
    return await database.fetch_one(query=query, values={"id": problem_id})
