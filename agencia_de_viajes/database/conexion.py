import psycopg2
from modelos.models import *
from sqlmodel import SQLModel, create_engine, Session
from database.datos import dbUrl

engine = create_engine(dbUrl, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as sesion:
        yield sesion

