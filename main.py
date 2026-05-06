from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

# DB setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/quickrent_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Scooter(Base):
    __tablename__ = "scooters"
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String)
    is_available = Column(Boolean, default=True)

class Rental(Base):
    __tablename__ = "rentals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    scooter_id = Column(Integer)

@app.get("/users/{username}")
def get_user_by_username(username: str):
    db = SessionLocal()
    try:
        # Filter DB by username column
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found in DB")
        return {"id": user.id, "username": user.username, "email": user.email}
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

@app.post("/users")
def create_user(user_data: dict):
    db = SessionLocal()
    new_user = User(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password']
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "status": "User saved in DB"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# Get scooters with their availability status
@app.get("/scooters")
def get_scooters():
    db = SessionLocal()
    scooters = db.query(Scooter).all()
    db.close()
    return scooters

@app.post("/scooters")
def create_scooter(scooter_data: dict):
    db = SessionLocal()
    new_scooter = Scooter(
        model=scooter_data['model'],
        is_available=scooter_data.get('is_available', True)
    )
    try:
        db.add(new_scooter)
        db.commit()
        db.refresh(new_scooter)
        return {"id": new_scooter.id, "status": "Scooter created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# Mark a scooter as rented or available
@app.put("/scooters/{id}/rent")
def update_scooter_status(id: int, available: bool):
    db = SessionLocal()
    scooter = db.query(Scooter).filter(Scooter.id == id).first()
    if scooter:
        scooter.is_available = available
        db.commit()
    db.close()
    return {"status": "updated"}
