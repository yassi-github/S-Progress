from sqlalchemy import Column, Table, Integer, String

from db import metadata, engine

import sys
sys.path.append('../')


problems = Table(
    "problems",
    metadata,
    Column("id", Integer, primary_key=True, index=True, unique=True),
    Column("title", String, index=True),
    Column("text", String, index=True),
    Column("correct_ans", String, index=True),
)

metadata.create_all(bind=engine)
