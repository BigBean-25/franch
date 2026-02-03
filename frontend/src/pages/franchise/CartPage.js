import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, ShoppingBag, ShoppingCart, Package, CreditCard, Trash2, Plus, Minus } from 'lucide-react';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';

const CartPage = () => {
  const navigate = useNavigate();
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const navigation = [
    { label: 'Dashboard', path: '/portal', icon: LayoutDashboard },
    { label: 'Browse Products', path: '/portal/products', icon: ShoppingBag },
    { label: 'Cart', path: '/portal/cart', icon: ShoppingCart },
    { label: 'My Orders', path: '/portal/orders', icon: Package },
    { label: 'Pay Outstanding', path: '/portal/pay-outstanding', icon: CreditCard },
  ];

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    try {
      const response = await api.get('/cart');
      setCartItems(response.data);
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId, newQuantity) => {
    if (newQuantity <= 0) {
      removeItem(itemId);
      return;
    }
    try {
      await api.put(`/cart/${itemId}?quantity=${newQuantity}`);
      fetchCart();
    } catch (error) {
      alert('Failed to update quantity');
    }
  };

  const removeItem = async (itemId) => {
    try {
      await api.delete(`/cart/${itemId}`);
      fetchCart();
    } catch (error) {
      alert('Failed to remove item');
    }
  };

  const placeOrder = async () => {
    if (cartItems.length === 0) {
      alert('Cart is empty');
      return;
    }

    const orderType = cartItems[0]?.product_id ? 'bakehouse' : 'merch';
    
    try {
      await api.post('/orders', { order_type: orderType, remarks: '' });
      alert('Order placed successfully!');
      navigate('/portal/orders');
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to place order');
    }
  };

  const calculateTotal = () => {
    let subtotal = 0;
    let gst = 0;
    cartItems.forEach(item => {
      const taxable = item.quantity * item.unit_price;
      subtotal += taxable;
      gst += taxable * (item.gst_percent / 100);
    });
    return { subtotal, gst, total: subtotal + gst };
  };

  const totals = calculateTotal();

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Shopping Cart</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : cartItems.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center border border-coffee-200">
            <ShoppingCart className="w-16 h-16 text-coffee-400 mx-auto mb-4" />
            <p className="text-coffee-700 text-lg mb-4">Your cart is empty</p>
            <button
              onClick={() => navigate('/portal/products')}
              className="px-6 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800"
            >
              Browse Products
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              {cartItems.map((item) => (
                <div key={item.id} className="bg-white rounded-lg shadow p-4 border border-coffee-200 flex justify-between items-center">
                  <div className="flex-1">
                    <h3 className="font-bold text-coffee-900">{item.product_name}</h3>
                    <p className="text-coffee-700">₹{item.unit_price} × {item.quantity}</p>
                    <p className="text-sm text-coffee-600">GST: {item.gst_percent}%</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="p-1 bg-coffee-100 rounded hover:bg-coffee-200"
                      >
                        <Minus className="w-4 h-4 text-coffee-900" />
                      </button>
                      <span className="w-8 text-center font-semibold text-coffee-900">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="p-1 bg-coffee-100 rounded hover:bg-coffee-200"
                      >
                        <Plus className="w-4 h-4 text-coffee-900" />
                      </button>
                    </div>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-white rounded-lg shadow p-6 border border-coffee-200 h-fit">
              <h2 className="text-xl font-bold text-coffee-900 mb-4">Order Summary</h2>
              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-coffee-700">
                  <span>Subtotal</span>
                  <span>₹{totals.subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-coffee-700">
                  <span>GST</span>
                  <span>₹{totals.gst.toFixed(2)}</span>
                </div>
                <div className="border-t border-coffee-200 pt-2 flex justify-between text-xl font-bold text-coffee-900">
                  <span>Total</span>
                  <span>₹{totals.total.toFixed(2)}</span>
                </div>
              </div>
              <button
                onClick={placeOrder}
                className="w-full px-4 py-3 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800 font-semibold"
              >
                Place Order
              </button>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default CartPage;
