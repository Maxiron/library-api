from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import redis_settings
from src.schemas import BookCreate
from src.crud import (
    add_book_to_catalog, remove_book_from_catalog, get_unavailable_books,
    get_customers, get_borrowed_books_for_customer, 
)
from redis import Redis
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis setup for Pub/Sub
redis_client = Redis(host=redis_settings.redis_host, port=redis_settings.redis_port, db=redis_settings.redis_db)

@app.get("/")
async def home():
    response ={
        "status": True,
        "message": "Library Admin API: Welcome to the Library Admin API"
    }
    # Return a JSON response
    return response

@app.post("/books")
def add_book(book: BookCreate):
    response = add_book_to_catalog(book)
    # Publish to Redis
    message = {"action": "add", "book": response}
    redis_client.publish('book_updates', json.dumps(message))
    return response

@app.delete("/books/{book_id}")
def remove_book(book_id: int):
    response = remove_book_from_catalog(book_id)
    # Publish to Redis
    message = {"action": "remove", "book": {"id": book_id}}
    redis_client.publish('book_updates', json.dumps(message))
    return response

@app.get("/users")
def list_users():
    return get_customers()

@app.get("/borrowings/{customer_id}")
def list_borrowings(customer_id: int):
    return get_borrowed_books_for_customer(customer_id)

@app.get("/books/unavailable")
def unavailable_books():
    return get_unavailable_books()
