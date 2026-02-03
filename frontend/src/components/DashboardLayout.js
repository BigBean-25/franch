import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut } from 'lucide-react';
import Logo from './Logo';

const DashboardLayout = ({ children, navigation }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="min-h-screen bg-coffee-50">
      <header className="bg-white shadow-md border-b-2 border-coffee-200">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center">
            <Logo className="w-10 h-10 mr-3" />
            <div>
              <h1 className="text-2xl font-bold text-coffee-900">BigBeanCafe</h1>
              <p className="text-xs text-coffee-700">{user?.name || 'User'}</p>
            </div>
          </div>
          <button
            onClick={logout}
            data-testid="logout-button"
            className="flex items-center gap-2 px-4 py-2 bg-coffee-700 text-white rounded-lg hover:bg-coffee-800 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </header>

      <div className="flex">
        {navigation && navigation.length > 0 && (
          <aside className="w-64 bg-white shadow-md min-h-screen border-r-2 border-coffee-200">
            <nav className="p-4 space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <button
                    key={item.path}
                    onClick={() => navigate(item.path)}
                    data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-coffee-700 text-white font-semibold'
                        : 'text-coffee-800 hover:bg-coffee-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {item.label}
                  </button>
                );
              })}
            </nav>
          </aside>
        )}

        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;