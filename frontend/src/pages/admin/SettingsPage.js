import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell } from 'lucide-react';
import api from '../../services/api';

const SettingsPage = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({});

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
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await api.get('/settings');
      setSettings(response.data);
      setFormData(response.data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.put('/settings', formData);
      alert('Settings updated successfully');
      fetchSettings();
    } catch (error) {
      alert('Failed to update settings');
    }
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">System Settings</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Company Name</label>
                  <input
                    type="text"
                    value={formData.company_name || ''}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Company GSTIN</label>
                  <input
                    type="text"
                    value={formData.company_gstin || ''}
                    onChange={(e) => setFormData({ ...formData, company_gstin: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Company Email</label>
                  <input
                    type="email"
                    value={formData.company_email || ''}
                    onChange={(e) => setFormData({ ...formData, company_email: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Company Phone</label>
                  <input
                    type="tel"
                    value={formData.company_phone || ''}
                    onChange={(e) => setFormData({ ...formData, company_phone: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-coffee-800 mb-1">Company Address</label>
                <textarea
                  value={formData.company_address || ''}
                  onChange={(e) => setFormData({ ...formData, company_address: e.target.value })}
                  className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  rows="2"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Razorpay Key ID</label>
                  <input
                    type="text"
                    value={formData.razorpay_key_id || ''}
                    onChange={(e) => setFormData({ ...formData, razorpay_key_id: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    placeholder="Enter Razorpay Key ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Razorpay Key Secret</label>
                  <input
                    type="password"
                    value={formData.razorpay_key_secret || ''}
                    onChange={(e) => setFormData({ ...formData, razorpay_key_secret: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    placeholder="Enter Razorpay Key Secret"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="px-6 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800"
              >
                Save Settings
              </button>
            </form>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default SettingsPage;
