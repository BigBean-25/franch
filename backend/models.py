from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Literal
from datetime import datetime, timezone
import uuid

# User Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password: str
    name: str
    role: Literal["super_admin", "franchise_admin", "bakehouse_admin", "merch_admin"]
    franchise_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: Literal["super_admin", "franchise_admin", "bakehouse_admin", "merch_admin"]
    franchise_id: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    role: str
    franchise_id: Optional[str] = None
    is_active: bool
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Franchise Models
class Franchise(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    owner_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    gstin: Optional[str] = None
    credit_limit: float = 100000.0
    used_credit: float = 0.0
    available_credit: float = 100000.0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FranchiseCreate(BaseModel):
    name: str
    owner_name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    gstin: Optional[str] = None

class FranchiseUpdate(BaseModel):
    name: Optional[str] = None
    owner_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gstin: Optional[str] = None
    is_active: Optional[bool] = None

# Category Models
class Category(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: Literal["bakehouse", "merch"]
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CategoryCreate(BaseModel):
    name: str
    type: Literal["bakehouse", "merch"]
    description: Optional[str] = None

# Product Models
class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category_id: str
    category_type: Literal["bakehouse", "merch"]
    description: Optional[str] = None
    original_price: float
    offer_price: Optional[float] = None
    gst_percent: float = 18.0
    sgst_percent: float = 9.0  # Half of GST
    cgst_percent: float = 9.0  # Half of GST
    unit: str = "piece"
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    name: str
    category_id: str
    category_type: Literal["bakehouse", "merch"]
    description: Optional[str] = None
    original_price: float
    offer_price: Optional[float] = None
    gst_percent: float = 18.0
    unit: str = "piece"
    image_url: Optional[str] = None

# Cart Models
class CartItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    franchise_id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    gst_percent: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int

# Order Models
class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    gst_percent: float
    sgst_percent: float
    cgst_percent: float
    taxable_amount: float
    sgst_amount: float
    cgst_amount: float
    gst_amount: float
    total_amount: float

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: str
    franchise_id: str
    franchise_name: str
    user_id: str
    order_type: Literal["bakehouse", "merch"]
    items: List[OrderItem]
    subtotal: float
    gst_total: float
    grand_total: float
    status: Literal["pending", "approved", "rejected", "completed", "cancelled"] = "pending"
    remarks: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_url: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(BaseModel):
    order_type: Literal["bakehouse", "merch"]
    remarks: Optional[str] = None

# Payment Models
class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payment_id: str
    franchise_id: str
    franchise_name: str
    amount: float
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    status: Literal["pending", "success", "failed"] = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paid_at: Optional[datetime] = None

class PaymentCreate(BaseModel):
    amount: float

# Credit Ledger Models
class CreditLedger(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    franchise_id: str
    transaction_type: Literal["order_placed", "order_approved", "order_rejected", "payment_made", "credit_reset"]
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    amount: float
    credit_before: float
    credit_after: float
    remarks: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Invoice Models
class Invoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    order_id: str
    franchise_id: str
    franchise_name: str
    invoice_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    invoice_url: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Notification Log Models
class NotificationLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal["email", "whatsapp"]
    recipient: str
    subject: Optional[str] = None
    message: str
    status: Literal["pending", "sent", "failed"] = "pending"
    retry_count: int = 0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sent_at: Optional[datetime] = None

# Audit Log Models
class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: str
    action: str
    module: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Settings Models
class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str = "BigBeanCafe"
    company_address: str
    company_phone: str
    company_email: str
    company_gstin: str
    logo_url: Optional[str] = None
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    email_enabled: bool = False
    whatsapp_enabled: bool = False
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
