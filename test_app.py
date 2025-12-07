from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    """User model"""
    id: Optional[int] = None
    first_name: str
    last_name: str
    email: EmailStr
    created_at: Optional[datetime] = datetime.now()

    class Config:
        orm_mode = True

class Event(BaseModel):
    """Event model"""
    id: Optional[int] = None
    name: str
    date: datetime
    location: str
    creator_id: int

    class Config:
        orm_mode = True

class Booking(BaseModel):
    """Booking model"""
    id: Optional[int] = None
    user_id: int
    event_id: int
    created_at: Optional[datetime] = datetime.now()

    class Config:
        orm_mode = True