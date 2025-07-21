/**
 * App.jsx - Main Application Component
 * Compatible with Flask JWT backend
 */

import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { apiUtils } from './services/api';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = apiUtils.isAuthenticated();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Public Route Component (redirect if already authenticated)
const PublicRoute = ({ children }) => {
  const isAuthenticated = apiUtils.isAuthenticated();
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Initialize app
    const initializeApp = async () => {
      try {
        // Check if user is already authenticated
        const token = apiUtils.isAuthenticated();
        if (token) {
          // Validate token by making a test request
          // This will automatically handle token refresh if needed
          // If token is invalid, the interceptor will redirect to login
        }
      } catch (error) {
        console.error('App initialization error:', error);
        // Clear invalid tokens
        apiUtils.clearAll();
      } finally {
        setLoading(false);
      }
    };

    initializeApp();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading AI Agent System...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } 
          />
          
          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Default Route */}
          <Route 
            path="/" 
            element={
              apiUtils.isAuthenticated() ? 
                <Navigate to="/dashboard" replace /> : 
                <Navigate to="/login" replace />
            } 
          />
          
          {/* Catch All Route */}
          <Route 
            path="*" 
            element={
              <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                  <p className="text-gray-600 mb-4">Page not found</p>
                  <button 
                    onClick={() => window.location.href = '/dashboard'}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Go to Dashboard
                  </button>
                </div>
              </div>
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

