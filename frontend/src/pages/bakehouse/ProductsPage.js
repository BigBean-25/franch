// Similar to admin ProductsPage but filtered for bakehouse only
import React from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, FolderOpen, Package, ShoppingCart } from 'lucide-react';

const ProductsPage = () => {
  const navigation = [
    { label: 'Dashboard', path: '/bakehouse', icon: LayoutDashboard },
    { label: 'Categories', path: '/bakehouse/categories', icon: FolderOpen },
    { label: 'Products', path: '/bakehouse/products', icon: Package },
    { label: 'Orders', path: '/bakehouse/orders', icon: ShoppingCart },
  ];

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Bakehouse Products</h1>
        <p className="text-coffee-700">Manage bakehouse products here. (Use Super Admin panel for full CRUD)</p>
      </div>
    </DashboardLayout>
  );
};

export default ProductsPage;
