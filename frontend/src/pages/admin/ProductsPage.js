import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, Users, Store, FolderOpen, Package, ShoppingCart, CreditCard, Settings, FileText, Bell, Plus, Edit, Trash2, X } from 'lucide-react';
import api from '../../services/api';

const ProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [filter, setFilter] = useState('all');
  const [formData, setFormData] = useState({
    name: '',
    category_id: '',
    category_type: 'bakehouse',
    description: '',
    original_price: '',
    offer_price: '',
    gst_percent: '18',
    unit: 'piece'
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
    fetchProducts();
    fetchCategories();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories');
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        original_price: parseFloat(formData.original_price),
        offer_price: formData.offer_price ? parseFloat(formData.offer_price) : null,
        gst_percent: parseFloat(formData.gst_percent)
      };
      
      if (editingProduct) {
        await api.put(`/products/${editingProduct.id}`, data);
      } else {
        await api.post('/products', data);
      }
      fetchProducts();
      setShowModal(false);
      resetForm();
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to save product');
    }
  };

  const handleDelete = async (productId) => {
    if (window.confirm('Delete this product?')) {
      try {
        await api.delete(`/products/${productId}`);
        fetchProducts();
      } catch (error) {
        alert('Failed to delete product');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      category_id: '',
      category_type: 'bakehouse',
      description: '',
      original_price: '',
      offer_price: '',
      gst_percent: '18',
      unit: 'piece'
    });
    setEditingProduct(null);
  };

  const openEditModal = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      category_id: product.category_id,
      category_type: product.category_type,
      description: product.description || '',
      original_price: product.original_price.toString(),
      offer_price: product.offer_price?.toString() || '',
      gst_percent: product.gst_percent.toString(),
      unit: product.unit
    });
    setShowModal(true);
  };

  const filteredProducts = filter === 'all' ? products : products.filter(p => p.category_type === filter);

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-coffee-900">Products Management</h1>
          <button
            onClick={() => { resetForm(); setShowModal(true); }}
            className="flex items-center gap-2 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800"
          >
            <Plus className="w-5 h-5" />
            Add Product
          </button>
        </div>

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg ${filter === 'all' ? 'bg-coffee-700 text-white' : 'bg-white text-coffee-900 border border-coffee-200'}`}
          >
            All Products
          </button>
          <button
            onClick={() => setFilter('bakehouse')}
            className={`px-4 py-2 rounded-lg ${filter === 'bakehouse' ? 'bg-coffee-700 text-white' : 'bg-white text-coffee-900 border border-coffee-200'}`}
          >
            Bakehouse
          </button>
          <button
            onClick={() => setFilter('merch')}
            className={`px-4 py-2 rounded-lg ${filter === 'merch' ? 'bg-coffee-700 text-white' : 'bg-white text-coffee-900 border border-coffee-200'}`}
          >
            Merchandise
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredProducts.map((product) => {
              const finalPrice = product.offer_price || product.original_price;
              return (
                <div key={product.id} className="bg-white rounded-lg shadow p-4 border border-coffee-200">
                  <div className="flex justify-between items-start mb-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${product.category_type === 'bakehouse' ? 'bg-coffee-200 text-coffee-900' : 'bg-green-200 text-green-900'}`}>
                      {product.category_type}
                    </span>
                    <div className="flex gap-1">
                      <button onClick={() => openEditModal(product)} className="text-coffee-600 hover:text-coffee-800">
                        <Edit className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleDelete(product.id)} className="text-red-600 hover:text-red-800">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-coffee-900 mb-1">{product.name}</h3>
                  <p className="text-sm text-coffee-700 mb-2">{product.description}</p>
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-coffee-700 text-sm">
                        {product.offer_price && (
                          <span className="line-through mr-2">₹{product.original_price}</span>
                        )}
                        <span className="text-lg font-bold text-coffee-900">₹{finalPrice}</span>
                      </p>
                      <p className="text-xs text-coffee-600">GST: {product.gst_percent}%</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-lg">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-coffee-900">
                  {editingProduct ? 'Edit Product' : 'Add Product'}
                </h2>
                <button onClick={() => { setShowModal(false); resetForm(); }}>
                  <X className="w-6 h-6 text-coffee-700" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Product Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Type</label>
                    <select
                      value={formData.category_type}
                      onChange={(e) => setFormData({ ...formData, category_type: e.target.value, category_id: '' })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    >
                      <option value="bakehouse">Bakehouse</option>
                      <option value="merch">Merchandise</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Category</label>
                    <select
                      value={formData.category_id}
                      onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    >
                      <option value="">Select Category</option>
                      {categories.filter(c => c.type === formData.category_type).map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-1">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    rows="2"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Original Price</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.original_price}
                      onChange={(e) => setFormData({ ...formData, original_price: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">Offer Price</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.offer_price}
                      onChange={(e) => setFormData({ ...formData, offer_price: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-coffee-800 mb-1">GST %</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.gst_percent}
                      onChange={(e) => setFormData({ ...formData, gst_percent: e.target.value })}
                      className="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500"
                      required
                    />
                  </div>
                </div>

                <div className="flex gap-2 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800"
                  >
                    {editingProduct ? 'Update' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => { setShowModal(false); resetForm(); }}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
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

export default ProductsPage;
