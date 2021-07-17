from databases import Database
from sqlalchemy import create_engine, MetaData


DATABASE = 'postgresql'
USER = 'root'
PASSWORD = 'password'
HOST = 'db'
PORT = '5432'
DB_NAME = 'spro'

DATABASE_URL = '{}://{}:{}@{}:{}/{}'.format(
    DATABASE, USER, PASSWORD, HOST, PORT, DB_NAME)

# export
database = Database(DATABASE_URL, min_size=5, max_size=20)

ECHO_LOG = False

# export
engine = create_engine(DATABASE_URL, echo=ECHO_LOG)

# export
metadata = MetaData()
