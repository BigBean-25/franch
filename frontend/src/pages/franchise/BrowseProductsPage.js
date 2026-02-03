import React, { useEffect, useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { LayoutDashboard, ShoppingBag, ShoppingCart, Package, CreditCard, Plus } from 'lucide-react';
import api from '../../services/api';

const BrowseProductsPage = () => {
  const [products, setProducts] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  const navigation = [
    { label: 'Dashboard', path: '/portal', icon: LayoutDashboard },
    { label: 'Browse Products', path: '/portal/products', icon: ShoppingBag },
    { label: 'Cart', path: '/portal/cart', icon: ShoppingCart },
    { label: 'My Orders', path: '/portal/orders', icon: Package },
    { label: 'Pay Outstanding', path: '/portal/pay-outstanding', icon: CreditCard },
  ];

  useEffect(() => {
    fetchProducts();
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

  const addToCart = async (productId) => {
    try {
      await api.post('/cart', { product_id: productId, quantity: 1 });
      alert('Added to cart!');
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to add to cart');
    }
  };

  const filteredProducts = filter === 'all' ? products : products.filter(p => p.category_type === filter);

  return (
    <DashboardLayout navigation={navigation}>
      <div>
        <h1 className="text-3xl font-bold text-coffee-900 mb-6">Browse Products</h1>

        <div className="flex gap-2 mb-6">
          {['all', 'bakehouse', 'merch'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg capitalize ${filter === f ? 'bg-coffee-700 text-white' : 'bg-white text-coffee-900 border border-coffee-200'}`}
            >
              {f === 'all' ? 'All Products' : f}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700 mx-auto"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProducts.map((product) => {
              const finalPrice = product.offer_price || product.original_price;
              return (
                <div key={product.id} className="bg-white rounded-lg shadow overflow-hidden border border-coffee-200">
                  {product.image_url && (
                    <img 
                      src={product.image_url} 
                      alt={product.name} 
                      className="w-full h-48 object-cover" 
                      onError={(e) => {e.target.style.display='none'}}
                    />
                  )}
                  <div className="p-6">
                    <span className={`px-2 py-1 text-xs rounded-full ${product.category_type === 'bakehouse' ? 'bg-coffee-200 text-coffee-900' : 'bg-green-200 text-green-900'}`}>
                      {product.category_type}
                    </span>
                    <h3 className="text-xl font-bold text-coffee-900 mt-3">{product.name}</h3>
                    <p className="text-sm text-coffee-700 mt-2 line-clamp-2">{product.description}</p>
                    <div className="mt-4">
                      {product.offer_price && (
                        <p className="text-sm text-gray-500 line-through">₹{product.original_price}</p>
                      )}
                      <p className="text-2xl font-bold text-coffee-900">₹{finalPrice}</p>
                      <p className="text-xs text-coffee-600">+ {product.gst_percent}% GST (incl. SGST+CGST)</p>
                    </div>
                    <button
                      onClick={() => addToCart(product.id)}
                      className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800"
                    >
                      <Plus className="w-4 h-4" />
                      Add to Cart
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default BrowseProductsPage;
