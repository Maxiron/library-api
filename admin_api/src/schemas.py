from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    publisher: str
    category: str


class SuccessResponse(BaseModel):
    message: str
    data: dict
    status_code: int