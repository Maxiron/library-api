# python imports
import asyncio
import json

# FastAPI imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Third-party imports
from redis import Redis 

# Local imports
from src.database import SessionLocal
from src.schemas import BookCreate
from src.crud import (
    add_new_book, delete_book,
)
from src.config import redis_settings
from src.routers import books, users

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router, prefix="/api")
app.include_router(users.router, prefix="/api")


# Redis setup for Pub/Sub
redis_client = Redis(host=redis_settings.redis_host, port=redis_settings.redis_port, db=redis_settings.redis_db)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Background task to listen for admin updates
def start_admin_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('book_updates')

    async def listen():
        # message = {
        #     "action": "add", 
        #     "book": {
        #         "id": 1,
        #         "title": "The Alchemist",
        #         "author": "Paulo Coelho",
        #         "publisher": "HarperOne",
        #         "category": "Adventure",
        #         "is_available": True
        #     }
        # }
        for message in pubsub.listen():
            print(f"Message: {message}")
            data = message['data']
            print(f"Received: {data}")
            data = json.loads(data)
            if data['action'] == 'add':
                book = data['book']
                await add_new_book(db=SessionLocal(), book=BookCreate(**book))
            elif data['action'] == 'remove':
                book_id = data['book']['id']
                await delete_book(db=SessionLocal(), book_id=book_id)
            else:
                print("Invalid action")
            

    loop = asyncio.get_event_loop()
    loop.create_task(listen())

start_admin_listener()



@app.get("/")
async def home():
    response ={
        "status": True,
        "message": "Library Customer API: Welcome to the Library Customer API"
    }
    # Return a JSON response
    return response