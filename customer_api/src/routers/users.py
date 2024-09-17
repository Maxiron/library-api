from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from src.crud import get_users, get_user, create_user
from src.database import SessionLocal
from src.schemas import UserCreate

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/users", tags=["Users"])



# Enroll user endpoint
@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)


# Admin Service Endpoints

#Get specific user
@router.get("/{email}")
def read_user(email: str, db: Session = Depends(get_db)):
    db_user = get_user(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#Get all users
@router.get("/")
def read_users(db: Session = Depends(get_db)):
    users = get_users(db)
    return users