from db import metadata, engine
from sqlalchemy import Column, Table, Integer, String, Boolean

import sys
sys.path.append('../')


users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String, index=True),
    Column("email", String, index=True),
    Column("hashed_password", String),
    Column("is_active", Boolean(), default=True),
    Column("is_superuser", Boolean(), default=False)
)

metadata.create_all(bind=engine)
