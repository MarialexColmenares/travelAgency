import psycopg2
from models import *
from sqlmodel import SQLModel, create_engine, Session

dbUrl = "postgresql://postgres:31890@127.0.0.1:5432/travel_agency_db"
engine = create_engine(dbUrl, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as sesion:
        yield sesion

