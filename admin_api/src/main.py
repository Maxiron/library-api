from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import redis_settings
from src.schemas import BookCreate, SuccessResponse
from src.database import SessionLocal
from src.crud import (
    create_book, delete_book, get_customer,
    get_customers, get_borrowed_books_for_customer, 
    mark_book_as_unavailable, get_unavailable_books
)
from redis import Redis
import json
import asyncio

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


def start_admin_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('book_updates')

    async def listen():
        for message in pubsub.listen():
            data = message['data']
            print(f"Received: {data}")
            data = json.loads(data)
            if data['action'] == 'borrow':
                # Mark book as unavailable
                mark_book_as_unavailable(db=SessionLocal(), book_id=data['book_id'])                
            else:
                print("Invalid action")
            

    loop = asyncio.get_event_loop()
    loop.create_task(listen())

start_admin_listener()

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    response = create_book(book)
    # Publish to Redis
    message = {"action": "add", "book": response}
    redis_client.publish('book_updates', json.dumps(message))
    return SuccessResponse(message="Book added successfully", data=response, status_code=200)

@app.delete("/books/{book_id}")
def remove_book(book_id: int):
    response = delete_book(book_id)
    # Publish to Redis
    message = {"action": "remove", "book": {"id": book_id}}
    redis_client.publish('book_updates', json.dumps(message))
    return response

@app.get("/users")
def list_users():
    return get_customers()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return get_customer(user_id)

@app.get("/borrowings/{customer_id}")
def list_borrowings(customer_id: int):
    return get_borrowed_books_for_customer(customer_id)

@app.get("/books/unavailable")
def unavailable_books():
    return get_unavailable_books(db=SessionLocal())
