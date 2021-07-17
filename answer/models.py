from db import metadata, engine
from sqlalchemy import Column, Table, Integer, String, Boolean
import sys
sys.path.append('../')


answers_table = Table(
    "answers",
    metadata,
    Column("number_of_trial", Integer, primary_key=True, index=True),
    Column("problem_id", Integer, index=True),
    Column("username", String, index=True),
    Column("script", String, index=True),
    Column("is_correct", Boolean, default=True),
    Column("result", String, index=True),
)

metadata.create_all(bind=engine)
