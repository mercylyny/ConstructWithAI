from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    is_google_user: bool
    created_at: datetime

    class Config:
        from_attributes = True

class GoogleLoginRequest(BaseModel):
    email: str
    name: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: str
    via: str = "email"  # "email" or "sms"
    phone: Optional[str] = None

class PasswordResetConfirm(BaseModel):
    email: str
    token: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
