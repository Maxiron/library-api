from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base
import uuid

class Book(Base):
    __tablename__ = "books"

    id = Column(String(100), primary_key=True, index=True, default=str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    publisher = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    is_available = Column(Boolean, default=True)