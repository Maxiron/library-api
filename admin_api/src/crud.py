import requests
import uuid
from  datetime import datetime

from sqlalchemy.orm import Session

from src.schemas import BookCreate, SuccessResponse
from src.models import Book as BookModel

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
    # book_data = book.dict() 
    # print(book_data)
    try:
        db_book = BookModel(
            title=book.title,
            author=book.author,
            publisher=book.publisher,
            category=book.category
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        # get the book details
        book_details = {
            "id": db_book.id,
            "title": db_book.title,
            "author": db_book.author,
            "publisher": db_book.publisher,
            "category": db_book.category,
            "is_available": db_book.is_available
        }
        print(book_details) 
        return book_details
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return SuccessResponse(
            message="An error occurred",
            data={},
            status_code=500
        )
    finally:
        db.close()

def delete_book(db: Session, book_id: str):
    try:
        db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
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
        db.query(BookModel).filter(BookModel.id == book_id).update({"is_available": False}, synchronize_session=False)
        db.commit()
        return True
    except Exception as e:
        return False
    finally:
        db.close()

def get_unavailable_books(db: Session):
    try:
        query = db.query(BookModel).filter(BookModel.is_available == False).all()
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
