import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, FolderOpen, Package, ShoppingCart, Edit, Trash2 } from 'lucide-react';
import api from '../../services/api';

const CategoriesPage = () => {
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [editingId, setEditingId] = useState(null);

  const navigation = [
    { label: 'Dashboard', path: '/merch', icon: LayoutDashboard },
    { label: 'Categories', path: '/merch/categories', icon: FolderOpen },
    { label: 'Products', path: '/merch/products', icon: Package },
    { label: 'Orders', path: '/merch/orders', icon: ShoppingCart },
  ];

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories?type=merch');
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...formData, type: 'merch' };
      if (editingId) {
        await api.put(`/categories/${editingId}`, data);
      } else {
        await api.post('/categories', data);
      }
      fetchCategories();
      setFormData({ name: '', description: '' });
      setEditingId(null);
    } catch (error) {
      alert('Failed to save category');
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

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Merch Categories</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
                <label className="block text-sm font-medium text-coffee-800 mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                  rows="3"
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" className="flex-1 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800">
                  {editingId ? 'Update' : 'Create'}
                </button>
                {editingId && (
                  <button type="button" onClick={() => { setEditingId(null); setFormData({ name: '', description: '' }); }} className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg">
                    Cancel
                  </button>
                )}
              </div>
            </form>
          </div>

          <div className="bg-white rounded-lg shadow p-6 border border-coffee-200">
            <h2 className="text-xl font-bold text-coffee-900 mb-4">Categories ({categories.length})</h2>
            <div className="space-y-2">
              {categories.map((cat) => (
                <div key={cat.id} className="flex justify-between items-center p-3 bg-coffee-50 rounded-lg">
                  <div>
                    <p className="font-semibold text-coffee-900">{cat.name}</p>
                    {cat.description && <p className="text-sm text-coffee-700">{cat.description}</p>}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => { setFormData({ name: cat.name, description: cat.description || '' }); setEditingId(cat.id); }} className="text-coffee-600">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete(cat.id)} className="text-red-600">
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
