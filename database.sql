-- BigBeanCafe Franchise Ordering System
-- MySQL/MariaDB Database Schema
-- Version: 1.0.0

-- Drop existing tables if any (for fresh installation)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS notification_logs;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS credit_ledger;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS franchises;
DROP TABLE IF EXISTS settings;
SET FOREIGN_KEY_CHECKS = 1;

-- Settings Table
CREATE TABLE settings (
    id VARCHAR(36) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL DEFAULT 'BigBeanCafe',
    company_address TEXT NOT NULL,
    company_phone VARCHAR(20) NOT NULL,
    company_email VARCHAR(255) NOT NULL,
    company_gstin VARCHAR(20) NOT NULL,
    logo_url VARCHAR(512),
    razorpay_key_id VARCHAR(255),
    razorpay_key_secret VARCHAR(255),
    email_enabled BOOLEAN DEFAULT FALSE,
    whatsapp_enabled BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Franchises Table
CREATE TABLE franchises (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    gstin VARCHAR(20),
    credit_limit DECIMAL(12, 2) DEFAULT 100000.00,
    used_credit DECIMAL(12, 2) DEFAULT 0.00,
    available_credit DECIMAL(12, 2) DEFAULT 100000.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role ENUM('super_admin', 'franchise_admin', 'bakehouse_admin', 'merch_admin') NOT NULL,
    franchise_id VARCHAR(36),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id) ON DELETE SET NULL
);

-- Categories Table
CREATE TABLE categories (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type ENUM('bakehouse', 'merch') NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_name_type (name, type)
);

-- Products Table
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id VARCHAR(36) NOT NULL,
    category_type ENUM('bakehouse', 'merch') NOT NULL,
    description TEXT,
    original_price DECIMAL(10, 2) NOT NULL,
    offer_price DECIMAL(10, 2),
    gst_percent DECIMAL(5, 2) DEFAULT 18.00,
    sgst_percent DECIMAL(5, 2) DEFAULT 9.00,
    cgst_percent DECIMAL(5, 2) DEFAULT 9.00,
    unit VARCHAR(50) DEFAULT 'piece',
    image_url VARCHAR(512),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Cart Items Table
CREATE TABLE cart_items (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    franchise_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    gst_percent DECIMAL(5, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Orders Table
CREATE TABLE orders (
    id VARCHAR(36) PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    franchise_id VARCHAR(36) NOT NULL,
    franchise_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    order_type ENUM('bakehouse', 'merch') NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    sgst_total DECIMAL(12, 2) NOT NULL,
    cgst_total DECIMAL(12, 2) NOT NULL,
    gst_total DECIMAL(12, 2) NOT NULL,
    grand_total DECIMAL(12, 2) NOT NULL,
    status ENUM('pending', 'approved', 'rejected', 'completed', 'cancelled') DEFAULT 'pending',
    remarks TEXT,
    invoice_number VARCHAR(50),
    invoice_url VARCHAR(512),
    approved_by VARCHAR(36),
    approved_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Order Items Table
CREATE TABLE order_items (
    id VARCHAR(36) PRIMARY KEY,
    order_id VARCHAR(36) NOT NULL,
    product_id VARCHAR(36) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    gst_percent DECIMAL(5, 2) NOT NULL,
    sgst_percent DECIMAL(5, 2) NOT NULL,
    cgst_percent DECIMAL(5, 2) NOT NULL,
    taxable_amount DECIMAL(12, 2) NOT NULL,
    sgst_amount DECIMAL(12, 2) NOT NULL,
    cgst_amount DECIMAL(12, 2) NOT NULL,
    gst_amount DECIMAL(12, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

-- Payments Table
CREATE TABLE payments (
    id VARCHAR(36) PRIMARY KEY,
    payment_id VARCHAR(50) NOT NULL UNIQUE,
    franchise_id VARCHAR(36) NOT NULL,
    franchise_name VARCHAR(255) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    razorpay_order_id VARCHAR(100),
    razorpay_payment_id VARCHAR(100),
    razorpay_signature VARCHAR(255),
    status ENUM('pending', 'success', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id) ON DELETE RESTRICT
);

-- Credit Ledger Table
CREATE TABLE credit_ledger (
    id VARCHAR(36) PRIMARY KEY,
    franchise_id VARCHAR(36) NOT NULL,
    transaction_type ENUM('order_placed', 'order_approved', 'order_rejected', 'payment_made', 'credit_reset') NOT NULL,
    order_id VARCHAR(36),
    payment_id VARCHAR(36),
    amount DECIMAL(12, 2) NOT NULL,
    credit_before DECIMAL(12, 2) NOT NULL,
    credit_after DECIMAL(12, 2) NOT NULL,
    remarks TEXT,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id) ON DELETE RESTRICT,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT
);

-- Invoices Table
CREATE TABLE invoices (
    id VARCHAR(36) PRIMARY KEY,
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    order_id VARCHAR(36) NOT NULL,
    franchise_id VARCHAR(36) NOT NULL,
    franchise_name VARCHAR(255) NOT NULL,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    invoice_url VARCHAR(512) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (franchise_id) REFERENCES franchises(id) ON DELETE RESTRICT
);

-- Notification Logs Table
CREATE TABLE notification_logs (
    id VARCHAR(36) PRIMARY KEY,
    type ENUM('email', 'whatsapp') NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
    retry_count INT DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL
);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    module VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_franchises_email ON franchises(email);
CREATE INDEX idx_franchises_is_active ON franchises(is_active);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_category_type ON products(category_type);
CREATE INDEX idx_orders_franchise_id ON orders(franchise_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_payments_franchise_id ON payments(franchise_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_credit_ledger_franchise_id ON credit_ledger(franchise_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
