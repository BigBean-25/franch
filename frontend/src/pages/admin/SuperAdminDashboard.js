import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { 
  LayoutDashboard, Users, Store, FolderOpen, Package, 
  ShoppingCart, CreditCard, Settings, FileText, Bell 
} from 'lucide-react';
import api from '../../services/api';

const SuperAdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const navigation = [
    { label: 'Dashboard', path: '/admin', icon: LayoutDashboard },
    { label: 'Users', path: '/admin/users', icon: Users },
    { label: 'Franchises', path: '/admin/franchises', icon: Store },
    { label: 'Categories', path: '/admin/categories', icon: FolderOpen },
    { label: 'Products', path: '/admin/products', icon: Package },
    { label: 'Orders', path: '/admin/orders', icon: ShoppingCart },
    { label: 'Payments', path: '/admin/payments', icon: CreditCard },
    { label: 'Reports', path: '/admin/reports', icon: FileText },
    { label: 'Notifications', path: '/admin/notifications', icon: Bell },
    { label: 'Settings', path: '/admin/settings', icon: Settings },
  ];

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/reports/dashboard');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div data-testid="super-admin-dashboard">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Super Admin Dashboard</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto"></div>
          </div>
        ) : (
          <div>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6" data-testid="stat-franchises">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Franchises</p>
                    <p className="text-3xl font-bold text-gray-800">{stats?.total_franchises || 0}</p>
                  </div>
                  <Store className="w-12 h-12 text-blue-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6" data-testid="stat-orders">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Orders</p>
                    <p className="text-3xl font-bold text-gray-800">{stats?.total_orders || 0}</p>
                  </div>
                  <ShoppingCart className="w-12 h-12 text-green-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6" data-testid="stat-pending">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Pending Orders</p>
                    <p className="text-3xl font-bold text-gray-800">{stats?.pending_orders || 0}</p>
                  </div>
                  <FileText className="w-12 h-12 text-orange-500" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6" data-testid="stat-revenue">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Revenue</p>
                    <p className="text-3xl font-bold text-gray-800">₹{stats?.total_revenue?.toLocaleString('en-IN') || 0}</p>
                  </div>
                  <CreditCard className="w-12 h-12 text-purple-500" />
                </div>
              </div>
            </div>

            {/* Alerts */}
            {stats?.credit_exhausted_franchises > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-2">
                  <Bell className="w-5 h-5 text-red-600" />
                  <p className="text-red-700 font-semibold">
                    {stats.credit_exhausted_franchises} franchise(s) have exhausted their credit limit
                  </p>
                </div>
              </div>
            )}

            {stats?.pending_orders > 0 && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-2">
                  <Bell className="w-5 h-5 text-orange-600" />
                  <p className="text-orange-700 font-semibold">
                    {stats.pending_orders} order(s) pending approval
                  </p>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-orange-500 transition-colors text-left">
                  <Users className="w-8 h-8 text-orange-600 mb-2" />
                  <p className="font-semibold text-gray-800">Manage Users</p>
                  <p className="text-sm text-gray-600">Create and manage user accounts</p>
                </button>
                <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-orange-500 transition-colors text-left">
                  <ShoppingCart className="w-8 h-8 text-orange-600 mb-2" />
                  <p className="font-semibold text-gray-800">Approve Orders</p>
                  <p className="text-sm text-gray-600">Review and approve pending orders</p>
                </button>
                <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-orange-500 transition-colors text-left">
                  <FileText className="w-8 h-8 text-orange-600 mb-2" />
                  <p className="font-semibold text-gray-800">View Reports</p>
                  <p className="text-sm text-gray-600">Generate and export reports</p>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default SuperAdminDashboard;
