from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_archived = Column(Boolean, default=False)

class Trucker(Base):
    __tablename__ = "truckers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    company_name = Column(String, nullable=True)
    province_of_issue = Column(String)
    is_archived = Column(Boolean, default=False)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime, nullable=True)
    verified_by = Column(String, nullable=True)
