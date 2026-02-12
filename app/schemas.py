from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    emailId: EmailStr
    fullName: Optional[str] = None
    phoneNumber: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    emailId: Optional[EmailStr] = None
    fullName: Optional[str] = None
    phoneNumber: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    emailId: EmailStr
    password: str

class UserResponse(UserBase):
    userId: int
    isActive: bool
    createdOn: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    emailId: Optional[str] = None

class RoleBase(BaseModel):
    roleName: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    roleId: int
    
    class Config:
        from_attributes = True

class UserRoleBase(BaseModel):
    userId: int
    roleId: int

class UserRoleResponse(UserRoleBase):
    userRoleId: int

    class Config:
        from_attributes = True

class ForgotPassword(BaseModel):
    emailId: EmailStr

class ResetPassword(BaseModel):
    emailId: EmailStr
    currentPassword: str
    newPassword: str
