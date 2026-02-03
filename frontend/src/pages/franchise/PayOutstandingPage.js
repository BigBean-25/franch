import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, ShoppingBag, ShoppingCart, Package, CreditCard } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const PayOutstandingPage = () => {
  const { user } = useAuth();
  const [franchise, setFranchise] = useState(null);
  const [loading, setLoading] = useState(true);

  const navigation = [
    { label: 'Dashboard', path: '/portal', icon: LayoutDashboard },
    { label: 'Browse Products', path: '/portal/products', icon: ShoppingBag },
    { label: 'Cart', path: '/portal/cart', icon: ShoppingCart },
    { label: 'My Orders', path: '/portal/orders', icon: Package },
    { label: 'Pay Outstanding', path: '/portal/pay-outstanding', icon: CreditCard },
  ];

  useEffect(() => {
    fetchFranchise();
  }, []);

  const fetchFranchise = async () => {
    try {
      const response = await api.get(`/franchises/${user.franchise_id}`);
      setFranchise(response.data);
    } catch (error) {
      console.error('Failed to fetch franchise:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    try {
      // This would integrate with Razorpay in production
      alert('Razorpay payment integration pending. Please configure Razorpay keys in Settings.');
    } catch (error) {
      alert('Failed to initiate payment');
    }
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Pay Outstanding</h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow p-8 border border-coffee-200">
              <div className="text-center mb-8">
                <p className="text-coffee-700 mb-2">Outstanding Amount</p>
                <p className="text-5xl font-bold text-red-600">₹{franchise?.used_credit.toLocaleString('en-IN')}</p>
              </div>

              <div className="space-y-4 mb-8">
                <div className="flex justify-between py-3 border-b border-coffee-200">
                  <span className="text-coffee-700">Credit Limit</span>
                  <span className="font-semibold text-coffee-900">₹{franchise?.credit_limit.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-3 border-b border-coffee-200">
                  <span className="text-coffee-700">Used Credit</span>
                  <span className="font-semibold text-red-600">₹{franchise?.used_credit.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-3">
                  <span className="text-coffee-700">Available Credit</span>
                  <span className={`font-semibold ${franchise?.available_credit <= 0 ? 'text-red-600' : 'text-green-600'}`}>
                    ₹{franchise?.available_credit.toLocaleString('en-IN')}
                  </span>
                </div>
              </div>

              <div className="bg-coffee-50 rounded-lg p-4 mb-6">
                <h3 className="font-bold text-coffee-900 mb-2">Payment Information</h3>
                <p className="text-sm text-coffee-700">
                  • Payment amount is fixed at ₹1,00,000<br />
                  • Your credit will be reset after successful payment<br />
                  • Payment is processed through Razorpay
                </p>
              </div>

              {franchise?.available_credit <= 0 && (
                <button
                  onClick={handlePayment}
                  className="w-full px-6 py-4 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800 font-semibold text-lg"
                >
                  Pay ₹1,00,000 Now
                </button>
              )}

              {franchise?.available_credit > 0 && (
                <div className="text-center text-green-600 font-semibold">
                  ✓ You have sufficient credit available
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default PayOutstandingPage;
