from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.config import redis_settings
from src.schemas import BookCreate, SuccessResponse
from src.database import SessionLocal
from src.crud import (
    create_book, delete_book, get_customer,
    get_customers, get_borrowed_books_for_customer, 
    mark_book_as_unavailable, get_unavailable_books
)
from redis import StrictRedis
import json
import asyncio
import threading
from contextlib import asynccontextmanager

REDIS_CHANNEL = "book_updates"

redis_client = StrictRedis(
    host=redis_settings.redis_host, port=redis_settings.redis_port, db=redis_settings.redis_db, decode_responses=True
)


# Background task to listen for admin updates
def listen_to_channel():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(REDIS_CHANNEL)

    for message in pubsub.listen():
        # Ensure we only process actual messages
        if message['type'] == 'message':
            data = message['data']
            print(f"Received: {data}")

            try:
                # Parse the data as JSON
                data = json.loads(data)
                
                # Check the action and process accordingly
                if data['action'] == 'borrow':
                    book_id = data.get('book_id')
                    if book_id:
                        # Mark the book as unavailable
                        with SessionLocal() as db:
                            mark_book_as_unavailable(db=db, book_id=book_id)
                    else:
                        print("Missing book_id in message")
                else:
                    print("Invalid action")
            except json.JSONDecodeError:
                print("Failed to decode JSON message")
            except Exception as e:
                print(f"Error processing message: {str(e)}")

async def start_redis_listener():
    thread = threading.Thread(target=listen_to_channel)
    thread.start()


async def lifespan():
    print(f"Subscribing to {REDIS_CHANNEL} on startup...")
    await start_redis_listener()

app = FastAPI(on_startup=[lifespan])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/")
async def home():
    response ={
        "status": True,
        "message": "Library Admin API: Welcome to the Library Admin API"
    }
    # Return a JSON response
    return response

@app.post("/api/books")
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    response = create_book(db=db, book=book)
    # Publish to Redis
    message = {"action": "add", "book": response}
    redis_client.publish(REDIS_CHANNEL, str(message))
    return SuccessResponse(message="Book added successfully", data={"book": response}, status_code=200)

@app.delete("/api/books/{book_id}")
def remove_book(book_id: int, db: Session = Depends(get_db)):
    response = delete_book(db=db, book_id=book_id)
    # Publish to Redis
    message = {"action": "remove", "book": {"id": book_id}}
    redis_client.publish(REDIS_CHANNEL, json.dumps(message))
    return response

@app.get("/api/users")
def list_users():
    return get_customers()

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    return get_customer(user_id)

@app.get("/api/borrowings/{customer_id}")
def list_borrowings(customer_id: int):
    return get_borrowed_books_for_customer(customer_id)

@app.get("/api/books/unavailable")
def unavailable_books():
    return get_unavailable_books(db=SessionLocal())
