from sqlalchemy.orm import Session
from src.models import User, Book, BorrowedBook
from src.schemas import UserCreate, ResponseSchema
from src.config import redis_settings
from datetime import datetime, timedelta
import uuid
import json
from redis import Redis


redis_client = Redis(host=redis_settings.redis_host, port=redis_settings.redis_port, db=redis_settings.redis_db)


def get_user(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    return ResponseSchema(
        message="User found" if user else "User not found",
        data={"user_id": user.id, "email": user.email} if user else {},
        status_code=200 if user else 404
    )

def get_users(db: Session):
    users = db.query(User).all()
    serialized_users = [{"user_id": user.id, "email": user.email} for user in users]
    return ResponseSchema(
        message="Users found" if users else "Users not found",
        data={
            "users": serialized_users
        },
        status_code=200 if users else 404
    )


def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, first_name=user.first_name, last_name=user.last_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return ResponseSchema(
        message="User created successfully",
        data={"user_id": db_user.id, "email": db_user.email},
        status_code=200
    )

def get_books(db: Session, publisher: str = None, category: str = None, is_available: bool = True):
    try:
        query = db.query(Book)
        if publisher:
            query = query.filter(Book.publisher == publisher, Book.is_available == is_available)
        if category:
            query = query.filter(Book.category == category, Book.is_available == is_available)
        if publisher and category:
            query = query.filter(Book.publisher == publisher, Book.category == category, Book.is_available == is_available)

        else:
            query = query.filter(Book.is_available == is_available)
    except Exception as e:
        print(f"An error occurred: {e}")
        return ResponseSchema(
            message="An error occurred",
            data=[],
            status_code=500
        )
    finally:
        # close the session
        db.close()

    return ResponseSchema(

        message="Books found" if query.all() else "Books not found",
        data={
            "books": [{"id": book.id, "title": book.title, "author": book.author, "publisher": book.publisher, "category": book.category, "is_available": book.is_available} for book in query]
            },
        status_code=200 if query.all() else 404
    )

def get_book(db: Session, book_id: str):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
    except Exception as e:
        print(f"An error occurred: {e}")
        return ResponseSchema(
            message="An error occurred",
            data={},
            status_code=500
        )
    finally:
        # close the session
        db.close()

    return ResponseSchema(
        message="Book found" if book else "Book not found",
        data={"id": book.id, "title": book.title, "author": book.author, "publisher": book.publisher, "category": book.category, "is_available": book.is_available} if book else {},
        status_code=200 if book else 404
    )

def add_new_book(db: Session, book: Book):
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
    return ResponseSchema(
        message="Book added successfully",
        data={"id": db_book.id, "title": db_book.title, "author": db_book.author, "publisher": db_book.publisher, "category": db_book.category, "is_available": db_book.is_available},
        status_code=200
    )

def delete_book(db: Session, book_id: str):
    db_book = get_book(db, book_id=book_id)
    if not db_book:
        return None
    db.query(Book).filter(Book.id == book_id).delete()
    db.commit()
    return ResponseSchema(
        message="Book deleted successfully",
        data={"id": db_book.id, "title": db_book.title, "author": db_book.author, "publisher": db_book.publisher, "category": db_book.category, "is_available": db_book.is_available},
        status_code=200
    )

def borrow_book(db: Session, book_id: str, user_email: str, days: int):
    db_book = get_book(db, book_id=book_id)
    if not db_book:
        return None
    db_borrowed = BorrowedBook(
        id=str(uuid.uuid4()),
        user_email=user_email,
        book_id=book_id,
        return_date=datetime.utcnow() + timedelta(days=days)
    )

    # Mark the book as unavailable
    db.query(Book).filter(Book.id == book_id).update({"is_available": False}, synchronize_session=False)

    db.add(db_borrowed)
    db.commit()
    db.refresh(db_borrowed)
    # Notify Admin API about the borrowed book 
    message = {"action": "borrow", "book": {"id": db_borrowed.book_id, "user_email": db_borrowed.user_email}}
    redis_client.publish('book_updates', json.dumps(message))


    return ResponseSchema(
        message="Book borrowed successfully",
        data={"id": db_borrowed.id, "user_email": db_borrowed.user_email, "book_id": db_borrowed.book_id, "borrow_date": db_borrowed.borrow_date, "return_date": db_borrowed.return_date},
        status_code=200
    )

def get_borrowed_books_for_customer(db: Session, customer_id: int):
    borrowed_books = db.query(BorrowedBook).filter(BorrowedBook.user_email == customer_id).all()
    data = [
        {
            "book_name": book.title,
            "author": book.author,
            "user_email": book.user_email,
            "book_id": book.book_id,
            "borrow_date": book.borrow_date,
            "return_date": book.return_date
        } for book in borrowed_books
    ]
    return ResponseSchema(
        message="Borrowed books found" if borrowed_books else "Borrowed books not found",
        data=data,
        status_code=200 if borrowed_books else 404
    )

