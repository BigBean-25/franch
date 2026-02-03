# BigBean Franchise Management System - Setup Guide

## ✅ Completed Tasks

### 1. Removed "Built with Emergent" References
- ✅ Removed emergent badge from `frontend/public/index.html`
- ✅ Updated page title to "BigBean | Franchise Management"
- ✅ Updated meta description to "BigBean Franchise Management System"
- ✅ Removed emergent scripts and visual editing tools
- ✅ Deleted `.emergent/` directory
- ✅ Updated dev server configuration to use BigBean domains
- ✅ Changed git commit emails from emergent to `support@bigbeancafe.in`

### 2. Converted Database from MongoDB to MySQL
- ✅ Created MySQL database configuration (`backend/database.py`)
- ✅ Created SQLAlchemy models (`backend/sql_models.py`)
- ✅ Created MySQL initialization script (`backend/init_mysql_db.py`)
- ✅ Created new MySQL-based server (`backend/mysql_server.py`)
- ✅ Added MySQL audit logging (`backend/utils/audit_mysql.py`)

## 🚀 Next Steps to Complete Setup

### Step 1: Create Environment Configuration
1. Navigate to `backend/` directory
2. Copy `env_template.txt` to `.env`
3. The MySQL credentials are already configured for your Hostinger database:
   ```
   DB_HOST=localhost
   DB_USER=u672910709_bigbeanorg
   DB_PASSWORD=Bbc@org26.
   DB_NAME=u672910709_bigbeanorg
   DB_PORT=3306
   ```
4. Generate a secure JWT secret key and update `JWT_SECRET_KEY` in `.env`

### Step 2: Test Database Connection
```bash
cd backend
python test_mysql_connection.py
```

### Step 3: Initialize Database
```bash
cd backend
python init_mysql_db.py
```

### Step 4: Start the Application

#### Backend (MySQL version):
```bash
cd backend
uvicorn mysql_server:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend:
```bash
cd frontend
npm install
npm start
```

## 📝 Demo Credentials (After Database Initialization)

| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@bigbeancafe.in | admin123 |
| Franchise Admin | franchise1@bigbeancafe.in | franchise123 |
| Bakehouse Admin | bakehouse@bigbeancafe.in | bakehouse123 |
| Merch Admin | merch@bigbeancafe.in | merch123 |

## 🗄️ Database Schema

The MySQL database includes these main tables:
- `users` - User accounts and authentication
- `franchises` - Franchise information and credit management
- `categories` - Product categories (bakehouse/merch)
- `products` - Product catalog
- `orders` - Order management
- `cart_items` - Shopping cart functionality
- `invoices` - Invoice generation and tracking
- `credit_ledger` - Credit transaction history
- `audit_logs` - System audit trail
- `settings` - Application settings

## 🔧 Troubleshooting

### Database Connection Issues
1. Verify Hostinger MySQL credentials
2. Check if your IP is whitelisted in Hostinger control panel
3. Ensure MySQL service is running
4. Check firewall settings

### Application Issues
1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Verify `.env` file is created and configured
3. Check that the database is initialized
4. Ensure both backend and frontend are running on different ports

## 🌐 API Endpoints

The API will be available at `http://localhost:8000` with endpoints:
- `/api/auth/login` - User authentication
- `/api/users` - User management
- `/api/franchises` - Franchise management
- `/api/categories` - Category management
- `/api/products` - Product catalog
- `/api/orders` - Order processing
- `/api/cart` - Shopping cart

## 📊 Features

- **Multi-role Authentication**: Super Admin, Franchise Admin, Bakehouse Admin, Merch Admin
- **Franchise Management**: Credit limits, order tracking, invoice generation
- **Product Catalog**: Bakehouse and merchandise items
- **Order Processing**: Cart management, approval workflow
- **Credit System**: Credit limits, usage tracking, payment processing
- **Audit Trail**: Complete system activity logging
- **Invoice Generation**: PDF invoice creation
- **Notifications**: Email and SMS notifications (configurable)

Your BigBean Franchise Management System is now ready to use with MySQL database!
