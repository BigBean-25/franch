from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid

Base = declarative_base()

def generate_id():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # super_admin, franchise_admin, bakehouse_admin, merch_admin
    franchise_id = Column(String(36), ForeignKey("franchises.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    franchise = relationship("Franchise", back_populates="users")
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")

class Franchise(Base):
    __tablename__ = "franchises"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    name = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    gstin = Column(String(15), nullable=True)
    credit_limit = Column(Float, default=50000.0)
    used_credit = Column(Float, default=0.0)
    available_credit = Column(Float, default=50000.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    users = relationship("User", back_populates="franchise")
    orders = relationship("Order", back_populates="franchise")
    cart_items = relationship("CartItem", back_populates="franchise")
    credit_ledger = relationship("CreditLedger", back_populates="franchise")
    invoices = relationship("Invoice", back_populates="franchise")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # bakehouse, merch
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    name = Column(String(255), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False)
    category_type = Column(String(50), nullable=False)  # bakehouse, merch
    description = Column(Text, nullable=True)
    original_price = Column(Float, nullable=False)
    offer_price = Column(Float, nullable=True)
    gst_percent = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # piece, kg, pack, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    franchise_id = Column(String(36), ForeignKey("franchises.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    gst_percent = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    franchise = relationship("Franchise", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    franchise_id = Column(String(36), ForeignKey("franchises.id"), nullable=False)
    franchise_name = Column(String(255), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    order_type = Column(String(50), nullable=False)  # bakehouse, merch
    items = Column(JSON, nullable=False)  # Store order items as JSON
    subtotal = Column(Float, nullable=False)
    sgst_total = Column(Float, nullable=False)
    cgst_total = Column(Float, nullable=False)
    gst_total = Column(Float, nullable=False)
    grand_total = Column(Float, nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    remarks = Column(Text, nullable=True)
    invoice_number = Column(String(50), nullable=True)
    invoice_url = Column(String(500), nullable=True)
    approved_by = Column(String(36), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    franchise = relationship("Franchise", back_populates="orders")
    user = relationship("User", back_populates="orders")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    franchise_id = Column(String(36), ForeignKey("franchises.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # razorpay, stripe, bank_transfer
    payment_id = Column(String(255), nullable=True)  # External payment ID
    status = Column(String(50), default="pending")  # pending, success, failed
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CreditLedger(Base):
    __tablename__ = "credit_ledger"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    franchise_id = Column(String(36), ForeignKey("franchises.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # order_approved, payment_received, credit_adjustment
    order_id = Column(String(36), nullable=True)
    payment_id = Column(String(36), nullable=True)
    amount = Column(Float, nullable=False)
    credit_before = Column(Float, nullable=False)
    credit_after = Column(Float, nullable=False)
    remarks = Column(Text, nullable=True)
    created_by = Column(String(36), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    franchise = relationship("Franchise", back_populates="credit_ledger")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(String(36), nullable=False)
    franchise_id = Column(String(36), ForeignKey("franchises.id"), nullable=False)
    franchise_name = Column(String(255), nullable=False)
    invoice_url = Column(String(500), nullable=False)
    invoice_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    franchise = relationship("Franchise", back_populates="invoices")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    recipient_email = Column(String(255), nullable=False)
    recipient_phone = Column(String(20), nullable=True)
    notification_type = Column(String(50), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="sent")  # sent, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    user_id = Column(String(36), nullable=False)
    user_email = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(36), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(String(36), primary_key=True, default=generate_id)
    company_name = Column(String(255), default="BigBeanCafe")
    company_address = Column(Text, default="Franchise Head Office, Koramangala, Bangalore - 560034")
    company_phone = Column(String(20), default="+91 80 1234 5678")
    company_email = Column(String(255), default="info@bigbeancafe.in")
    company_gstin = Column(String(15), default="29AAAAA0000A1Z5")
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
