from uuid import UUID
from pydantic import BaseModel, Field
from typing import List


class UserSignup(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
    
    

# Schema for images
class FaceImages(BaseModel):
    images: List[str]


class Login(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserAuth(BaseModel):
    email: str = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class UserOut(BaseModel):
    id: UUID
    email: str


class SystemUser(UserOut):
    password: str


class UpdatePassword(BaseModel):
    email: str
    old_password: str
    new_password: str


class ForgotPassword(BaseModel):
    email: str


class ResetPassword(BaseModel):
    email: str
    otp: str
    password: str
