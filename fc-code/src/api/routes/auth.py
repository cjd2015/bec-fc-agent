from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.user import User, UserProfile
from src.schemas.user import UserCreate, UserLogin

router = APIRouter()


def _hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="username already exists")

    if payload.email:
        existing_email = db.query(User).filter(User.email == payload.email).first()
        if existing_email:
            raise HTTPException(status_code=409, detail="email already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=_hash_password(payload.password),
        status="active",
        register_source="api",
    )
    db.add(user)
    db.flush()

    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(user)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "status": user.status,
        },
    }


@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or user.password_hash != _hash_password(payload.password):
        raise HTTPException(status_code=401, detail="invalid username or password")

    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": user.id,
            "username": user.username,
            "status": user.status,
        },
    }
