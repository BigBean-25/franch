import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, FolderOpen, Package, ShoppingCart } from 'lucide-react';
import api from '../../services/api';

const MerchAdmin = () => {
  const [stats, setStats] = useState({ categories: 0, products: 0, orders: 0 });

  const navigation = [
    { label: 'Dashboard', path: '/merch', icon: LayoutDashboard },
    { label: 'Categories', path: '/merch/categories', icon: FolderOpen },
    { label: 'Products', path: '/merch/products', icon: Package },
    { label: 'Orders', path: '/merch/orders', icon: ShoppingCart },
  ];

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [cats, prods, orders] = await Promise.all([
        api.get('/categories?type=merch'),
        api.get('/products?category_type=merch'),
        api.get('/orders?order_type=merch')
      ]);
      setStats({
        categories: cats.data.length,
        products: prods.data.length,
        orders: orders.data.length
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Merch Admin Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <FolderOpen className="w-12 h-12 text-coffee-600 mb-2" />
            <p className="text-coffee-700">Categories</p>
            <p className="text-3xl font-bold text-coffee-900">{stats.categories}</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <Package className="w-12 h-12 text-coffee-600 mb-2" />
            <p className="text-coffee-700">Products</p>
            <p className="text-3xl font-bold text-coffee-900">{stats.products}</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <ShoppingCart className="w-12 h-12 text-coffee-600 mb-2" />
            <p className="text-coffee-700">Orders</p>
            <p className="text-3xl font-bold text-coffee-900">{stats.orders}</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default MerchAdmin;
