import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, ShoppingBag, Package, UserCog } from 'lucide-react';
import Logo from '../components/Logo';

const LandingPage = () => {
  const [selectedPortal, setSelectedPortal] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const portals = [
    {
      id: 'super_admin',
      title: 'Super Admin',
      description: 'Complete system management',
      icon: UserCog,
      color: 'from-coffee-800 to-coffee-900',
    },
    {
      id: 'franchise_admin',
      title: 'Franchise Portal',
      description: 'Order products & manage franchise',
      icon: User,
      color: 'from-coffee-600 to-coffee-700',
    },
    {
      id: 'bakehouse_admin',
      title: 'Bakehouse Admin',
      description: 'Manage bakehouse products & orders',
      icon: Package,
      color: 'from-coffee-700 to-coffee-800',
    },
    {
      id: 'merch_admin',
      title: 'Merch Admin',
      description: 'Manage merchandise & orders',
      icon: ShoppingBag,
      color: 'from-coffee-600 to-coffee-800',
    },
  ];

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const user = await login(email, password);
      
      if (user.role === 'super_admin') {
        navigate('/admin');
      } else if (user.role === 'franchise_admin') {
        navigate('/portal');
      } else if (user.role === 'bakehouse_admin') {
        navigate('/bakehouse');
      } else if (user.role === 'merch_admin') {
        navigate('/merch');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-coffee-50 to-coffee-100">
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-center">
            <Logo className="w-12 h-12 mr-3" />
            <div>
              <h1 className="text-3xl font-bold text-coffee-900">BigBeanCafe</h1>
              <p className="text-coffee-700 text-sm">Franchise Ordering System</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {!selectedPortal ? (
          <div>
            <h2 className="text-4xl font-bold text-center mb-4 text-coffee-900">
              Welcome to BigBeanCafe
            </h2>
            <p className="text-center text-coffee-700 mb-12 text-lg">
              Select your portal to get started
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
              {portals.map((portal) => {
                const Icon = portal.icon;
                return (
                  <div
                    key={portal.id}
                    onClick={() => setSelectedPortal(portal)}
                    data-testid={`${portal.id}-portal-card`}
                    className="group cursor-pointer transform transition-all duration-300 hover:scale-105"
                  >
                    <div className={`bg-gradient-to-br ${portal.color} rounded-xl p-8 shadow-lg h-full flex flex-col items-center justify-center text-white hover:shadow-2xl`}>
                      <Icon className="w-16 h-16 mb-4 group-hover:scale-110 transition-transform" />
                      <h3 className="text-2xl font-bold mb-2 text-center">{portal.title}</h3>
                      <p className="text-center text-white/90 text-sm">{portal.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="max-w-md mx-auto">
            <div className={`bg-gradient-to-br ${selectedPortal.color} rounded-t-xl p-6 text-white text-center`}>
              {React.createElement(selectedPortal.icon, { className: 'w-16 h-16 mx-auto mb-3' })}
              <h2 className="text-3xl font-bold">{selectedPortal.title}</h2>
              <p className="mt-2 text-white/90">{selectedPortal.description}</p>
            </div>

            <div className="bg-white rounded-b-xl shadow-xl p-8">
              <form onSubmit={handleLogin} className="space-y-6">
                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded" data-testid="error-message">
                    {error}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    data-testid="email-input"
                    className="w-full px-4 py-3 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
                    placeholder="Enter your email"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-coffee-800 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    data-testid="password-input"
                    className="w-full px-4 py-3 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
                    placeholder="Enter your password"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  data-testid="login-button"
                  className={`w-full bg-gradient-to-r ${selectedPortal.color} text-white py-3 px-4 rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-50`}
                >
                  {loading ? 'Logging in...' : 'Login'}
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setSelectedPortal(null);
                    setEmail('');
                    setPassword('');
                    setError('');
                  }}
                  className="w-full text-coffee-700 py-2 hover:text-coffee-900 transition-colors"
                >
                  Back to Portal Selection
                </button>
              </form>
            </div>
          </div>
        )}
      </main>

      <footer className="bg-coffee-900 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2025 BigBeanCafe. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;