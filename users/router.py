from utils.dbutils import get_connection
from .schemas import UserCreate, UserUpdate, UserSelect
from .models import users
import hashlib

from fastapi import APIRouter, Depends
from starlette.requests import Request
from databases import Database
from sqlalchemy.sql.schema import Table
from typing import List

import sys
sys.path.append('../')


router = APIRouter()


# 入力したパスワード（平文）をハッシュ化して返す。
def get_users_insert_dict(user: Table):
    pwhash = hashlib.sha256(user.password.encode('utf-8')).hexdigest()
    values = user.dict()
    values.pop("password")
    values["hashed_password"] = pwhash
    return values


# usersを全件検索して「UserSelect」のリストをjsonにして返す。
@router.get("/users/", response_model=List[UserSelect])
async def users_findall(request: Request, database: Database = Depends(get_connection)):
    query = users.select()
    return await database.fetch_all(query)


# usersをidで検索して「UserSelect」をjsonにして返す。
@router.get("/users/find", response_model=UserSelect)
async def users_findone(id: int, database: Database = Depends(get_connection)):
    query = users.select().where(users.columns.id == id)
    return await database.fetch_one(query)


# usersを新規登録する。
@router.post("/users/create", response_model=UserSelect)
async def users_create(user: UserCreate, database: Database = Depends(get_connection)):
    # validatorは省略
    query = users.insert()
    values = get_users_insert_dict(user)
    ret = await database.execute(query, values)
    return {**user.dict()}


# usersを更新。
@router.post("/users/update", response_model=UserSelect)
async def users_update(user: UserUpdate, database: Database = Depends(get_connection)):
    # validatorは省略
    query = users.update().where(users.columns.id == user.id)
    values = get_users_insert_dict(user)
    ret = await database.execute(query, values)
    return {**user.dict()}


# usersを削除。
@router.post("/users/delete")
async def users_delete(user: UserUpdate, database: Database = Depends(get_connection)):
    query = users.delete().where(users.columns.id == user.id)
    ret = await database.execute(query)
    return {"result": "delete success"}
