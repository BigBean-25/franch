import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell, Plus, Edit, Trash2 } from 'lucide-react';
import api from '../../services/api';

const CategoriesPage = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({ name: '', type: 'bakehouse', description: '' });
  const [editingId, setEditingId] = useState(null);

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
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories');
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/categories/${editingId}`, formData);
      } else {
        await api.post('/categories', formData);
      }
      fetchCategories();
      setFormData({ name: '', type: 'bakehouse', description: '' });
      setEditingId(null);
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to save category');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this category?')) {
      try {
        await api.delete(`/categories/${id}`);
        fetchCategories();
      } catch (error) {
        alert('Failed to delete category');
      }
    }
  };

  const handleEdit = (category) => {
    setFormData({ name: category.name, type: category.type, description: category.description || '' });
    setEditingId(category.id);
  };

  const bakehouseCategories = categories.filter(c => c.type === 'bakehouse');
  const merchCategories = categories.filter(c => c.type === 'merch');

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Categories Management</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <h2 className="text-xl font-bold text-coffee-900 mb-4">{editingId ? 'Edit' : 'Add'} Category</h2>
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
                <label className="block text-sm font-medium text-coffee-800 mb-1">Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                >
                  <option value="bakehouse">Bakehouse</option>
                  <option value="merch">Merchandise</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-coffee-800 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  rows="3"
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800"
                >
                  {editingId ? 'Update' : 'Create'}
                </button>
                {editingId && (
                  <button
                    type="button"
                    onClick={() => { setEditingId(null); setFormData({ name: '', type: 'bakehouse', description: '' }); }}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <h2 className="text-xl font-bold text-coffee-900 mb-4 flex items-center gap-2">
              <Package className="w-6 h-6 text-coffee-700" />
              Bakehouse Categories ({bakehouseCategories.length})
            </h2>
            <div className="space-y-2">
              {bakehouseCategories.map((cat) => (
                <div key={cat.id} className="flex justify-between items-center p-3 bg-coffee-50 rounded-lg">
                  <div>
                    <p className="font-semibold text-coffee-900">{cat.name}</p>
                    {cat.description && <p className="text-sm text-coffee-700">{cat.description}</p>}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleEdit(cat)} className="text-coffee-600 hover:text-coffee-800">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete(cat.id)} className="text-red-600 hover:text-red-800">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <h2 className="text-xl font-bold text-coffee-900 mb-4 flex items-center gap-2">
              <ShoppingBag className="w-6 h-6 text-coffee-700" />
              Merch Categories ({merchCategories.length})
            </h2>
            <div className="space-y-2">
              {merchCategories.map((cat) => (
                <div key={cat.id} className="flex justify-between items-center p-3 bg-coffee-50 rounded-lg">
                  <div>
                    <p className="font-semibold text-coffee-900">{cat.name}</p>
                    {cat.description && <p className="text-sm text-coffee-700">{cat.description}</p>}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleEdit(cat)} className="text-coffee-600 hover:text-coffee-800">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete(cat.id)} className="text-red-600 hover:text-red-800">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default CategoriesPage;
