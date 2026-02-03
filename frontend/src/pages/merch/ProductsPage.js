import React from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, FolderOpen, Package, ShoppingCart } from 'lucide-react';

const ProductsPage = () => {
  const navigation = [
    { label: 'Dashboard', path: '/merch', icon: LayoutDashboard },
    { label: 'Categories', path: '/merch/categories', icon: FolderOpen },
    { label: 'Products', path: '/merch/products', icon: Package },
    { label: 'Orders', path: '/merch/orders', icon: ShoppingCart },
  ];

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Merch Products</h1>
        <p className="text-coffee-700">Manage merchandise products here. (Use Super Admin panel for full CRUD)</p>
      </div>
    </DashboardLayout>
  );
};

export default ProductsPage;
