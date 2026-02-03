import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell, Plus, Edit, Trash2, X } from 'lucide-react';
import api from '../../services/api';

const FranchisesPage = () => {
  const [franchises, setFranchises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingFranchise, setEditingFranchise] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    owner_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    gstin: ''
  });

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
    fetchFranchises();
  }, []);

  const fetchFranchises = async () => {
    try {
      const response = await api.get('/franchises');
      setFranchises(response.data);
    } catch (error) {
      console.error('Failed to fetch franchises:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingFranchise) {
        await api.put(`/franchises/${editingFranchise.id}`, formData);
      } else {
        await api.post('/franchises', formData);
      }
      fetchFranchises();
      setShowModal(false);
      resetForm();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to save franchise');
    }
  };

  const handleDelete = async (franchiseId) => {
    if (window.confirm('Are you sure you want to delete this franchise?')) {
      try {
        await api.delete(`/franchises/${franchiseId}`);
        fetchFranchises();
      } catch (error) {
        alert('Failed to delete franchise');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      owner_name: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      pincode: '',
      gstin: ''
    });
    setEditingFranchise(null);
  };

  const openEditModal = (franchise) => {
    setEditingFranchise(franchise);
    setFormData({
      name: franchise.name,
      owner_name: franchise.owner_name,
      email: franchise.email,
      phone: franchise.phone,
      address: franchise.address,
      city: franchise.city,
      state: franchise.state,
      pincode: franchise.pincode,
      gstin: franchise.gstin || ''
    });
    setShowModal(true);
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-coffee-900">Franchises Management</h1>
          <button
            onClick={() => { resetForm(); setShowModal(true); }}
            className="flex items-center gap-2 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Add Franchise
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {franchises.map((franchise) => (
              <div key={franchise.id} className="bg-white rounded-lg shadow p-6 border border-coffee-200">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-coffee-900">{franchise.name}</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => openEditModal(franchise)}
                      className="text-coffee-600 hover:text-coffee-800"
                    >
                      <Edit className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(franchise.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <p className="text-coffee-700"><strong>Owner:</strong> {franchise.owner_name}</p>
                  <p className="text-coffee-700"><strong>Email:</strong> {franchise.email}</p>
                  <p className="text-coffee-700"><strong>Phone:</strong> {franchise.phone}</p>
                  <p className="text-coffee-700"><strong>Location:</strong> {franchise.city}, {franchise.state}</p>
                  <div className="pt-4 border-t border-coffee-200">
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <p className="text-xs text-coffee-600">Credit Limit</p>
                        <p className="font-bold text-coffee-900">₹{franchise.credit_limit.toLocaleString('en-IN')}</p>
                      </div>
                      <div>
                        <p className="text-xs text-coffee-600">Available</p>
                        <p className={`font-bold ${franchise.available_credit <= 0 ? 'text-red-600' : 'text-green-600'}`}>
                          ₹{franchise.available_credit.toLocaleString('en-IN')}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-coffee-900">
                  {editingFranchise ? 'Edit Franchise' : 'Add Franchise'}
                </h2>
                <button onClick={() => { setShowModal(false); resetForm(); }}>
                  <X className="w-6 h-6 text-coffee-700" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Franchise Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Owner Name</label>
                    <input
                      type="text"
                      value={formData.owner_name}
                      onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Phone</label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Address</label>
                  <textarea
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    rows="2"
                    required
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">City</label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">State</label>
                    <input
                      type="text"
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Pincode</label>
                    <input
                      type="text"
                      value={formData.pincode}
                      onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">GSTIN (Optional)</label>
                  <input
                    type="text"
                    value={formData.gstin}
                    onChange={(e) => setFormData({ ...formData, gstin: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  />
                </div>

                <div className="flex gap-2 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800 transition-colors"
                  >
                    {editingFranchise ? 'Update' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => { setShowModal(false); resetForm(); }}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default FranchisesPage;
