# python imports
import asyncio
import json
import threading
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Third-party imports
from redis import StrictRedis 

# Local imports
from src.database import SessionLocal
from src.schemas import BookCreate
from src.crud import (
    add_new_book, delete_book,
)
from src.config import redis_settings
from src.routers import books, users

REDIS_CHANNEL = "book_updates"
redis_client = StrictRedis(
    host=redis_settings.redis_host, port=redis_settings.redis_port, db=redis_settings.redis_db, decode_responses=True
)

# Background task to listen for admin updates
def listen_to_channel():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(REDIS_CHANNEL)

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data']
            print(f"Received message: {data} on channel: {REDIS_CHANNEL}")
            
            try:
                if isinstance(data, str):
                    str_data = data.replace("'", '"')  # Convert single quotes to double quotes                    
                    str_data = str_data.replace("True", "true")  # Convert True to true

                # Load the converted string into a Python dictionary
                data = json.loads(str_data)

                # Ensure the action exists and handle based on 'add' or 'remove'
                action = data['action']
                if action == 'add':
                    book_data = data['book']
                    if book_data:
                        # Create a new book from the provided book data
                        with SessionLocal() as db:
                            add_new_book(db=db, book=BookCreate(**book_data))
                elif action == 'remove':
                    book_id = data['book']['id']
                    if book_id:
                        # Delete the book with the given ID
                        with SessionLocal() as db:
                            delete_book(db=db, book_id=book_id)
                else:
                    print("Invalid action")
            except json.JSONDecodeError as e:                
                print(f"Failed to decode JSON message; {str(e)}")
            except Exception as e:
                print(f"Error processing message: {str(e)}")
            

async def start_redis_listener(background_tasks: BackgroundTasks):
    # Start the background task to listen for messages
    # background_tasks.add_task(listen_to_channel)
    asyncio.get_event_loop().run_in_executor(None, listen_to_channel)




async def lifespan():
    print(f"Subscribing to {REDIS_CHANNEL} on startup...")
    await start_redis_listener(BackgroundTasks())


app = FastAPI(on_startup=[lifespan])

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
        "message": "Library Customer API: Welcome to the Library Customer API"
    }
    # Return a JSON response
    return response