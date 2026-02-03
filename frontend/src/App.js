import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import SuperAdminDashboard from './pages/admin/SuperAdminDashboard';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
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

// Placeholder components for routes (to be implemented)
const UsersPage = () => <div>Users Management - Coming Soon</div>;
const FranchisesPage = () => <div>Franchises Management - Coming Soon</div>;
const CategoriesPage = () => <div>Categories Management - Coming Soon</div>;
const ProductsPage = () => <div>Products Management - Coming Soon</div>;
const OrdersPage = () => <div>Orders Management - Coming Soon</div>;
const PaymentsPage = () => <div>Payments Management - Coming Soon</div>;
const ReportsPage = () => <div>Reports - Coming Soon</div>;
const NotificationsPage = () => <div>Notifications - Coming Soon</div>;
const SettingsPage = () => <div>Settings - Coming Soon</div>;

// Franchise Portal Pages
const FranchisePortal = () => <div>Franchise Portal - Coming Soon</div>;

// Bakehouse Admin Pages
const BakehouseAdmin = () => <div>Bakehouse Admin - Coming Soon</div>;

// Merch Admin Pages
const MerchAdmin = () => <div>Merch Admin - Coming Soon</div>;

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />

          {/* Super Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <SuperAdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <UsersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/franchises"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <FranchisesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/categories"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <CategoriesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/products"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <ProductsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/orders"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <OrdersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/payments"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <PaymentsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/reports"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <ReportsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/notifications"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <NotificationsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/settings"
            element={
              <ProtectedRoute allowedRoles={['super_admin']}>
                <SettingsPage />
              </ProtectedRoute>
            }
          />

          {/* Franchise Portal Routes */}
          <Route
            path="/portal/*"
            element={
              <ProtectedRoute allowedRoles={['franchise_admin']}>
                <FranchisePortal />
              </ProtectedRoute>
            }
          />

          {/* Bakehouse Admin Routes */}
          <Route
            path="/bakehouse/*"
            element={
              <ProtectedRoute allowedRoles={['bakehouse_admin']}>
                <BakehouseAdmin />
              </ProtectedRoute>
            }
          />

          {/* Merch Admin Routes */}
          <Route
            path="/merch/*"
            element={
              <ProtectedRoute allowedRoles={['merch_admin']}>
                <MerchAdmin />
              </ProtectedRoute>
            }
          />

          {/* 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
