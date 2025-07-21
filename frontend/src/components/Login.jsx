/**
 * Login Component - User Authentication
 * Compatible with Flask JWT backend
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { Loader2, LogIn, User, Lock, Bot } from 'lucide-react';
import { authAPI, apiUtils } from '../services/api';
import '../App.css';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      setError('Please enter both username and password');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(formData.username, formData.password);
      
      if (response.status === 'success') {
        // Login successful, redirect to dashboard
        navigate('/dashboard');
      } else {
        setError(response.message || 'Login failed');
      }
    } catch (error) {
      const errorInfo = apiUtils.handleError(error);
      setError(errorInfo.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (username, password) => {
    setFormData({ username, password });
    setLoading(true);
    setError('');

    try {
      const response = await authAPI.login(username, password);
      
      if (response.status === 'success') {
        navigate('/dashboard');
      } else {
        setError(response.message || 'Demo login failed');
      }
    } catch (error) {
      const errorInfo = apiUtils.handleError(error);
      setError(errorInfo.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-blue-600 p-3 rounded-full">
              <Bot className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Agent System</h1>
          <p className="text-gray-600">Intelligent Task Management Platform</p>
        </div>

        {/* Login Form */}
        <Card className="shadow-lg">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Sign In</CardTitle>
            <CardDescription className="text-center">
              Enter your credentials to access the dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Username Field */}
              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium text-gray-700">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="username"
                    name="username"
                    type="text"
                    placeholder="Enter your username"
                    value={formData.username}
                    onChange={handleInputChange}
                    className="pl-10"
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="pl-10"
                    disabled={loading}
                    required
                  />
                </div>
              </div>

              {/* Error Alert */}
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Login Button */}
              <Button
                type="submit"
                className="w-full"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing In...
                  </>
                ) : (
                  <>
                    <LogIn className="mr-2 h-4 w-4" />
                    Sign In
                  </>
                )}
              </Button>
            </form>

            {/* Demo Accounts */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600 text-center mb-4">
                Demo Accounts (Click to login)
              </p>
              
              <div className="space-y-2">
                {/* Admin Demo */}
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => handleDemoLogin('admin', 'admin123')}
                  disabled={loading}
                >
                  <div className="flex items-center">
                    <div className="bg-red-100 p-1 rounded mr-3">
                      <User className="h-4 w-4 text-red-600" />
                    </div>
                    <div className="text-left">
                      <div className="font-medium">Admin Account</div>
                      <div className="text-xs text-gray-500">Full system access</div>
                    </div>
                  </div>
                </Button>

                {/* Team Member Demo */}
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => handleDemoLogin('john_doe', 'user123')}
                  disabled={loading}
                >
                  <div className="flex items-center">
                    <div className="bg-blue-100 p-1 rounded mr-3">
                      <User className="h-4 w-4 text-blue-600" />
                    </div>
                    <div className="text-left">
                      <div className="font-medium">Team Member</div>
                      <div className="text-xs text-gray-500">Task management access</div>
                    </div>
                  </div>
                </Button>
              </div>
            </div>

            {/* Features */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600 text-center mb-3">
                System Features
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                  AI Task Generation
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mr-2"></div>
                  Performance Tracking
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mr-2"></div>
                  Telegram Notifications
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-orange-400 rounded-full mr-2"></div>
                  Kanban Board
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-6 text-sm text-gray-500">
          <p>AI Agent System v2.0</p>
          <p>Compatible with Python 3.10 & Windows 10</p>
        </div>
      </div>
    </div>
  );
};

export default Login;

