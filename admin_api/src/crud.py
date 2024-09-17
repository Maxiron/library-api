import requests

from src.schemas import BookCreate

CUSTOMER_API_BASE_URL = "http://customer-api:8000/api/v1/"

def get_customers():
    response = requests.get(CUSTOMER_API_BASE_URL)
    return response.json()

def get_borrowed_books_for_customer(customer_id):
    response = requests.get(f"{CUSTOMER_API_BASE_URL}/borrowed-books/{customer_id}")
    return response.json()

def add_book_to_catalog(book: BookCreate):
    response = requests.post(f"{CUSTOMER_API_BASE_URL}/books", json=book.dict())
    return response.json()

def remove_book_from_catalog(book_id: int):
    response = requests.delete(f"{CUSTOMER_API_BASE_URL}/books/{book_id}")
    return response.json()

def get_unavailable_books():
    response = requests.get(f"{CUSTOMER_API_BASE_URL}/borrowed-books")
    return response.json()

