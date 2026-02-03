from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

# Import database
from database import get_db, init_db
from sql_models import (
    User as SQLUser, Franchise as SQLFranchise, Category as SQLCategory,
    Product as SQLProduct, CartItem as SQLCartItem, Order as SQLOrder,
    Payment as SQLPayment, CreditLedger as SQLCreditLedger, Invoice as SQLInvoice,
    NotificationLog as SQLNotificationLog, AuditLog as SQLAuditLog, Settings as SQLSettings
)

# Import models (Pydantic models for API)
from models import (
    User, UserCreate, UserResponse, LoginRequest, LoginResponse,
    Franchise, FranchiseCreate, FranchiseUpdate,
    Category, CategoryCreate,
    Product, ProductCreate,
    CartItem, CartItemCreate,
    Order, OrderCreate, OrderItem,
    Payment, PaymentCreate,
    CreditLedger, Invoice, NotificationLog, AuditLog, Settings
)

# Import auth
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, require_role
)

# Import utils
from utils.notifications import (
    notify_order_placed, notify_order_approved, notify_order_rejected,
    notify_credit_exhausted, notify_payment_success
)
from utils.audit_mysql import log_audit_mysql
from utils.invoice_generator import generate_invoice_pdf, get_next_invoice_number

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="BigBeanCafe Franchise Ordering System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# Authentication Routes
# ============================================

