import requests
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from src.schemas import BookCreate, SuccessResponse
from src.models import Book

CUSTOMER_API_BASE_URL = " http://127.0.0.1:8000/api/"

def get_customers():
    response = requests.get(CUSTOMER_API_BASE_URL + "users/")
    print(response.json())
    return response.json()

def get_customer(customer_id):
    response = requests.get(f"{CUSTOMER_API_BASE_URL}/users/{customer_id}")
    return response.json()

def get_borrowed_books_for_customer(customer_id):
    response = requests.get(f"{CUSTOMER_API_BASE_URL}/borrowed-books/{customer_id}")
    return response.json()



def create_book(db: Session, book: BookCreate):
    try:
        db_book = Book(
            id=str(uuid.uuid4()),
            title=book.title,
            author=book.author,
            publisher=book.publisher,
            category=book.category,
            is_available=True
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    except Exception as e:
        return {}
    finally:
        db.close()

def delete_book(db: Session, book_id: str):
    try:
        db_book = db.query(Book).filter(Book.id == book_id).first()
        if not db_book:
            return False
        db.delete(db_book)
        db.commit()
        return True
    except Exception as e:
        return False
    finally:
        db.close()

def mark_book_as_unavailable(db: Session, book_id: str):
    try:
        db.query(Book).filter(Book.id == book_id).update({"is_available": False}, synchronize_session=False)
        db.commit()
        return True
    except Exception as e:
        return False
    finally:
        db.close()

def get_unavailable_books(db: Session):
    try:
        query = db.query(Book).filter(Book.is_available == False).all()
    except Exception as e:
        return SuccessResponse(
            message= "An error occurred",
            data={},
            status_code=500
        )
    finally:
        db.close()
    return SuccessResponse(
        message="Unavailable books retrieved successfully" if query else "No unavailable books found",
        data={
            "books": query if query else [],
        },
        status_code=200 if query else 404
    )
