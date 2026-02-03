import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, ShoppingBag, ShoppingCart, Package, CreditCard, Download } from 'lucide-react';
import api from '../../services/api';

const MyOrdersPage = () => {
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
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders');
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-200 text-yellow-900',
      approved: 'bg-green-200 text-green-900',
      rejected: 'bg-red-200 text-red-900',
    };
    return colors[status] || 'bg-gray-200 text-gray-900';
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">My Orders</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="bg-white rounded-lg shadow p-6 border border-coffee-200">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-coffee-900">{order.order_number}</h3>
                    <p className="text-sm text-coffee-600">{new Date(order.created_at).toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 rounded-full text-sm ${getStatusColor(order.status)}`}>
                      {order.status}
                    </span>
                    <p className="text-2xl font-bold text-coffee-900 mt-2">₹{order.grand_total.toLocaleString('en-IN')}</p>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 p-4 bg-coffee-50 rounded-lg mb-4">
                  <div>
                    <p className="text-sm text-coffee-600">Type</p>
                    <p className="font-semibold text-coffee-900 capitalize">{order.order_type}</p>
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

                {order.status === 'approved' && order.invoice_url && (
                  <a
                    href={`${process.env.REACT_APP_BACKEND_URL}${order.invoice_url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800"
                  >
                    <Download className="w-5 h-5" />
                    Download Invoice
                  </a>
                )}
              </div>
            ))}

            {orders.length === 0 && (
              <div className="text-center py-12 text-coffee-700">
                No orders yet
              </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default MyOrdersPage;
