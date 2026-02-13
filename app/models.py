from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Text
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


class Customer(Base):
    __tablename__ = "epay_customers"

    customerId = Column(Integer, primary_key=True)
    businessId = Column(Integer, ForeignKey("epay_business.businessId"), nullable=False)
    customerName = Column(String(100), nullable=False)
    customerPhone = Column(String, nullable=False)
    customerFullAddress = Column(String, nullable=False)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())


class Invoice(Base):
    __tablename__ = "epay_invoices"

    invoiceId = Column(Integer, primary_key=True)
    businessId = Column(Integer, ForeignKey("epay_business.businessId"), nullable=False)
    customerId = Column(Integer, ForeignKey("epay_customers.customerId"), nullable=False)
    invoiceNumber = Column(String, nullable=False)
    invoiceDate = Column(DateTime(timezone=True), server_default=func.now())
    invoiceAmount = Column(Integer, nullable=False)
    amountInWords = Column(String, nullable=False)
    paymentMode = Column(String, nullable=False)
    paymentType = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    pdfURL = Column(Text, nullable=True)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())
    
class SubscriptionPlan(Base):
    __tablename__ = "epay_subscription_plans"

    subscriptionPlanId = Column(Integer, primary_key=True)
    subscriptionPlanName = Column(String, nullable=False)
    subscriptionPlanDescription = Column(String, nullable=False)
    subscriptionPlanPrice = Column(Integer, nullable=False)
    subscriptionPlanDuration = Column(Integer, nullable=False)
    subscriptionPlanStatus = Column(Boolean, default=True)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())

class Subscription(Base):
    __tablename__ = "epay_subscriptions"

    subscriptionId = Column(Integer, primary_key=True)
    businessId = Column(Integer, ForeignKey("epay_business.businessId"), nullable=False, unique=True)
    subscriptionPlanId = Column(Integer, ForeignKey("epay_subscription_plans.subscriptionPlanId"), nullable=False)
    subscriptionStatus = Column(Boolean, default=True)
    subscriptionStartDate = Column(DateTime(timezone=True), server_default=func.now())
    subscriptionEndDate = Column(DateTime(timezone=True), server_default=func.now())
    autoRenew = Column(Boolean, default=True)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())
    
class SubscriptionPayment(Base):
    __tablename__ = "epay_subscription_payments"

    subscriptionPaymentId = Column(Integer, primary_key=True)
    subscriptionId = Column(Integer, ForeignKey("epay_subscriptions.subscriptionId"), nullable=False)
    paymentStatus = Column(Boolean, default=True)
    paymentDate = Column(DateTime(timezone=True), server_default=func.now())
    paymentAmount = Column(Integer, nullable=False)
    paymentMode = Column(String, nullable=False)
    paymentType = Column(String, nullable=False)
    paymentPurpose = Column(String, nullable=False)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())

class SubscriptionUsage(Base):
    __tablename__ = "epay_subscription_usages"

    subscriptionUsageId = Column(Integer, primary_key=True)
    subscriptionId = Column(Integer, ForeignKey("epay_subscriptions.subscriptionId"), nullable=False)
    usageMonth = Column(String(7), nullable=False)
    invoiceCount  = Column(Integer, nullable=False)
    createdOn = Column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        UniqueConstraint("subscriptionId", "usageMonth", name="ux_subscription_usage"),
    )
   