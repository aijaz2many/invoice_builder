from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .core.database import Base

class User(Base):
    __tablename__ = "epay_users"

    userId = Column(Integer, primary_key=True, index=True)
    fullName = Column(String, nullable=False)
    emailId= Column(String, unique=True, index=True, nullable=False)
    phoneNumber = Column(String, nullable=False)
    hashPassword = Column(String, nullable=False)
    algoPassword = Column(String, nullable=False)
    isActive = Column(Boolean, default=True)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())
    lastLoginOn = Column(DateTime(timezone=True), server_default=func.now())

class Role(Base):
    __tablename__ = "epay_roles"

    roleId = Column(Integer, primary_key=True)
    roleName = Column(String(50), unique=True, nullable=False)


class UserRole(Base):
    __tablename__ = "epay_user_roles"

    userRoleId = Column(Integer, primary_key=True)
    userId = Column(Integer, ForeignKey("epay_users.userId"), nullable=False)
    roleId = Column(Integer, ForeignKey("epay_roles.roleId"), nullable=False)

    __table_args__ = (
        UniqueConstraint("userId", "roleId", name="ux_user_role"),
    )

class BusinessType(Base):
    __tablename__ = "epay_business_types"

    businessTypeId = Column(Integer, primary_key=True)
    businessTypeName = Column(String(50), unique=True, nullable=False)
    isActive = Column(Boolean, default=True)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())

class Business(Base):
    __tablename__ = "epay_business"

    businessId = Column(Integer, primary_key=True)
    businessName = Column(String(100), unique=True, nullable=False)
    businessTypeId = Column(Integer, ForeignKey("epay_business_types.businessTypeId"), nullable=False)
    userId = Column(Integer, ForeignKey("epay_users.userId"), nullable=False)
    businessLogo = Column(String, nullable=True)
    businessAddress = Column(String, nullable=True)
    businessCity = Column(String, nullable=True)
    businessState = Column(String, nullable=True)
    businessCountry = Column(String, nullable=True)
    businessZip = Column(String, nullable=True)
    businessPhone = Column(String, nullable=True)
    businessEmail = Column(String, nullable=True)
    businessWebsite = Column(String, nullable=True)
    isActive = Column(Boolean, default=True)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())
    lastLoginOn = Column(DateTime(timezone=True), server_default=func.now())