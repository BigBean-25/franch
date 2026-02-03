import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, FolderOpen, Package, ShoppingCart, CheckCircle, XCircle } from 'lucide-react';
import api from '../../services/api';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  const navigation = [
    { label: 'Dashboard', path: '/bakehouse', icon: LayoutDashboard },
    { label: 'Categories', path: '/bakehouse/categories', icon: FolderOpen },
    { label: 'Products', path: '/bakehouse/products', icon: Package },
    { label: 'Orders', path: '/bakehouse/orders', icon: ShoppingCart },
  ];

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders?order_type=bakehouse');
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (orderId) => {
    if (window.confirm('Approve this order?')) {
      try {
        await api.post(`/orders/${orderId}/approve`);
        fetchOrders();
        alert('Order approved!');
      } catch (error) {
        alert(error.response?.data?.detail || 'Failed to approve order');
      }
    }
  };

  const handleReject = async (orderId) => {
    const reason = prompt('Enter rejection reason:');
    if (reason) {
      try {
        await api.post(`/orders/${orderId}/reject?remarks=${encodeURIComponent(reason)}`);
        fetchOrders();
        alert('Order rejected');
      } catch (error) {
        alert('Failed to reject order');
      }
    }
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Bakehouse Orders</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="bg-white rounded-lg shadow p-6 border border-coffee-200">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold text-coffee-900">{order.order_number}</h3>
                    <p className="text-coffee-700">{order.franchise_name}</p>
                    <p className="text-sm text-coffee-600">{new Date(order.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-coffee-900">₹{order.grand_total.toLocaleString('en-IN')}</p>
                    <span className={`px-3 py-1 rounded-full text-sm ${order.status === 'approved' ? 'bg-green-200 text-green-900' : order.status === 'pending' ? 'bg-yellow-200 text-yellow-900' : 'bg-red-200 text-red-900'}`}>
                      {order.status}
                    </span>
                  </div>
                </div>

                {order.status === 'pending' && (
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => handleApprove(order.id)}
                      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      <CheckCircle className="w-5 h-5" />
                      Approve
                    </button>
                    <button
                      onClick={() => handleReject(order.id)}
                      className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      <XCircle className="w-5 h-5" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default OrdersPage;
