import sys
sys.path.append('../')
from sqlalchemy import Column, Table, Integer, String, Boolean
from db import metadata, engine


answers_table = Table(
    "answers",
    metadata,
    Column("problem_id", Integer, primary_key=True, index=True),
    Column("username", String, index=True),
    Column("script", String, index=True),
    Column("is_correct", Boolean(), default=True),
)

metadata.create_all(bind=engine)
