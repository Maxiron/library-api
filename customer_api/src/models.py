from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

from uuid import uuid4
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    borrowed_books = relationship("BorrowedBook", back_populates="user")

class Book(Base):
    __tablename__ = 'books'

    # id is a uuid4 string
    id = Column(String, primary_key=True, default=str(uuid4()))
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    publisher = Column(String(200), nullable=False)
    # Category List: Fiction, Non-Fiction, Mystery, Thriller, Romance, History, Science etc.
    category = Column(String(100), nullable=False)
    is_available = Column(Boolean, default=True)

class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_email = Column(String, ForeignKey("users.email"))
    book_id = Column(String, ForeignKey("books.id"))
    borrow_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime)
    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book")



