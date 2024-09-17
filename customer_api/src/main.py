# python imports
import asyncio

# FastAPI imports
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# Third-party imports
from redis import Redis 

# Local imports
from src.models import User, Book
from src.database import SessionLocal, engine, Base
from src.schemas import UserCreate, Book, BorrowedBook, User, BookCreate
from src.crud import (
    get_user, create_user, get_books, get_book, borrow_book, 
    sync_books, add_new_book, get_users, delete_book, get_borrowed_books_for_customer,
)
from src.config import redis_settings

app = FastAPI()

# Redis setup for Pub/Sub
redis_client = Redis(host=redis_settings.redis_host, port=redis_settings.redis_port, db=redis_settings.redis_db)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Background task to listen for admin updates
def start_admin_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('admin_channel')

    async def listen():
        for message in pubsub.listen():
            if message['type'] == 'message':
                # Process the admin message (e.g., sync books)
                sync_books(db=SessionLocal(), data=message['data'])

    loop = asyncio.get_event_loop()
    loop.create_task(listen())

start_admin_listener()



@app.get("/")
async def home():
    response ={
        "status": True,
        "message": "Library Admin API: Welcome to the Library Admin API"
    }
    # Return a JSON response
    return response

# Enroll user endpoint
@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

# Get available books endpoint
@app.get("/books/", response_model=list[Book])
def read_books(publisher: str = None, category: str = None, db: Session = Depends(get_db)):
    books = get_books(db, publisher=publisher, category=category)
    return books

@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: str, db: Session = Depends(get_db)):
    db_book = get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.post("/borrow/{book_id}", response_model=BorrowedBook)
def borrow_book(book_id: str, days: int, user_email: str, db: Session = Depends(get_db)):
    borrowed_book = borrow_book(db=db, book_id=book_id, user_email=user_email, days=days)
    if not borrowed_book:
        raise HTTPException(status_code=400, detail="Cannot borrow book")
    return borrowed_book



# Admin only routes

# Add book endpoint
@app.post("/books/", response_model=Book)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = add_new_book(db=db, book=book)
    return db_book

# Delete book endpoint
@app.delete("/books/{book_id}")
def delete_single_book(book_id: str, db: Session = Depends(get_db)):
    db_book = get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return delete_book(db=db, book_id=book_id)

# Get unavailable books endpoint
@app.get("/books/unavailable", response_model=list[Book])
def unavailable_books(db: Session = Depends(get_db)):
    books = get_books(db, is_available=False)
    return books

# Get borrowed books for customer endpoint
@app.get("/borrowings/{customer_id}", response_model=list[BorrowedBook])
def list_borrowings(customer_id: int, db: Session = Depends(get_db)):
    borrowed_books = get_borrowed_books_for_customer(db, customer_id=customer_id)
    return borrowed_books


#Get specific user
@app.get("/users/{email}", response_model=User)
def read_user(email: str, db: Session = Depends(get_db)):
    db_user = get_user(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#Get all users
@app.get("/users/", response_model=list[User])
def read_users(db: Session = Depends(get_db)):
    users = get_users(db)
    return users

