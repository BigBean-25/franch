import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import AsyncSessionLocal, init_db
from sql_models import User, Franchise, Category, Product, Settings
from auth import get_password_hash
from datetime import datetime, timezone

async def init_database():
    """Initialize MySQL database with default data"""
    
    print("🚀 Initializing BigBeanCafe MySQL Database...")
    
    # Create all tables
    await init_db()
    print("✅ Database tables created")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if super admin already exists
            result = await session.execute(
                select(User).where(User.email == "admin@bigbeancafe.in")
            )
            existing_admin = result.scalar_one_or_none()
            
            if not existing_admin:
                # Create Super Admin
                print("Creating Super Admin...")
                super_admin = User(
                    email="admin@bigbeancafe.in",
                    password=get_password_hash("admin123"),
                    name="Super Admin",
                    role="super_admin"
                )
                session.add(super_admin)
                print("✅ Super Admin created: admin@bigbeancafe.in / admin123")
            else:
                print("✅ Super Admin already exists")
            
            # Create Sample Franchise
            result = await session.execute(
                select(Franchise).where(Franchise.email == "franchise1@bigbeancafe.in")
            )
            existing_franchise = result.scalar_one_or_none()
            
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
                session.add(franchise)
                await session.flush()  # To get the franchise ID
                
                # Create Franchise Admin user
                franchise_admin = User(
                    email="franchise1@bigbeancafe.in",
                    password=get_password_hash("franchise123"),
                    name="Rajesh Kumar",
                    role="franchise_admin",
                    franchise_id=franchise.id
                )
                session.add(franchise_admin)
                print("✅ Sample Franchise created: franchise1@bigbeancafe.in / franchise123")
            else:
                print("✅ Sample Franchise already exists")
            
            # Create Bakehouse Admin
            result = await session.execute(
                select(User).where(User.email == "bakehouse@bigbeancafe.in")
            )
            existing_bakehouse = result.scalar_one_or_none()
            
            if not existing_bakehouse:
                print("Creating Bakehouse Admin...")
                bakehouse_admin = User(
                    email="bakehouse@bigbeancafe.in",
                    password=get_password_hash("bakehouse123"),
                    name="Bakehouse Manager",
                    role="bakehouse_admin"
                )
                session.add(bakehouse_admin)
                print("✅ Bakehouse Admin created: bakehouse@bigbeancafe.in / bakehouse123")
            else:
                print("✅ Bakehouse Admin already exists")
            
            # Create Merch Admin
            result = await session.execute(
                select(User).where(User.email == "merch@bigbeancafe.in")
            )
            existing_merch = result.scalar_one_or_none()
            
            if not existing_merch:
                print("Creating Merch Admin...")
                merch_admin = User(
                    email="merch@bigbeancafe.in",
                    password=get_password_hash("merch123"),
                    name="Merchandise Manager",
                    role="merch_admin"
                )
                session.add(merch_admin)
                print("✅ Merch Admin created: merch@bigbeancafe.in / merch123")
            else:
                print("✅ Merch Admin already exists")
            
            # Create Categories
            result = await session.execute(
                select(Category).where(Category.type == "bakehouse")
            )
            bakehouse_categories = result.scalars().all()
            
            if not bakehouse_categories:
                print("Creating Bakehouse Categories...")
                categories = [
                    Category(name="Breads & Buns", type="bakehouse", description="Fresh breads and buns"),
                    Category(name="Cakes & Pastries", type="bakehouse", description="Delicious cakes and pastries"),
                    Category(name="Cookies & Biscuits", type="bakehouse", description="Crunchy cookies and biscuits"),
                ]
                for cat in categories:
                    session.add(cat)
                print(f"✅ Created {len(categories)} Bakehouse Categories")
            else:
                print("✅ Bakehouse Categories already exist")
            
            result = await session.execute(
                select(Category).where(Category.type == "merch")
            )
            merch_categories = result.scalars().all()
            
            if not merch_categories:
                print("Creating Merch Categories...")
                categories = [
                    Category(name="Coffee Mugs", type="merch", description="Branded coffee mugs"),
                    Category(name="T-Shirts", type="merch", description="BigBean Cafe branded t-shirts"),
                    Category(name="Caps & Accessories", type="merch", description="Caps and other accessories"),
                ]
                for cat in categories:
                    session.add(cat)
                print(f"✅ Created {len(categories)} Merch Categories")
            else:
                print("✅ Merch Categories already exist")
            
            # Create Sample Products
            result = await session.execute(select(Product))
            existing_products = result.scalars().all()
            
            if not existing_products:
                print("Creating Sample Products...")
                
                # Get category IDs
                bread_cat_result = await session.execute(
                    select(Category).where(Category.name == "Breads & Buns", Category.type == "bakehouse")
                )
                bread_cat = bread_cat_result.scalar_one()
                
                cake_cat_result = await session.execute(
                    select(Category).where(Category.name == "Cakes & Pastries", Category.type == "bakehouse")
                )
                cake_cat = cake_cat_result.scalar_one()
                
                mug_cat_result = await session.execute(
                    select(Category).where(Category.name == "Coffee Mugs", Category.type == "merch")
                )
                mug_cat = mug_cat_result.scalar_one()
                
                tshirt_cat_result = await session.execute(
                    select(Category).where(Category.name == "T-Shirts", Category.type == "merch")
                )
                tshirt_cat = tshirt_cat_result.scalar_one()
                
                products = [
                    Product(
                        name="Whole Wheat Bread",
                        category_id=bread_cat.id,
                        category_type="bakehouse",
                        description="Fresh whole wheat bread",
                        original_price=40.0,
                        offer_price=35.0,
                        gst_percent=5.0,
                        unit="piece"
                    ),
                    Product(
                        name="Burger Buns (Pack of 6)",
                        category_id=bread_cat.id,
                        category_type="bakehouse",
                        description="Soft burger buns",
                        original_price=60.0,
                        gst_percent=5.0,
                        unit="pack"
                    ),
                    Product(
                        name="Chocolate Cake (1kg)",
                        category_id=cake_cat.id,
                        category_type="bakehouse",
                        description="Rich chocolate cake",
                        original_price=500.0,
                        offer_price=450.0,
                        gst_percent=5.0,
                        unit="piece"
                    ),
                    Product(
                        name="Blueberry Muffin",
                        category_id=cake_cat.id,
                        category_type="bakehouse",
                        description="Delicious blueberry muffins",
                        original_price=80.0,
                        gst_percent=5.0,
                        unit="piece"
                    ),
                    Product(
                        name="BigBean Coffee Mug",
                        category_id=mug_cat.id,
                        category_type="merch",
                        description="Premium ceramic coffee mug with BigBean logo",
                        original_price=299.0,
                        offer_price=249.0,
                        gst_percent=18.0,
                        unit="piece"
                    ),
                    Product(
                        name="BigBean Branded T-Shirt",
                        category_id=tshirt_cat.id,
                        category_type="merch",
                        description="Cotton t-shirt with BigBean branding",
                        original_price=599.0,
                        gst_percent=12.0,
                        unit="piece"
                    ),
                ]
                
                for product in products:
                    session.add(product)
                print(f"✅ Created {len(products)} Sample Products")
            else:
                print("✅ Sample Products already exist")
            
            # Create Settings
            result = await session.execute(select(Settings))
            existing_settings = result.scalar_one_or_none()
            
            if not existing_settings:
                print("Creating System Settings...")
                settings = Settings(
                    company_name="BigBeanCafe",
                    company_address="Franchise Head Office, Koramangala, Bangalore - 560034",
                    company_phone="+91 80 1234 5678",
                    company_email="info@bigbeancafe.in",
                    company_gstin="29AAAAA0000A1Z5"
                )
                session.add(settings)
                print("✅ System Settings created")
            else:
                print("✅ System Settings already exist")
            
            # Commit all changes
            await session.commit()
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error initializing database: {e}")
            raise
    
    print("\n🎉 MySQL Database initialization complete!")
    print("\n📝 Demo Credentials:")
    print("━" * 60)
    print("Super Admin:      admin@bigbeancafe.in / admin123")
    print("Franchise Admin:  franchise1@bigbeancafe.in / franchise123")
    print("Bakehouse Admin:  bakehouse@bigbeancafe.in / bakehouse123")
    print("Merch Admin:      merch@bigbeancafe.in / merch123")
    print("━" * 60)

if __name__ == "__main__":
    asyncio.run(init_database())
