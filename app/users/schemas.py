from pydantic import BaseModel, EmailStr

from app.users.models import Roles


class SUsersRegister(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str
    role: Roles

    class Config:
        from_attributes = True


class SUsersLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class SUsersResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
