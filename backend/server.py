from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

# Import models
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
from utils.audit import log_audit
from utils.invoice_generator import generate_invoice_pdf, get_next_invoice_number

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'bigbeancafe_db')]

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
async def register(user_data: UserCreate, current_user: dict = Depends(require_role("super_admin"))):
    """Register a new user (Super Admin only)"""
    
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        password=hashed_password,
        name=user_data.name,
        role=user_data.role,
        franchise_id=user_data.franchise_id
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.insert_one(doc)
    
    # Audit log
    await log_audit(db, current_user["id"], current_user["email"], "CREATE_USER", "users", f"Created user {user.email}")
    
    return UserResponse(**user.model_dump())

@api_router.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
async def login(credentials: LoginRequest):
    """Login endpoint"""
    
    # Find user
    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if active
    if not user_doc.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    # Create token
    token_data = {
        "sub": user_doc["id"],
        "email": user_doc["email"],
        "role": user_doc["role"],
        "franchise_id": user_doc.get("franchise_id")
    }
    access_token = create_access_token(token_data)
    
    # Audit log
    await log_audit(db, user_doc["id"], user_doc["email"], "LOGIN", "auth", "User logged in")
    
    user_response = UserResponse(**user_doc)
    return LoginResponse(access_token=access_token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    user_doc = await db.users.find_one({"id": current_user["id"]})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user_doc)

# ============================================
# User Management Routes (Super Admin)
# ============================================

@api_router.get("/users", response_model=List[UserResponse], tags=["Users"])
async def list_users(current_user: dict = Depends(require_role("super_admin"))):
    """List all users"""
    users = await db.users.find({}, {"_id": 0}).to_list(1000)
    return [UserResponse(**u) for u in users]

