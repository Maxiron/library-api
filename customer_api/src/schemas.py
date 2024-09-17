from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: str

    class Config:
        from_attributes = True

class BookBase(BaseModel):
    title: str
    author: str
    publisher: str
    category: str

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: str    
    is_available: bool
    class Config:
        from_attributes = True

class BorrowedBookBase(BaseModel):
    id: str
    user_email: str
    book_id: str
    borrow_date: datetime
    return_date: datetime

class BorrowedBook(BorrowedBookBase):
    class Config:
        from_attributes = True

class ResponseSchema(BaseModel):
    message: str
    data: dict
    status_code: int
