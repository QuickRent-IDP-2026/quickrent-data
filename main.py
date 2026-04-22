from fastapi import FastAPI
from sqlalchemy import create_engine, text
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/quickrent_db")

engine = create_engine(DATABASE_URL)

@app.get("/")
def read_root():
    return {"message": "Data Service is up and running!"}

@app.get("/db-check")
def check_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "Connected to Database successfully!"}
    except Exception as e:
        return {"status": "Error", "details": str(e)}