@api_router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: str, current_user: dict = Depends(require_role("super_admin"))):
    """Get user by ID"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)

@api_router.put("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def update_user(user_id: str, updates: dict, current_user: dict = Depends(require_role("super_admin"))):
    """Update user"""
    result = await db.users.update_one({"id": user_id}, {"$set": updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    await log_audit(db, current_user["id"], current_user["email"], "UPDATE_USER", "users", f"Updated user {user_id}")
    return UserResponse(**user)

@api_router.delete("/users/{user_id}", tags=["Users"])
async def delete_user(user_id: str, current_user: dict = Depends(require_role("super_admin"))):
    """Delete user"""
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    await log_audit(db, current_user["id"], current_user["email"], "DELETE_USER", "users", f"Deleted user {user_id}")
    return {"message": "User deleted"}

# ============================================
# Franchise Routes
# ============================================

@api_router.get("/franchises", response_model=List[Franchise], tags=["Franchises"])
async def list_franchises(current_user: dict = Depends(get_current_user)):
    """List all franchises"""
    franchises = await db.franchises.find({}, {"_id": 0}).to_list(1000)
    return [Franchise(**f) for f in franchises]

@api_router.post("/franchises", response_model=Franchise, tags=["Franchises"])
async def create_franchise(franchise_data: FranchiseCreate, current_user: dict = Depends(require_role("super_admin"))):
    """Create new franchise"""
    franchise = Franchise(**franchise_data.model_dump())
    
    doc = franchise.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.franchises.insert_one(doc)
    await log_audit(db, current_user["id"], current_user["email"], "CREATE_FRANCHISE", "franchises", f"Created franchise {franchise.name}")
    
    return franchise

@api_router.get("/franchises/{franchise_id}", response_model=Franchise, tags=["Franchises"])
async def get_franchise(franchise_id: str, current_user: dict = Depends(get_current_user)):
    """Get franchise by ID"""
    franchise = await db.franchises.find_one({"id": franchise_id}, {"_id": 0})
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    return Franchise(**franchise)

@api_router.put("/franchises/{franchise_id}", response_model=Franchise, tags=["Franchises"])
async def update_franchise(franchise_id: str, updates: FranchiseUpdate, current_user: dict = Depends(require_role("super_admin"))):
    """Update franchise"""
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    result = await db.franchises.update_one({"id": franchise_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Franchise not found")
    
    franchise = await db.franchises.find_one({"id": franchise_id}, {"_id": 0})
    await log_audit(db, current_user["id"], current_user["email"], "UPDATE_FRANCHISE", "franchises", f"Updated franchise {franchise_id}")
    
    return Franchise(**franchise)

@api_router.delete("/franchises/{franchise_id}", tags=["Franchises"])
async def delete_franchise(franchise_id: str, current_user: dict = Depends(require_role("super_admin"))):
    """Delete franchise"""
    result = await db.franchises.delete_one({"id": franchise_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Franchise not found")
    
    await log_audit(db, current_user["id"], current_user["email"], "DELETE_FRANCHISE", "franchises", f"Deleted franchise {franchise_id}")
    return {"message": "Franchise deleted"}

# ============================================
# Category Routes
# ============================================

@api_router.get("/categories", response_model=List[Category], tags=["Categories"])
async def list_categories(type: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """List categories"""
    query = {}
    if type:
        query["type"] = type
    
    categories = await db.categories.find(query, {"_id": 0}).to_list(1000)
    return [Category(**c) for c in categories]

@api_router.post("/categories", response_model=Category, tags=["Categories"])
async def create_category(
    category_data: CategoryCreate,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin"))
):
    """Create category"""
    # Check permission based on type
    if current_user["role"] == "bakehouse_admin" and category_data.type != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only create bakehouse categories")
    if current_user["role"] == "merch_admin" and category_data.type != "merch":
        raise HTTPException(status_code=403, detail="Can only create merch categories")
    
    category = Category(**category_data.model_dump())
    
    doc = category.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.categories.insert_one(doc)
    await log_audit(db, current_user["id"], current_user["email"], "CREATE_CATEGORY", "categories", f"Created category {category.name}")
    
    return category

@api_router.put("/categories/{category_id}", response_model=Category, tags=["Categories"])
async def update_category(
    category_id: str,
    updates: dict,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin"))
):
    """Update category"""
    category = await db.categories.find_one({"id": category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check permission
    if current_user["role"] == "bakehouse_admin" and category["type"] != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only update bakehouse categories")
    if current_user["role"] == "merch_admin" and category["type"] != "merch":
        raise HTTPException(status_code=403, detail="Can only update merch categories")
    
    await db.categories.update_one({"id": category_id}, {"$set": updates})
    category = await db.categories.find_one({"id": category_id}, {"_id": 0})
    await log_audit(db, current_user["id"], current_user["email"], "UPDATE_CATEGORY", "categories", f"Updated category {category_id}")
    
    return Category(**category)

@api_router.delete("/categories/{category_id}", tags=["Categories"])
async def delete_category(
    category_id: str,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin"))
):
    """Delete category"""
    category = await db.categories.find_one({"id": category_id})
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check permission
    if current_user["role"] == "bakehouse_admin" and category["type"] != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only delete bakehouse categories")
    if current_user["role"] == "merch_admin" and category["type"] != "merch":
        raise HTTPException(status_code=403, detail="Can only delete merch categories")
    
    await db.categories.delete_one({"id": category_id})
    await log_audit(db, current_user["id"], current_user["email"], "DELETE_CATEGORY", "categories", f"Deleted category {category_id}")
    
    return {"message": "Category deleted"}

# ============================================
# Product Routes
# ============================================

@api_router.get("/products", response_model=List[Product], tags=["Products"])
async def list_products(
    category_id: Optional[str] = None,
    category_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List products"""
    query = {"is_active": True}
    if category_id:
        query["category_id"] = category_id
    if category_type:
        query["category_type"] = category_type
    
    products = await db.products.find(query, {"_id": 0}).to_list(1000)
    return [Product(**p) for p in products]

@api_router.post("/products", response_model=Product, tags=["Products"])
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin"))
):
    """Create product"""
    # Check permission
    if current_user["role"] == "bakehouse_admin" and product_data.category_type != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only create bakehouse products")
    if current_user["role"] == "merch_admin" and product_data.category_type != "merch":
        raise HTTPException(status_code=403, detail="Can only create merch products")
    
    product = Product(**product_data.model_dump())
    
    doc = product.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.products.insert_one(doc)
    await log_audit(db, current_user["id"], current_user["email"], "CREATE_PRODUCT", "products", f"Created product {product.name}")
    
    return product

