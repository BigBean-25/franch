import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './pages/LandingPage';

// Admin Pages
import SuperAdminDashboard from './pages/admin/SuperAdminDashboard';
import UsersPage from './pages/admin/UsersPage';
import FranchisesPage from './pages/admin/FranchisesPage';
import CategoriesPage from './pages/admin/CategoriesPage';
import ProductsPage from './pages/admin/ProductsPage';
import OrdersPage from './pages/admin/OrdersPage';
import PaymentsPage from './pages/admin/PaymentsPage';
import ReportsPage from './pages/admin/ReportsPage';
import NotificationsPage from './pages/admin/NotificationsPage';
import SettingsPage from './pages/admin/SettingsPage';

// Franchise Portal Pages
import FranchisePortal from './pages/franchise/FranchisePortal';
import BrowseProductsPage from './pages/franchise/BrowseProductsPage';
import CartPage from './pages/franchise/CartPage';
import MyOrdersPage from './pages/franchise/MyOrdersPage';
import PayOutstandingPage from './pages/franchise/PayOutstandingPage';

// Bakehouse Admin Pages
import BakehouseAdmin from './pages/bakehouse/BakehouseAdmin';
import BakehouseCategoriesPage from './pages/bakehouse/CategoriesPage';
import BakehouseProductsPage from './pages/bakehouse/ProductsPage';
import BakehouseOrdersPage from './pages/bakehouse/OrdersPage';

// Merch Admin Pages
import MerchAdmin from './pages/merch/MerchAdmin';
import MerchCategoriesPage from './pages/merch/CategoriesPage';
import MerchProductsPage from './pages/merch/ProductsPage';
import MerchOrdersPage from './pages/merch/OrdersPage';

import './App.css';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-coffee-700"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />

          {/* Super Admin Routes */}
          <Route path="/admin" element={<ProtectedRoute allowedRoles={['super_admin']}><SuperAdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute allowedRoles={['super_admin']}><UsersPage /></ProtectedRoute>} />
          <Route path="/admin/franchises" element={<ProtectedRoute allowedRoles={['super_admin']}><FranchisesPage /></ProtectedRoute>} />
          <Route path="/admin/categories" element={<ProtectedRoute allowedRoles={['super_admin']}><CategoriesPage /></ProtectedRoute>} />
          <Route path="/admin/products" element={<ProtectedRoute allowedRoles={['super_admin']}><ProductsPage /></ProtectedRoute>} />
          <Route path="/admin/orders" element={<ProtectedRoute allowedRoles={['super_admin']}><OrdersPage /></ProtectedRoute>} />
          <Route path="/admin/payments" element={<ProtectedRoute allowedRoles={['super_admin']}><PaymentsPage /></ProtectedRoute>} />
          <Route path="/admin/reports" element={<ProtectedRoute allowedRoles={['super_admin']}><ReportsPage /></ProtectedRoute>} />
          <Route path="/admin/notifications" element={<ProtectedRoute allowedRoles={['super_admin']}><NotificationsPage /></ProtectedRoute>} />
          <Route path="/admin/settings" element={<ProtectedRoute allowedRoles={['super_admin']}><SettingsPage /></ProtectedRoute>} />

          {/* Franchise Portal Routes */}
          <Route path="/portal" element={<ProtectedRoute allowedRoles={['franchise_admin']}><FranchisePortal /></ProtectedRoute>} />
          <Route path="/portal/products" element={<ProtectedRoute allowedRoles={['franchise_admin']}><BrowseProductsPage /></ProtectedRoute>} />
          <Route path="/portal/cart" element={<ProtectedRoute allowedRoles={['franchise_admin']}><CartPage /></ProtectedRoute>} />
          <Route path="/portal/orders" element={<ProtectedRoute allowedRoles={['franchise_admin']}><MyOrdersPage /></ProtectedRoute>} />
          <Route path="/portal/pay-outstanding" element={<ProtectedRoute allowedRoles={['franchise_admin']}><PayOutstandingPage /></ProtectedRoute>} />

          {/* Bakehouse Admin Routes */}
          <Route path="/bakehouse" element={<ProtectedRoute allowedRoles={['bakehouse_admin']}><BakehouseAdmin /></ProtectedRoute>} />
          <Route path="/bakehouse/categories" element={<ProtectedRoute allowedRoles={['bakehouse_admin']}><BakehouseCategoriesPage /></ProtectedRoute>} />
          <Route path="/bakehouse/products" element={<ProtectedRoute allowedRoles={['bakehouse_admin']}><BakehouseProductsPage /></ProtectedRoute>} />
          <Route path="/bakehouse/orders" element={<ProtectedRoute allowedRoles={['bakehouse_admin']}><BakehouseOrdersPage /></ProtectedRoute>} />

          {/* Merch Admin Routes */}
          <Route path="/merch" element={<ProtectedRoute allowedRoles={['merch_admin']}><MerchAdmin /></ProtectedRoute>} />
          <Route path="/merch/categories" element={<ProtectedRoute allowedRoles={['merch_admin']}><MerchCategoriesPage /></ProtectedRoute>} />
          <Route path="/merch/products" element={<ProtectedRoute allowedRoles={['merch_admin']}><MerchProductsPage /></ProtectedRoute>} />
          <Route path="/merch/orders" element={<ProtectedRoute allowedRoles={['merch_admin']}><MerchOrdersPage /></ProtectedRoute>} />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
