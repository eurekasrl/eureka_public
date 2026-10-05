from sqlalchemy import Column, String, Integer, Text
from db.db import Base

# Define your Table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))

class AppConfig(Base):
    __tablename__ = "config"
    key = Column(String(50), primary_key=True)
    value = Column(Text) # This is where we will store the OneDrive Refresh Token