@api_router.get("/products/{product_id}", response_model=Product, tags=["Products"])
async def get_product(product_id: str, current_user: dict = Depends(get_current_user)):
    """Get product by ID"""
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.put("/products/{product_id}", response_model=Product, tags=["Products"])
async def update_product(
    product_id: str,
    updates: dict,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin"))
):
    """Update product"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check permission
    if current_user["role"] == "bakehouse_admin" and product["category_type"] != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only update bakehouse products")
    if current_user["role"] == "merch_admin" and product["category_type"] != "merch":
        raise HTTPException(status_code=403, detail="Can only update merch products")
    
    await db.products.update_one({"id": product_id}, {"$set": updates})
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    await log_audit(db, current_user["id"], current_user["email"], "UPDATE_PRODUCT", "products", f"Updated product {product_id}")
    
    return Product(**product)

@api_router.delete("/products/{product_id}", tags=["Products"])
async def delete_product(
    product_id: str,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin"))
):
    """Delete product"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check permission
    if current_user["role"] == "bakehouse_admin" and product["category_type"] != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only delete bakehouse products")
    if current_user["role"] == "merch_admin" and product["category_type"] != "merch":
        raise HTTPException(status_code=403, detail="Can only delete merch products")
    
    await db.products.delete_one({"id": product_id})
    await log_audit(db, current_user["id"], current_user["email"], "DELETE_PRODUCT", "products", f"Deleted product {product_id}")
    
    return {"message": "Product deleted"}

# ============================================
# Cart Routes (Franchise only)
# ============================================

@api_router.get("/cart", response_model=List[CartItem], tags=["Cart"])
async def get_cart(current_user: dict = Depends(require_role("franchise_admin"))):
    """Get cart items"""
    items = await db.cart_items.find({"user_id": current_user["id"]}, {"_id": 0}).to_list(100)
    return [CartItem(**item) for item in items]

