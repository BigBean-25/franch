import React from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell, Download } from 'lucide-react';
import api from '../../services/api';

const ReportsPage = () => {
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

  const handleExport = async () => {
    try {
      const response = await api.get('/reports/orders/export', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'orders_export.csv');
      document.body.appendChild(link);
      link.click();
    } catch (error) {
      alert('Failed to export orders');
    }
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Reports</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <h2 className="text-xl font-bold text-coffee-900 mb-4">Orders Export</h2>
            <p className="text-coffee-700 mb-4">Export all orders data to CSV format for analysis.</p>
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800"
            >
              <Download className="w-5 h-5" />
              Export Orders CSV
            </button>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <h2 className="text-xl font-bold text-coffee-900 mb-4">Sales Report</h2>
            <p className="text-coffee-700 mb-4">Generate comprehensive sales reports.</p>
            <button className="px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800">
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ReportsPage;
