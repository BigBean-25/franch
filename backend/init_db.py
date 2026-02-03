import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from auth import get_password_hash
from models import User, Franchise, Category, Product, Settings
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def init_database():
    """Initialize database with default data"""
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'bigbeancafe_db')]
    
    print("🚀 Initializing BigBeanCafe Database...")
    
    # Check if super admin already exists
    existing_admin = await db.users.find_one({"email": "admin@bigbeancafe.in"})
    
    if not existing_admin:
        # Create Super Admin
        print("Creating Super Admin...")
        super_admin = User(
            email="admin@bigbeancafe.in",
            password=get_password_hash("admin123"),
            name="Super Admin",
            role="super_admin"
        )
        
        doc = super_admin.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        print("✅ Super Admin created: admin@bigbeancafe.in / admin123")
    else:
        print("✅ Super Admin already exists")
    
    # Create Sample Franchise
    existing_franchise = await db.franchises.find_one({"email": "franchise1@bigbeancafe.in"})
    
    if not existing_franchise:
        print("Creating Sample Franchise...")
        franchise = Franchise(
            name="BigBean Cafe - Mumbai Central",
            owner_name="Rajesh Kumar",
            email="franchise1@bigbeancafe.in",
            phone="+91 9876543210",
            address="Shop No. 12, Central Plaza",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            gstin="27AAAAA0000A1Z5"
        )
        
        doc = franchise.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.franchises.insert_one(doc)
        
        franchise_id = doc['id']
        
        # Create Franchise Admin user
        franchise_admin = User(
            email="franchise1@bigbeancafe.in",
            password=get_password_hash("franchise123"),
            name="Rajesh Kumar",
            role="franchise_admin",
            franchise_id=franchise_id
        )
        
        admin_doc = franchise_admin.model_dump()
        admin_doc['created_at'] = admin_doc['created_at'].isoformat()
        await db.users.insert_one(admin_doc)
        
        print("✅ Sample Franchise created: franchise1@bigbeancafe.in / franchise123")
    else:
        print("✅ Sample Franchise already exists")
    
    # Create Bakehouse Admin
    existing_bakehouse = await db.users.find_one({"email": "bakehouse@bigbeancafe.in"})
    
    if not existing_bakehouse:
        print("Creating Bakehouse Admin...")
        bakehouse_admin = User(
            email="bakehouse@bigbeancafe.in",
            password=get_password_hash("bakehouse123"),
            name="Bakehouse Manager",
            role="bakehouse_admin"
        )
        
        doc = bakehouse_admin.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        print("✅ Bakehouse Admin created: bakehouse@bigbeancafe.in / bakehouse123")
    else:
        print("✅ Bakehouse Admin already exists")
    
    # Create Merch Admin
    existing_merch = await db.users.find_one({"email": "merch@bigbeancafe.in"})
    
    if not existing_merch:
        print("Creating Merch Admin...")
        merch_admin = User(
            email="merch@bigbeancafe.in",
            password=get_password_hash("merch123"),
            name="Merchandise Manager",
            role="merch_admin"
        )
        
        doc = merch_admin.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        print("✅ Merch Admin created: merch@bigbeancafe.in / merch123")
    else:
        print("✅ Merch Admin already exists")
    
    # Create Categories
    bakehouse_cat_count = await db.categories.count_documents({"type": "bakehouse"})
    
    if bakehouse_cat_count == 0:
        print("Creating Bakehouse Categories...")
        bakehouse_categories = [
            Category(name="Breads & Buns", type="bakehouse", description="Fresh breads and buns"),
            Category(name="Cakes & Pastries", type="bakehouse", description="Delicious cakes and pastries"),
            Category(name="Cookies & Biscuits", type="bakehouse", description="Crunchy cookies and biscuits"),
        ]
        
        for cat in bakehouse_categories:
            doc = cat.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.categories.insert_one(doc)
        
        print(f"✅ Created {len(bakehouse_categories)} Bakehouse Categories")
    else:
        print("✅ Bakehouse Categories already exist")
    
    merch_cat_count = await db.categories.count_documents({"type": "merch"})
    
    if merch_cat_count == 0:
        print("Creating Merch Categories...")
        merch_categories = [
            Category(name="Coffee Mugs", type="merch", description="Branded coffee mugs"),
            Category(name="T-Shirts", type="merch", description="BigBean Cafe branded t-shirts"),
            Category(name="Caps & Accessories", type="merch", description="Caps and other accessories"),
        ]
        
        for cat in merch_categories:
            doc = cat.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.categories.insert_one(doc)
        
        print(f"✅ Created {len(merch_categories)} Merch Categories")
    else:
        print("✅ Merch Categories already exist")
    
    # Create Sample Products
    product_count = await db.products.count_documents({})
    
    if product_count == 0:
        print("Creating Sample Products...")
        
        # Get category IDs
        bread_cat = await db.categories.find_one({"name": "Breads & Buns", "type": "bakehouse"})
        cake_cat = await db.categories.find_one({"name": "Cakes & Pastries", "type": "bakehouse"})
        mug_cat = await db.categories.find_one({"name": "Coffee Mugs", "type": "merch"})
        tshirt_cat = await db.categories.find_one({"name": "T-Shirts", "type": "merch"})
        
        products = [
            Product(
                name="Whole Wheat Bread",
                category_id=bread_cat['id'],
                category_type="bakehouse",
                description="Fresh whole wheat bread",
                original_price=40.0,
                offer_price=35.0,
                gst_percent=5.0,
                unit="piece"
            ),
            Product(
                name="Burger Buns (Pack of 6)",
                category_id=bread_cat['id'],
                category_type="bakehouse",
                description="Soft burger buns",
                original_price=60.0,
                gst_percent=5.0,
                unit="pack"
            ),
            Product(
                name="Chocolate Cake (1kg)",
                category_id=cake_cat['id'],
                category_type="bakehouse",
                description="Rich chocolate cake",
                original_price=500.0,
                offer_price=450.0,
                gst_percent=5.0,
                unit="piece"
            ),
            Product(
                name="Blueberry Muffin",
                category_id=cake_cat['id'],
                category_type="bakehouse",
                description="Delicious blueberry muffins",
                original_price=80.0,
                gst_percent=5.0,
                unit="piece"
            ),
            Product(
                name="BigBean Coffee Mug",
                category_id=mug_cat['id'],
                category_type="merch",
                description="Premium ceramic coffee mug with BigBean logo",
                original_price=299.0,
                offer_price=249.0,
                gst_percent=18.0,
                unit="piece"
            ),
            Product(
                name="BigBean Branded T-Shirt",
                category_id=tshirt_cat['id'],
                category_type="merch",
                description="Cotton t-shirt with BigBean branding",
                original_price=599.0,
                gst_percent=12.0,
                unit="piece"
            ),
        ]
        
        for product in products:
            doc = product.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.products.insert_one(doc)
        
        print(f"✅ Created {len(products)} Sample Products")
    else:
        print("✅ Sample Products already exist")
    
    # Create Settings
    existing_settings = await db.settings.find_one({})
    
    if not existing_settings:
        print("Creating System Settings...")
        settings = Settings(
            company_name="BigBeanCafe",
            company_address="Franchise Head Office, Koramangala, Bangalore - 560034",
            company_phone="+91 80 1234 5678",
            company_email="info@bigbeancafe.in",
            company_gstin="29AAAAA0000A1Z5"
        )
        
        doc = settings.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.settings.insert_one(doc)
        print("✅ System Settings created")
    else:
        print("✅ System Settings already exist")
    
    # Create indexes
    print("Creating database indexes...")
    await db.users.create_index("email", unique=True)
    await db.franchises.create_index("email", unique=True)
    await db.orders.create_index("order_number", unique=True)
    await db.invoices.create_index("invoice_number", unique=True)
    print("✅ Database indexes created")
    
    client.close()
    
    print("\n🎉 Database initialization complete!")
    print("\n📝 Demo Credentials:")
    print("━" * 60)
    print("Super Admin:      admin@bigbeancafe.in / admin123")
    print("Franchise Admin:  franchise1@bigbeancafe.in / franchise123")
    print("Bakehouse Admin:  bakehouse@bigbeancafe.in / bakehouse123")
    print("Merch Admin:      merch@bigbeancafe.in / merch123")
    print("━" * 60)

if __name__ == "__main__":
    asyncio.run(init_database())