@api_router.post("/cart", response_model=CartItem, tags=["Cart"])
async def add_to_cart(item_data: CartItemCreate, current_user: dict = Depends(require_role("franchise_admin"))):
    """Add item to cart"""
    # Get product
    product = await db.products.find_one({"id": item_data.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if item already in cart
    existing = await db.cart_items.find_one({
        "user_id": current_user["id"],
        "product_id": item_data.product_id
    })
    
    if existing:
        # Update quantity
        new_qty = existing["quantity"] + item_data.quantity
        await db.cart_items.update_one(
            {"id": existing["id"]},
            {"$set": {"quantity": new_qty}}
        )
        cart_item = await db.cart_items.find_one({"id": existing["id"]}, {"_id": 0})
    else:
        # Create new cart item
        unit_price = product.get("offer_price") or product["original_price"]
        cart_item_obj = CartItem(
            user_id=current_user["id"],
            franchise_id=current_user["franchise_id"],
            product_id=product["id"],
            product_name=product["name"],
            quantity=item_data.quantity,
            unit_price=unit_price,
            gst_percent=product["gst_percent"]
        )
        
        doc = cart_item_obj.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.cart_items.insert_one(doc)
        cart_item = doc
    
    return CartItem(**cart_item)

@api_router.put("/cart/{item_id}", response_model=CartItem, tags=["Cart"])
async def update_cart_item(item_id: str, quantity: int, current_user: dict = Depends(require_role("franchise_admin"))):
    """Update cart item quantity"""
    if quantity <= 0:
        await db.cart_items.delete_one({"id": item_id, "user_id": current_user["id"]})
        return {"message": "Item removed from cart"}
    
    result = await db.cart_items.update_one(
        {"id": item_id, "user_id": current_user["id"]},
        {"$set": {"quantity": quantity}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    cart_item = await db.cart_items.find_one({"id": item_id}, {"_id": 0})
    return CartItem(**cart_item)

@api_router.delete("/cart/{item_id}", tags=["Cart"])
async def remove_from_cart(item_id: str, current_user: dict = Depends(require_role("franchise_admin"))):
    """Remove item from cart"""
    result = await db.cart_items.delete_one({"id": item_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

@api_router.delete("/cart", tags=["Cart"])
async def clear_cart(current_user: dict = Depends(require_role("franchise_admin"))):
    """Clear cart"""
    await db.cart_items.delete_many({"user_id": current_user["id"]})
    return {"message": "Cart cleared"}

# ============================================
# Order Routes
# ============================================

@api_router.get("/orders", response_model=List[Order], tags=["Orders"])
async def list_orders(
    status_filter: Optional[str] = None,
    order_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List orders"""
    query = {}
    
    # Filter by role
    if current_user["role"] == "franchise_admin":
        query["franchise_id"] = current_user["franchise_id"]
    elif current_user["role"] == "bakehouse_admin":
        query["order_type"] = "bakehouse"
    elif current_user["role"] == "merch_admin":
        query["order_type"] = "merch"
    
    if status_filter:
        query["status"] = status_filter
    if order_type:
        query["order_type"] = order_type
    
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Order(**o) for o in orders]

@api_router.post("/orders", response_model=Order, tags=["Orders"])
async def create_order(order_data: OrderCreate, current_user: dict = Depends(require_role("franchise_admin"))):
    """Create order from cart"""
    # Get franchise
    franchise = await db.franchises.find_one({"id": current_user["franchise_id"]})
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    
    # Get cart items
    cart_items = await db.cart_items.find({
        "user_id": current_user["id"],
        "franchise_id": current_user["franchise_id"]
    }).to_list(100)
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Filter by order type
    filtered_cart = [item for item in cart_items if item.get("product_id")]
    if not filtered_cart:
        raise HTTPException(status_code=400, detail="No items match the order type")
    
    # Calculate order totals
    order_items = []
    subtotal = 0
    gst_total = 0
    
    for cart_item in filtered_cart:
        quantity = cart_item["quantity"]
        unit_price = cart_item["unit_price"]
        gst_percent = cart_item["gst_percent"]
        
        taxable_amount = quantity * unit_price
        gst_amount = taxable_amount * (gst_percent / 100)
        total_amount = taxable_amount + gst_amount
        
        order_item = OrderItem(
            product_id=cart_item["product_id"],
            product_name=cart_item["product_name"],
            quantity=quantity,
            unit_price=unit_price,
            gst_percent=gst_percent,
            taxable_amount=taxable_amount,
            gst_amount=gst_amount,
            total_amount=total_amount
        )
        order_items.append(order_item)
        
        subtotal += taxable_amount
        gst_total += gst_amount
    
    grand_total = subtotal + gst_total
    
    # Check credit availability
    if grand_total > franchise["available_credit"]:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient credit. Available: ₹{franchise['available_credit']:.2f}, Required: ₹{grand_total:.2f}"
        )
    
    # Generate order number
    order_count = await db.orders.count_documents({}) + 1
    order_number = f"BBC-ORD-{datetime.now().year}-{order_count:05d}"
    
    # Create order
    order = Order(
        order_number=order_number,
        franchise_id=franchise["id"],
        franchise_name=franchise["name"],
        user_id=current_user["id"],
        order_type=order_data.order_type,
        items=[item.model_dump() for item in order_items],
        subtotal=subtotal,
        gst_total=gst_total,
        grand_total=grand_total,
        remarks=order_data.remarks
    )
    
    doc = order.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.orders.insert_one(doc)
    
    # Clear cart items
    await db.cart_items.delete_many({"user_id": current_user["id"]})
    
    # Send notification
    await notify_order_placed(db, doc, franchise["email"])
    
    # Audit log
    await log_audit(db, current_user["id"], current_user["email"], "CREATE_ORDER", "orders", f"Created order {order_number}")
    
    return order

@api_router.get("/orders/{order_id}", response_model=Order, tags=["Orders"])
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get order by ID"""
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permission
    if current_user["role"] == "franchise_admin" and order["franchise_id"] != current_user["franchise_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return Order(**order)

@api_router.post("/orders/{order_id}/approve", response_model=Order, tags=["Orders"])
async def approve_order(
    order_id: str,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin"))
):
    """Approve order"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permission
    if current_user["role"] == "bakehouse_admin" and order["order_type"] != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only approve bakehouse orders")
    if current_user["role"] == "merch_admin" and order["order_type"] != "merch":
        raise HTTPException(status_code=403, detail="Can only approve merch orders")
    
    if order["status"] != "pending":
        raise HTTPException(status_code=400, detail="Order is not pending")
    
    # Get franchise
    franchise = await db.franchises.find_one({"id": order["franchise_id"]})
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    
    # Deduct credit
    new_used_credit = franchise["used_credit"] + order["grand_total"]
    new_available_credit = franchise["credit_limit"] - new_used_credit
    
    await db.franchises.update_one(
        {"id": franchise["id"]},
        {
            "$set": {
                "used_credit": new_used_credit,
                "available_credit": new_available_credit
            }
        }
    )
    
    # Generate invoice
    year = datetime.now().year
    invoice_number = get_next_invoice_number(year)
    
    invoice_data = {
        "invoice_number": invoice_number,
        "order_id": order["id"],
        "franchise_name": franchise["name"],
        "franchise_address": f"{franchise['address']}, {franchise['city']}, {franchise['state']} - {franchise['pincode']}",
        "franchise_gstin": franchise.get("gstin"),
        "items": order["items"],
        "subtotal": order["subtotal"],
        "gst_total": order["gst_total"],
        "grand_total": order["grand_total"],
        "invoice_date": datetime.now(timezone.utc)
    }
    
    company_settings = await db.settings.find_one({})
    if not company_settings:
        company_settings = {
            "company_name": "BigBeanCafe",
            "company_address": "Franchise Head Office, India",
            "company_phone": "+91 1234567890",
            "company_gstin": "22AAAAA0000A1Z5"
        }
    
    invoice_path = generate_invoice_pdf(invoice_data, company_settings)
    invoice_url = f"/api/invoices/{invoice_number}.pdf"
    
    # Save invoice record
    invoice = Invoice(
        invoice_number=invoice_number,
        order_id=order["id"],
        franchise_id=franchise["id"],
        franchise_name=franchise["name"],
        invoice_url=invoice_url
    )
    
    invoice_doc = invoice.model_dump()
    invoice_doc['invoice_date'] = invoice_doc['invoice_date'].isoformat()
    invoice_doc['created_at'] = invoice_doc['created_at'].isoformat()
    
    await db.invoices.insert_one(invoice_doc)
    
    # Update order
    await db.orders.update_one(
        {"id": order_id},
        {
            "$set": {
                "status": "approved",
                "invoice_number": invoice_number,
                "invoice_url": invoice_url,
                "approved_by": current_user["id"],
                "approved_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Credit ledger entry
    ledger = CreditLedger(
        franchise_id=franchise["id"],
        transaction_type="order_approved",
        order_id=order["id"],
        amount=order["grand_total"],
        credit_before=franchise["used_credit"],
        credit_after=new_used_credit,
        remarks=f"Order {order['order_number']} approved",
        created_by=current_user["id"]
    )
    
    ledger_doc = ledger.model_dump()
    ledger_doc['created_at'] = ledger_doc['created_at'].isoformat()
    
    await db.credit_ledger.insert_one(ledger_doc)
    
    # Check if credit exhausted
    if new_available_credit <= 0:
        await notify_credit_exhausted(db, franchise["name"], franchise["email"])
    
    # Send notification
    order["invoice_number"] = invoice_number
    await notify_order_approved(db, order, franchise["email"])
    
    # Audit log
    await log_audit(db, current_user["id"], current_user["email"], "APPROVE_ORDER", "orders", f"Approved order {order['order_number']}")
    
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    return Order(**order)

@api_router.post("/orders/{order_id}/reject", response_model=Order, tags=["Orders"])
async def reject_order(
    order_id: str,
    remarks: str,
    current_user: dict = Depends(require_role("super_admin", "bakehouse_admin", "merch_admin"))
):
    """Reject order"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permission
    if current_user["role"] == "bakehouse_admin" and order["order_type"] != "bakehouse":
        raise HTTPException(status_code=403, detail="Can only reject bakehouse orders")
    if current_user["role"] == "merch_admin" and order["order_type"] != "merch":
        raise HTTPException(status_code=403, detail="Can only reject merch orders")
    
    if order["status"] != "pending":
        raise HTTPException(status_code=400, detail="Order is not pending")
    
    # Update order
    await db.orders.update_one(
        {"id": order_id},
        {
            "$set": {
                "status": "rejected",
                "remarks": remarks,
                "approved_by": current_user["id"],
                "approved_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Get franchise
    franchise = await db.franchises.find_one({"id": order["franchise_id"]})
    
    # Send notification
    await notify_order_rejected(db, order, franchise["email"], remarks)
    
    # Audit log
    await log_audit(db, current_user["id"], current_user["email"], "REJECT_ORDER", "orders", f"Rejected order {order['order_number']}")
    
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    return Order(**order)

# ============================================
# Payment Routes
# ============================================

@api_router.post("/payments/create-order", tags=["Payments"])
async def create_payment_order(current_user: dict = Depends(require_role("franchise_admin"))):
    """Create Razorpay order for credit reset (₹1,00,000)"""
    import razorpay
    
    # Get settings
    settings = await db.settings.find_one({})
    if not settings or not settings.get("razorpay_key_id"):
        raise HTTPException(status_code=500, detail="Payment gateway not configured")
    
    # Get franchise
    franchise = await db.franchises.find_one({"id": current_user["franchise_id"]})
    if not franchise:
        raise HTTPException(status_code=404, detail="Franchise not found")
    
    # Amount is always ₹1,00,000 (in paise)
    amount = 100000 * 100
    
    # Create Razorpay order
    client = razorpay.Client(auth=(settings["razorpay_key_id"], settings.get("razorpay_key_secret", "")))
    
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })
    
    # Save payment record
    payment = Payment(
        payment_id=razorpay_order["id"],
        franchise_id=franchise["id"],
        franchise_name=franchise["name"],
        amount=100000.0,
        razorpay_order_id=razorpay_order["id"]
    )
    
    doc = payment.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.payments.insert_one(doc)
    
    return {
        "order_id": razorpay_order["id"],
        "amount": amount,
        "currency": "INR",
        "key_id": settings["razorpay_key_id"]
    }

@api_router.post("/payments/verify", tags=["Payments"])
async def verify_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    current_user: dict = Depends(require_role("franchise_admin"))
):
    """Verify Razorpay payment and reset credit"""
    import razorpay
    
    # Get settings
    settings = await db.settings.find_one({})
    if not settings or not settings.get("razorpay_key_id"):
        raise HTTPException(status_code=500, detail="Payment gateway not configured")
    
    # Get payment record
    payment = await db.payments.find_one({"razorpay_order_id": razorpay_order_id})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Verify signature
    client = razorpay.Client(auth=(settings["razorpay_key_id"], settings.get("razorpay_key_secret", "")))
    
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    # Update payment record
    await db.payments.update_one(
        {"id": payment["id"]},
        {
            "$set": {
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
                "status": "success",
                "paid_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    # Get franchise
    franchise = await db.franchises.find_one({"id": payment["franchise_id"]})
    
    # Reset credit
    old_used_credit = franchise["used_credit"]
    
    await db.franchises.update_one(
        {"id": franchise["id"]},
        {
            "$set": {
                "used_credit": 0.0,
                "available_credit": 100000.0
            }
        }
    )
    
    # Credit ledger entry
    ledger = CreditLedger(
        franchise_id=franchise["id"],
        transaction_type="credit_reset",
        payment_id=payment["id"],
        amount=100000.0,
        credit_before=old_used_credit,
        credit_after=0.0,
        remarks=f"Payment successful - Credit reset",
        created_by=current_user["id"]
    )
    
    ledger_doc = ledger.model_dump()
    ledger_doc['created_at'] = ledger_doc['created_at'].isoformat()
    
    await db.credit_ledger.insert_one(ledger_doc)
    
    # Send notification
    await notify_payment_success(db, payment, franchise["email"])
    
    # Audit log
    await log_audit(db, current_user["id"], current_user["email"], "PAYMENT_SUCCESS", "payments", f"Payment successful - Credit reset")
    
    return {"message": "Payment successful, credit reset"}

@api_router.get("/payments", response_model=List[Payment], tags=["Payments"])
async def list_payments(current_user: dict = Depends(get_current_user)):
    """List payments"""
    query = {}
    if current_user["role"] == "franchise_admin":
        query["franchise_id"] = current_user["franchise_id"]
    
    payments = await db.payments.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Payment(**p) for p in payments]

# ============================================
# Invoice Routes
# ============================================

@api_router.get("/invoices/{filename}", tags=["Invoices"])
async def download_invoice(filename: str):
    """Download invoice PDF"""
    filepath = Path("/app/backend/invoices") / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Invoice not found")
    return FileResponse(filepath, media_type="application/pdf", filename=filename)

# ============================================
# Reports & Analytics
# ============================================

@api_router.get("/reports/dashboard", tags=["Reports"])
async def get_dashboard_stats(current_user: dict = Depends(require_role("super_admin"))):
    """Get dashboard statistics"""
    total_franchises = await db.franchises.count_documents({})
    active_franchises = await db.franchises.count_documents({"is_active": True})
    total_orders = await db.orders.count_documents({})
    pending_orders = await db.orders.count_documents({"status": "pending"})
    
    # Calculate total revenue (approved orders)
    approved_orders = await db.orders.find({"status": "approved"}).to_list(10000)
    total_revenue = sum(order["grand_total"] for order in approved_orders)
    
    # Credit exhausted franchises
    credit_exhausted = await db.franchises.count_documents({"available_credit": {"$lte": 0}})
    
    return {
        "total_franchises": total_franchises,
        "active_franchises": active_franchises,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_revenue": total_revenue,
        "credit_exhausted_franchises": credit_exhausted
    }

@api_router.get("/reports/orders/export", tags=["Reports"])
async def export_orders(current_user: dict = Depends(require_role("super_admin"))):
    """Export orders to CSV"""
    orders = await db.orders.find({}, {"_id": 0}).to_list(10000)
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Order Number", "Franchise", "Order Type", "Status",
        "Subtotal", "GST Total", "Grand Total", "Created At"
    ])
    
    # Write data
    for order in orders:
        writer.writerow([
            order["order_number"],
            order["franchise_name"],
            order["order_type"],
            order["status"],
            order["subtotal"],
            order["gst_total"],
            order["grand_total"],
            order["created_at"]
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
    )

# ============================================
# Settings Routes
# ============================================

@api_router.get("/settings", response_model=Settings, tags=["Settings"])
async def get_settings(current_user: dict = Depends(require_role("super_admin"))):
    """Get system settings"""
    settings = await db.settings.find_one({}, {"_id": 0})
    if not settings:
        # Create default settings
        default_settings = Settings(
            company_name="BigBeanCafe",
            company_address="Franchise Head Office, India",
            company_phone="+91 1234567890",
            company_email="info@bigbeancafe.in",
            company_gstin="22AAAAA0000A1Z5"
        )
        doc = default_settings.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.settings.insert_one(doc)
        return default_settings
    return Settings(**settings)

@api_router.put("/settings", response_model=Settings, tags=["Settings"])
async def update_settings(updates: dict, current_user: dict = Depends(require_role("super_admin"))):
    """Update system settings"""
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    settings = await db.settings.find_one({})
    if settings:
        await db.settings.update_one({"id": settings["id"]}, {"$set": updates})
    else:
        default_settings = Settings(
            company_name="BigBeanCafe",
            company_address="Franchise Head Office, India",
            company_phone="+91 1234567890",
            company_email="info@bigbeancafe.in",
            company_gstin="22AAAAA0000A1Z5"
        )
        doc = default_settings.model_dump()
        doc.update(updates)
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.settings.insert_one(doc)
    
    settings = await db.settings.find_one({}, {"_id": 0})
    await log_audit(db, current_user["id"], current_user["email"], "UPDATE_SETTINGS", "settings", "Updated system settings")
    
    return Settings(**settings)

# ============================================
# Audit Logs
# ============================================

@api_router.get("/audit-logs", response_model=List[AuditLog], tags=["Audit"])
async def get_audit_logs(current_user: dict = Depends(require_role("super_admin"))):
    """Get audit logs"""
    logs = await db.audit_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(1000).to_list(1000)
    return [AuditLog(**log) for log in logs]

# ============================================
# Notification Logs
# ============================================

@api_router.get("/notification-logs", response_model=List[NotificationLog], tags=["Notifications"])
async def get_notification_logs(current_user: dict = Depends(require_role("super_admin"))):
    """Get notification logs"""
    logs = await db.notification_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(1000).to_list(1000)
    return [NotificationLog(**log) for log in logs]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
