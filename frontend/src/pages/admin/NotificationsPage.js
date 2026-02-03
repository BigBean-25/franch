import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell } from 'lucide-react';
import api from '../../services/api';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
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
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await api.get('/notification-logs');
      setNotifications(response.data);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Notification Logs</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow border border-coffee-200">
            <table className="w-full">
              <thead className="bg-coffee-100 border-b border-coffee-200">
                <tr>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Type</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Recipient</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Message</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Status</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Date</th>
                </tr>
              </thead>
              <tbody>
                {notifications.map((notif) => (
                  <tr key={notif.id} className="border-b border-coffee-100 hover:bg-coffee-50">
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 bg-coffee-200 text-coffee-900 rounded text-sm">{notif.type}</span>
                    </td>
                    <td className="px-6 py-4 text-coffee-900">{notif.recipient}</td>
                    <td className="px-6 py-4 text-coffee-700">{notif.message.substring(0, 60)}...</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-sm ${notif.status === 'sent' ? 'bg-green-200 text-green-900' : notif.status === 'pending' ? 'bg-yellow-200 text-yellow-900' : 'bg-red-200 text-red-900'}`}>
                        {notif.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-coffee-700">{new Date(notif.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default NotificationsPage;
