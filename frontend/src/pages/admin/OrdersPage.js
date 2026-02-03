import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell, CheckCircle, XCircle, Download } from 'lucide-react';
import api from '../../services/api';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState(null);

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
    fetchOrders();
  }, [filter]);

  const fetchOrders = async () => {
    try {
      const params = filter !== 'all' ? `?status_filter=${filter}` : '';
      const response = await api.get(`/orders${params}`);
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (orderId) => {
    if (window.confirm('Approve this order? Credit will be deducted.')) {
      try {
        await api.post(`/orders/${orderId}/approve`);
        fetchOrders();
        setSelectedOrder(null);
        alert('Order approved successfully!');
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
        setSelectedOrder(null);
        alert('Order rejected');
      } catch (error) {
        alert('Failed to reject order');
      }
    }
  };

  const getStatusColor = (status) => {
    if (status === 'pending') return 'bg-yellow-200 text-yellow-900';
    if (status === 'approved') return 'bg-green-200 text-green-900';
    if (status === 'rejected') return 'bg-red-200 text-red-900';
    return 'bg-gray-200 text-gray-900';
  };

  const filteredOrders = filter === 'all' ? orders : orders.filter(o => o.status === filter);

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Orders Management</h1>

        <div className="flex gap-2 mb-4">
          <button onClick={() => setFilter('all')} className={`px-4 py-2 rounded-lg ${filter === 'all' ? 'bg-coffee-700 text-white' : 'bg-white text-coffee-900 border border-coffee-200'}`}>All</button>
          <button onClick={() => setFilter('pending')} className={`px-4 py-2 rounded-lg ${filter === 'pending' ? 'bg-coffee-700 text-white' : 'bg-white text-coffee-900 border border-coffee-200'}`}>Pending</button>
          <button onClick={() => setFilter('approved')} className={`px-4 py-2 rounded-lg ${filter === 'approved' ? 'bg-coffee-700 text-white' : 'bg-white text-coffee-900 border border-coffee-200'}`}>Approved</button>
          <button onClick={() => setFilter('rejected')} className={`px-4 py-2 rounded-lg ${filter === 'rejected' ? 'bg-coffee-700 text-white' : 'bg-white text-coffee-900 border border-coffee-200'}`}>Rejected</button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredOrders.map((order) => (
              <div key={order.id} className="bg-white rounded-lg shadow p-6 border border-coffee-200">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-coffee-900">{order.order_number}</h3>
                    <p className="text-coffee-700">{order.franchise_name}</p>
                    <p className="text-sm text-coffee-600">{new Date(order.created_at).toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 rounded-full text-sm ${getStatusColor(order.status)}`}>{order.status}</span>
                    <p className="text-2xl font-bold text-coffee-900 mt-2">₹{order.grand_total.toLocaleString('en-IN')}</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-4 p-4 bg-coffee-50 rounded-lg">
                  <div>
                    <p className="text-sm text-coffee-600">Type</p>
                    <p className="font-semibold text-coffee-900">{order.order_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-coffee-600">Items</p>
                    <p className="font-semibold text-coffee-900">{order.items.length}</p>
                  </div>
                  <div>
                    <p className="text-sm text-coffee-600">GST</p>
                    <p className="font-semibold text-coffee-900">₹{order.gst_total.toLocaleString('en-IN')}</p>
                  </div>
                </div>

                {order.status === 'pending' && (
                  <div className="flex gap-2 mt-4">
                    <button onClick={() => handleApprove(order.id)} className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                      <CheckCircle className="w-5 h-5" />
                      Approve
                    </button>
                    <button onClick={() => handleReject(order.id)} className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                      <XCircle className="w-5 h-5" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}

            {filteredOrders.length === 0 && (
              <div className="text-center py-12 text-coffee-700">No orders found</div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default OrdersPage;
