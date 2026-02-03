import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, ShoppingBag, ShoppingCart, Package, CreditCard } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const FranchisePortal = () => {
  const { user } = useAuth();
  const [franchise, setFranchise] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const navigation = [
    { label: 'Dashboard', path: '/portal', icon: LayoutDashboard },
    { label: 'Browse Products', path: '/portal/products', icon: ShoppingBag },
    { label: 'Cart', path: '/portal/cart', icon: ShoppingCart },
    { label: 'My Orders', path: '/portal/orders', icon: Package },
    { label: 'Pay Outstanding', path: '/portal/pay-outstanding', icon: CreditCard },
  ];

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [franchiseRes, ordersRes] = await Promise.all([
        api.get(`/franchises/${user.franchise_id}`),
        api.get('/orders')
      ]);
      setFranchise(franchiseRes.data);
      setOrders(ordersRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const creditUsagePercent = franchise ? (franchise.used_credit / franchise.credit_limit) * 100 : 0;

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Franchise Dashboard</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
                <p className="text-sm text-coffee-700 mb-1">Credit Limit</p>
                <p className="text-3xl font-bold text-coffee-900">₹{franchise?.credit_limit.toLocaleString('en-IN')}</p>
              </div>

              <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
                <p className="text-sm text-coffee-700 mb-1">Used Credit</p>
                <p className="text-3xl font-bold text-red-600">₹{franchise?.used_credit.toLocaleString('en-IN')}</p>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${creditUsagePercent >= 100 ? 'bg-red-600' : creditUsagePercent >= 75 ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{ width: `${Math.min(creditUsagePercent, 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
                <p className="text-sm text-coffee-700 mb-1">Available Credit</p>
                <p className={`text-3xl font-bold ${franchise?.available_credit <= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  ₹{franchise?.available_credit.toLocaleString('en-IN')}
                </p>
              </div>
            </div>

            {franchise?.available_credit <= 0 && (
              <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
                <p className="text-red-800 font-semibold">⚠️ Credit Exhausted! Please make a payment to continue ordering.</p>
              </div>
            )}

            <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
              <h2 className="text-xl font-bold text-coffee-900 mb-4">Recent Orders</h2>
              <div className="space-y-3">
                {orders.slice(0, 5).map((order) => (
                  <div key={order.id} className="flex justify-between items-center p-3 bg-coffee-50 rounded-lg">
                    <div>
                      <p className="font-semibold text-coffee-900">{order.order_number}</p>
                      <p className="text-sm text-coffee-700">{new Date(order.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-coffee-900">₹{order.grand_total.toLocaleString('en-IN')}</p>
                      <span className={`text-xs px-2 py-1 rounded-full ${order.status === 'approved' ? 'bg-green-200 text-green-900' : order.status === 'pending' ? 'bg-yellow-200 text-yellow-900' : 'bg-red-200 text-red-900'}`}>
                        {order.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default FranchisePortal;
