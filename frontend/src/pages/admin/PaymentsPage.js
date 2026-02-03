import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell } from 'lucide-react';
import api from '../../services/api';

const PaymentsPage = () => {
  const [payments, setPayments] = useState([]);
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
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      const response = await api.get('/payments');
      setPayments(response.data);
    } catch (error) {
      console.error('Failed to fetch payments:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Payments</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow border border-coffee-200">
            <table className="w-full">
              <thead className="bg-coffee-100 border-b border-coffee-200">
                <tr>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Payment ID</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Franchise</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Amount</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Status</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Date</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <tr key={payment.id} className="border-b border-coffee-100 hover:bg-coffee-50">
                    <td className="px-6 py-4 text-coffee-700 font-mono text-sm">{payment.razorpay_payment_id || payment.payment_id}</td>
                    <td className="px-6 py-4 text-coffee-900">{payment.franchise_name}</td>
                    <td className="px-6 py-4 text-coffee-900 font-semibold">₹{payment.amount.toLocaleString('en-IN')}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-sm ${payment.status === 'success' ? 'bg-green-200 text-green-900' : payment.status === 'pending' ? 'bg-yellow-200 text-yellow-900' : 'bg-red-200 text-red-900'}`}>
                        {payment.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-coffee-700">{new Date(payment.created_at).toLocaleString()}</td>
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

export default PaymentsPage;
