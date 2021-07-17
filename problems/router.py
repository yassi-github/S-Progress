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
    return FileResponse(path=f'alpine-cmd/problem_files/{problem_id}/q.txt', media_type='application/octet-stream', filename='q.txt')
