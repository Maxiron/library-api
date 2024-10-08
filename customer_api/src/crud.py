from sqlalchemy.orm import Session
from src.models import User, Book, BorrowedBook
from src.schemas import UserCreate, ResponseSchema, BookCreate
from src.config import redis_settings
from datetime import datetime, timedelta
import uuid
import json
from redis import StrictRedis


REDIS_CHANNEL = "book_updates"
redis_client = StrictRedis(
    host=redis_settings.redis_host, port=redis_settings.redis_port, db=redis_settings.redis_db, decode_responses=True
)


def get_user(db: Session, id: int = None, email: str = None):
    try:
        if email:
            user = db.query(User).filter(User.email == email).first()
        else:
            user = db.query(User).filter(User.id == id).first()
        return user
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
    

def get_users(db: Session):
    try:
        users = db.query(User).all()
        serialized_users = [
            {
                "user_id": user.id, 
                "email": user.email, 
                "first_name": user.firstname,
                "last_name": user.lastname
            } for user in users]
        return ResponseSchema(
            message="Users found" if users else "Users not found",
            data={
                "users": serialized_users
            },
            status_code=200 if users else 404
        )
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


def create_user(db: Session, user: UserCreate):
    try:
        db_user = User(email=user.email, firstname=user.first_name, lastname=user.last_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return ResponseSchema(
            message="User created successfully",
            data={"user_id": db_user.id, "email": db_user.email},
            status_code=200
        )
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

        return ResponseSchema(
            message="Books found" if query.all() else "Books not found",
            data={
                "books": [
                    {
                        "id": book.id, 
                        "title": book.title, 
                        "author": book.author, 
                        "publisher": book.publisher, 
                        "category": book.category,
                        "is_available": book.is_available
                    } for book in query]
                },
            status_code=200 if query.all() else 404
        )
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


def get_book(db: Session, book_id: str, is_available: bool = True):
    try:
        book = db.query(Book).filter(Book.id == book_id, Book.is_available == is_available).first()
        if book is None:
            return None
        return ResponseSchema(
            message="Book found",
            data={
                "id": book.id, 
                "title": book.title, 
                "author": book.author, 
                "publisher": book.publisher, 
                "category": book.category, 
                "is_available": book.is_available
            },
            status_code=200 if book else 404
        )
            
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


def add_new_book(db: Session, book: BookCreate):
    # book = book.dict()
    try:
        db_book = Book(
            id=book.id,
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
    except Exception as e:
        return ResponseSchema(
            message="An error occurred",
            data={},
            status_code=500
        )
    finally:
        db.close()

def delete_book(db: Session, book_id: str):
    try:
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
    except Exception as e:
        return ResponseSchema(
            message="An error occurred",
            data={},
            status_code=500
        )
    finally:
        db.close()

def borrow_book(db: Session, book_id: str, user_email: str, days: int):
    # try:
        db_book = get_book(db=db, book_id=book_id, is_available=True)
        if not db_book:
            return None

        db_borrowed = BorrowedBook(
            user_email=user_email,
            book_id=book_id,
            return_date=datetime.utcnow() + timedelta(days=days)
        )

        db.add(db_borrowed)
        db.commit()
        db.refresh(db_borrowed)

        # Mark the book as unavailable
        db.query(Book).filter(Book.id == book_id).update({"is_available": False}, synchronize_session=False)
        db.commit()

        # Notify Admin API about the borrowed book 
        message = {"action": "borrow", "book_id": db_borrowed.book_id}
        redis_client.publish(REDIS_CHANNEL, str(message))


        return ResponseSchema(
            message="Book borrowed successfully",
            data={},
            status_code=200
        )
    # except Exception as e:
    #     return ResponseSchema(
    #         message=f"An error occurred: {str(e)}",
    #         data={},
    #         status_code=500
    #     )
    # finally:
    #     db.close()

def get_borrowed_books_for_customer(db: Session, customer_id: int):
    # try:
        # Get user email
        user = db.query(User).filter(User.id == customer_id).first()
        if user:
            user_email = user.email
        else:
            return ResponseSchema(
                message="User not found",
                data={},
                status_code=404
            )   
        borrowed_books = db.query(BorrowedBook).filter(BorrowedBook.user_email == user_email).all()
        data = [
            {
                "book_id": book.book_id,
                "book_title":book.book.title,
                "book_author": book.book.author,
                "book_publisher": book.book.publisher,
                "book_category": book.book.category,
                "user_email": book.user_email,
                "borrow_date": book.borrow_date,
                "return_date": book.return_date
            } for book in borrowed_books
        ]
        return ResponseSchema(
            message="Borrowed books found" if borrowed_books else "Borrowed books not found",
            data={
                "books": data
            },
            status_code=200 if borrowed_books else 404
        )
    # except Exception as e:
    #     return ResponseSchema(
    #         message=f"An error occurred: {str(e)}",
    #         data={},
    #         status_code=500
    #     )
    # finally:
    #     db.close()

