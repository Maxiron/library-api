from fastapi import APIRouter, Query, Depends, Request, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import traceback
from fastapi.responses import JSONResponse
from typing import List
from src.crud import get_books, get_book, borrow_book, add_new_book, delete_book, get_borrowed_books_for_customer
from src.database import SessionLocal
from src.schemas import BorrowedBook, Book, BookCreate, BorrowedBookCreate, ResponseSchema




router = APIRouter(prefix="/books", tags=["Books"])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get available books endpoint
@router.get("/")
async def read_books(publisher: str = None, category: str = None, db: Session = Depends(get_db)):
    books = get_books(db, publisher=publisher, category=category)
    return books


# Get single book endpoint
@router.get("/{book_id}")
async def read_book(book_id: str, db: Session = Depends(get_db)):
    db_book = get_book(db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

# Filter books endpoint
@router.get("")
async def filter_books(publisher: Optional[str] = Query(None), category: Optional[str] = Query(None), db: Session = Depends(get_db)):
    books = get_books(db, publisher=publisher, category=category)
    return books

# Borrow single book endpoint
@router.post("/borrow/{book_id}")
async def borrow_single_book(book_id: str, data: BorrowedBookCreate, db: Session = Depends(get_db)):
    borrowed_book = borrow_book(db=db, book_id=book_id, user_email=data.user_email, days=data.days)
    if not borrowed_book:
        return ResponseSchema(
            message="Book is currently unavailable",
            data={},
            status_code=404
        )
    return borrowed_book


# Admin Service Endpoints

# Get borrowed books for customer endpoint
@router.get("/borrowings/{customer_id}")
async def list_borrowings(customer_id: int, db: Session = Depends(get_db)):
    borrowed_books = get_borrowed_books_for_customer(db, customer_id=customer_id)
    return borrowed_books



