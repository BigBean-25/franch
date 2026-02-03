import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell, Plus, Edit, Trash2, X } from 'lucide-react';
import api from '../../services/api';

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const [franchises, setFranchises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    role: 'franchise_admin',
    franchise_id: ''
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
    fetchUsers();
    fetchFranchises();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFranchises = async () => {
    try {
      const response = await api.get('/franchises');
      setFranchises(response.data);
    } catch (error) {
      console.error('Failed to fetch franchises:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        const { password, ...updateData } = formData;
        await api.put(`/users/${editingUser.id}`, updateData);
      } else {
        await api.post('/auth/register', formData);
      }
      fetchUsers();
      setShowModal(false);
      resetForm();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to save user');
    }
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        await api.delete(`/users/${userId}`);
        fetchUsers();
      } catch (error) {
        alert('Failed to delete user');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      name: '',
      role: 'franchise_admin',
      franchise_id: ''
    });
    setEditingUser(null);
  };

  const openEditModal = (user) => {
    setEditingUser(user);
    setFormData({
      email: user.email,
      password: '',
      name: user.name,
      role: user.role,
      franchise_id: user.franchise_id || ''
    });
    setShowModal(true);
  };

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-coffee-900">Users Management</h1>
          <button
            onClick={() => { resetForm(); setShowModal(true); }}
            className="flex items-center gap-2 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800 transition-colors"
            data-testid="add-user-button"
          >
            <Plus className="w-5 h-5" />
            Add User
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow border border-coffee-200">
            <table className="w-full">
              <thead className="bg-coffee-100 border-b border-coffee-200">
                <tr>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Name</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Email</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Role</th>
                  <th className="text-left px-6 py-3 text-coffee-900 font-semibold">Status</th>
                  <th className="text-right px-6 py-3 text-coffee-900 font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-coffee-100 hover:bg-coffee-50">
                    <td className="px-6 py-4 text-coffee-900">{user.name}</td>
                    <td className="px-6 py-4 text-coffee-700">{user.email}</td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 bg-coffee-200 text-coffee-900 rounded-full text-sm">
                        {user.role.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-sm ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => openEditModal(user)}
                        className="text-coffee-600 hover:text-coffee-800 mr-3"
                      >
                        <Edit className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDelete(user.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-coffee-900">
                  {editingUser ? 'Edit User' : 'Add User'}
                </h2>
                <button onClick={() => { setShowModal(false); resetForm(); }}>
                  <X className="w-6 h-6 text-coffee-700" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    required
                    disabled={!!editingUser}
                  />
                </div>

                {!editingUser && (
                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Password</label>
                    <input
                      type="password"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Role</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  >
                    <option value="super_admin">Super Admin</option>
                    <option value="franchise_admin">Franchise Admin</option>
                    <option value="bakehouse_admin">Bakehouse Admin</option>
                    <option value="merch_admin">Merch Admin</option>
                  </select>
                </div>

                {formData.role === 'franchise_admin' && (
                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Franchise</label>
                    <select
                      value={formData.franchise_id}
                      onChange={(e) => setFormData({ ...formData, franchise_id: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    >
                      <option value="">Select Franchise</option>
                      {franchises.map((f) => (
                        <option key={f.id} value={f.id}>{f.name}</option>
                      ))}
                    </select>
                  </div>
                )}

                <div className="flex gap-2 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800 transition-colors"
                  >
                    {editingUser ? 'Update' : 'Create'}
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

export default UsersPage;