@api_router.post("/auth/register", response_model=UserResponse, tags=["Auth"])
async def register(
    user_data: UserCreate, 
    current_user: dict = Depends(require_role("super_admin")),
    db: AsyncSession = Depends(get_db)
):
    """Register a new user (Super Admin only)"""
    
    # Check if user exists
    result = await db.execute(select(SQLUser).where(SQLUser.email == user_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = SQLUser(
        email=user_data.email,
        password=hashed_password,
        name=user_data.name,
        role=user_data.role,
        franchise_id=user_data.franchise_id
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Audit log
    await log_audit_mysql(db, current_user["id"], current_user["email"], "CREATE_USER", "users", f"Created user {user.email}")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        franchise_id=user.franchise_id,
        is_active=user.is_active,
        created_at=user.created_at
    )

@api_router.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login endpoint"""
    
    # Find user
    result = await db.execute(select(SQLUser).where(SQLUser.email == credentials.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Create token
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "franchise_id": user.franchise_id
    }
    access_token = create_access_token(token_data)
    
    # Audit log
    await log_audit_mysql(db, user.id, user.email, "LOGIN", "auth", "User logged in")
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        franchise_id=user.franchise_id,
        is_active=user.is_active,
        created_at=user.created_at
    )
    return LoginResponse(access_token=access_token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get current user info"""
    result = await db.execute(select(SQLUser).where(SQLUser.id == current_user["id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        franchise_id=user.franchise_id,
        is_active=user.is_active,
        created_at=user.created_at
    )

# ============================================
# User Management Routes (Super Admin)
# ============================================

@api_router.get("/users", response_model=List[UserResponse], tags=["Users"])
async def list_users(
    current_user: dict = Depends(require_role("super_admin")),
    db: AsyncSession = Depends(get_db)
):
    """List all users"""
    result = await db.execute(select(SQLUser))
    users = result.scalars().all()
    
    return [UserResponse(
        id=u.id,
        email=u.email,
        name=u.name,
        role=u.role,
        franchise_id=u.franchise_id,
        is_active=u.is_active,
        created_at=u.created_at
    ) for u in users]

@api_router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(
    user_id: str, 
    current_user: dict = Depends(require_role("super_admin")),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID"""
    result = await db.execute(select(SQLUser).where(SQLUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        franchise_id=user.franchise_id,
        is_active=user.is_active,
        created_at=user.created_at
    )

# ============================================
# Franchise Routes
# ============================================

@api_router.get("/franchises", response_model=List[Franchise], tags=["Franchises"])
async def list_franchises(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all franchises"""
    result = await db.execute(select(SQLFranchise))
    franchises = result.scalars().all()
    
    return [Franchise(
        id=f.id,
        name=f.name,
        owner_name=f.owner_name,
        email=f.email,
        phone=f.phone,
        address=f.address,
        city=f.city,
        state=f.state,
        pincode=f.pincode,
        gstin=f.gstin,
        credit_limit=f.credit_limit,
        used_credit=f.used_credit,
        available_credit=f.available_credit,
        is_active=f.is_active,
        created_at=f.created_at
    ) for f in franchises]

@api_router.post("/franchises", response_model=Franchise, tags=["Franchises"])
async def create_franchise(
    franchise_data: FranchiseCreate, 
    current_user: dict = Depends(require_role("super_admin")),
    db: AsyncSession = Depends(get_db)
):
    """Create new franchise"""
    franchise = SQLFranchise(**franchise_data.model_dump())
    
    db.add(franchise)
    await db.commit()
    await db.refresh(franchise)
    
    await log_audit_mysql(db, current_user["id"], current_user["email"], "CREATE_FRANCHISE", "franchises", f"Created franchise {franchise.name}")
    
    return Franchise(
        id=franchise.id,
        name=franchise.name,
        owner_name=franchise.owner_name,
        email=franchise.email,
        phone=franchise.phone,
        address=franchise.address,
        city=franchise.city,
        state=franchise.state,
        pincode=franchise.pincode,
        gstin=franchise.gstin,
        credit_limit=franchise.credit_limit,
        used_credit=franchise.used_credit,
        available_credit=franchise.available_credit,
        is_active=franchise.is_active,
        created_at=franchise.created_at
    )

# ============================================
# Category Routes
# ============================================

@api_router.get("/categories", response_model=List[Category], tags=["Categories"])
async def list_categories(
    type: Optional[str] = None, 
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List categories"""
    query = select(SQLCategory)
    if type:
        query = query.where(SQLCategory.type == type)
    
    result = await db.execute(query)
    categories = result.scalars().all()
    
    return [Category(
        id=c.id,
        name=c.name,
        type=c.type,
        description=c.description,
        is_active=c.is_active,
        created_at=c.created_at
    ) for c in categories]

@api_router.post("/categories", response_model=Category, tags=["Categories"])
async def create_category(
    category_data: CategoryCreate,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin")),
    db: AsyncSession = Depends(get_db)
):
    """Create category"""
    # Check permission based on type
    if current_user["role"] == "bakehouse_admin" and category_data.type != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only create bakehouse categories")
    if current_user["role"] == "merch_admin" and category_data.type != "merch":
        raise HTTPException(status_code=403, detail="Can only create merch categories")
    
    category = SQLCategory(**category_data.model_dump())
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    await log_audit_mysql(db, current_user["id"], current_user["email"], "CREATE_CATEGORY", "categories", f"Created category {category.name}")
    
    return Category(
        id=category.id,
        name=category.name,
        type=category.type,
        description=category.description,
        is_active=category.is_active,
        created_at=category.created_at
    )

# ============================================
# Product Routes
# ============================================

@api_router.get("/products", response_model=List[Product], tags=["Products"])
async def list_products(
    category_id: Optional[str] = None,
    category_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List products"""
    query = select(SQLProduct).where(SQLProduct.is_active == True)
    if category_id:
        query = query.where(SQLProduct.category_id == category_id)
    if category_type:
        query = query.where(SQLProduct.category_type == category_type)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return [Product(
        id=p.id,
        name=p.name,
        category_id=p.category_id,
        category_type=p.category_type,
        description=p.description,
        original_price=p.original_price,
        offer_price=p.offer_price,
        gst_percent=p.gst_percent,
        unit=p.unit,
        is_active=p.is_active,
        created_at=p.created_at
    ) for p in products]

@api_router.post("/products", response_model=Product, tags=["Products"])
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin")),
    db: AsyncSession = Depends(get_db)
):
    """Create product"""
    # Check permission
    if current_user["role"] == "bakehouse_admin" and product_data.category_type != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only create bakehouse products")
    if current_user["role"] == "merch_admin" and product_data.category_type != "merch":
        raise HTTPException(status_code=403, detail="Can only create merch products")
    
    product = SQLProduct(**product_data.model_dump())
    
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    await log_audit_mysql(db, current_user["id"], current_user["email"], "CREATE_PRODUCT", "products", f"Created product {product.name}")
    
    return Product(
        id=product.id,
        name=product.name,
        category_id=product.category_id,
        category_type=product.category_type,
        description=product.description,
        original_price=product.original_price,
        offer_price=product.offer_price,
        gst_percent=product.gst_percent,
        unit=product.unit,
        is_active=product.is_active,
        created_at=product.created_at
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    logger.info("Database initialized")

@app.get("/")
async def root():
    return {"message": "BigBeanCafe Franchise Ordering System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
