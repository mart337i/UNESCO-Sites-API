from fastapi import FastAPI, UploadFile, File, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

DATABASE_URL = "sqlite:///./whc-sites.db"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


async def get_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()