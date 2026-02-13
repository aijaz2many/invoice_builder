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

# Business Type Schemas
class BusinessTypeBase(BaseModel):
    businessTypeName: str
    isActive: bool = True

class BusinessTypeCreate(BusinessTypeBase):
    pass

class BusinessTypeResponse(BusinessTypeBase):
    businessTypeId: int
    createdOn: datetime
    
    class Config:
        from_attributes = True

# Business Schemas
class BusinessBase(BaseModel):
    businessName: str
    businessTypeId: int
    userId: int
    businessLogo: Optional[str] = None
    businessAddress: Optional[str] = None
    businessCity: Optional[str] = None
    businessState: Optional[str] = None
    businessCountry: Optional[str] = None
    businessZip: Optional[str] = None
    businessPhone: Optional[str] = None
    businessEmail: Optional[str] = None
    businessWebsite: Optional[str] = None
    isActive: bool = True

class BusinessCreate(BusinessBase):
    pass

class BusinessResponse(BusinessBase):
    businessId: int
    createdOn: datetime
    lastLoginOn: datetime
    
    class Config:
        from_attributes = True
