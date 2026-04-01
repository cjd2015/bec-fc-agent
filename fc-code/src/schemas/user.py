from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserProfileUpdate(BaseModel):
    target_level: Optional[str] = None
    current_level: Optional[str] = None
    industry_background: Optional[str] = None
    learning_goal: Optional[str] = None
    learning_preference: Optional[str] = None
