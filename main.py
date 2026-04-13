from fastapi import Depends, FastAPI
from sqlmodel import SQLModel, Session
from database import get_db, engine
import models
from sqlalchemy import text

app = FastAPI()

SQLModel.metadata.create_all(engine)

@app.get("/")
def home():
    return {"message": "Sistema Agencia de Viajes"}

@app.get("/test_db/")
def test_db(db: Session = Depends(get_db)): 
    try:
        db.execute(text("SELECT 1"))
        return {"status": "Conexión exitosa"}
    except Exception as e:
        return {"status": "Error", "detail": str(e)}