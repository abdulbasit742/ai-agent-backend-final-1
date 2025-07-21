/**
 * API Service - Backend Communication
 * Compatible with Python 3.10 Flask backend
 */

import axios from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const TOKEN_KEY = 'ai_agent_token';
const REFRESH_TOKEN_KEY = 'ai_agent_refresh_token';
const USER_KEY = 'ai_agent_user';

export const tokenManager = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  setToken: (token) => localStorage.setItem(TOKEN_KEY, token),
  removeToken: () => localStorage.removeItem(TOKEN_KEY),
  
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setRefreshToken: (token) => localStorage.setItem(REFRESH_TOKEN_KEY, token),
  removeRefreshToken: () => localStorage.removeItem(REFRESH_TOKEN_KEY),
  
  getUser: () => {
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  },
  setUser: (user) => localStorage.setItem(USER_KEY, JSON.stringify(user)),
  removeUser: () => localStorage.removeItem(USER_KEY),
  
  clearAll: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = tokenManager.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = tokenManager.getRefreshToken();
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: {
              Authorization: `Bearer ${refreshToken}`
            }
          });
          
          const { access_token } = response.data;
          tokenManager.setToken(access_token);
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          tokenManager.clearAll();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        tokenManager.clearAll();
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    const { access_token, refresh_token, user } = response.data;
    
    tokenManager.setToken(access_token);
    tokenManager.setRefreshToken(refresh_token);
    tokenManager.setUser(user);
    
    return response.data;
  },
  
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      tokenManager.clearAll();
    }
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  
  refreshToken: async () => {
    const refreshToken = tokenManager.getRefreshToken();
    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    });
    
    const { access_token } = response.data;
    tokenManager.setToken(access_token);
    
    return response.data;
  },
  
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.put('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    return response.data;
  },
  
  getUsers: async (params = {}) => {
    const response = await api.get('/auth/users', { params });
    return response.data;
  },
  
  getAuthStats: async () => {
    const response = await api.get('/auth/stats');
    return response.data;
  }
};

// Tasks API
export const tasksAPI = {
  getTasks: async (params = {}) => {
    const response = await api.get('/tasks', { params });
    return response.data;
  },
  
  getTask: async (taskId) => {
    const response = await api.get(`/tasks/${taskId}`);
    return response.data;
  },
  
  createTask: async (taskData) => {
    const response = await api.post('/tasks', taskData);
    return response.data;
  },
  
  updateTask: async (taskId, taskData) => {
    const response = await api.put(`/tasks/${taskId}`, taskData);
    return response.data;
  },
  
  deleteTask: async (taskId) => {
    const response = await api.delete(`/tasks/${taskId}`);
    return response.data;
  },
  
  getTaskStats: async () => {
    const response = await api.get('/tasks/stats');
    return response.data;
  },
  
  getKanbanData: async () => {
    const response = await api.get('/tasks/kanban');
    return response.data;
  },
  
  bulkUpdateTasks: async (taskIds, updates) => {
    const response = await api.put('/tasks/bulk-update', {
      task_ids: taskIds,
      updates
    });
    return response.data;
  }
};

// AI Chat API
export const chatAPI = {
  generateTasks: async (context = {}) => {
    const response = await api.post('/chat/generate-tasks', context);
    return response.data;
  },
  
  analyzePerformance: async (timeframe = '30 days') => {
    const response = await api.post('/chat/analyze-performance', { timeframe });
    return response.data;
  },
  
  suggestAssignment: async (taskInfo) => {
    const response = await api.post('/chat/suggest-assignment', { task_info: taskInfo });
    return response.data;
  },
  
  getServiceStatus: async () => {
    const response = await api.get('/chat/service-status');
    return response.data;
  },
  
  testServices: async () => {
    const response = await api.post('/chat/test-services');
    return response.data;
  }
};

// Telegram API
export const telegramAPI = {
  getStatus: async () => {
    const response = await api.get('/telegram/status');
    return response.data;
  },
  
  testConnection: async () => {
    const response = await api.post('/telegram/test');
    return response.data;
  },
  
  sendMessage: async (message, title = 'Custom Message', emoji = '📢') => {
    const response = await api.post('/telegram/send-message', {
      message,
      title,
      emoji
    });
    return response.data;
  },
  
  notifyTaskAssignment: async (taskId) => {
    const response = await api.post('/telegram/notify-task-assignment', {
      task_id: taskId
    });
    return response.data;
  },
  
  notifyTaskCompletion: async (taskId) => {
    const response = await api.post('/telegram/notify-task-completion', {
      task_id: taskId
    });
    return response.data;
  },
  
  sendPerformanceReport: async (timeframe = '30 days') => {
    const response = await api.post('/telegram/send-performance-report', {
      timeframe
    });
    return response.data;
  },
  
  getNotificationSettings: async () => {
    const response = await api.get('/telegram/notifications/settings');
    return response.data;
  },
  
  updateNotificationSettings: async (settings) => {
    const response = await api.put('/telegram/notifications/settings', settings);
    return response.data;
  },
  
  getNotificationHistory: async () => {
    const response = await api.get('/telegram/history');
    return response.data;
  }
};

// Utility functions
export const apiUtils = {
  handleError: (error) => {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      return {
        status,
        message: data.message || 'An error occurred',
        details: data.details || null
      };
    } else if (error.request) {
      // Request was made but no response received
      return {
        status: 0,
        message: 'Network error - please check your connection',
        details: null
      };
    } else {
      // Something else happened
      return {
        status: 0,
        message: error.message || 'An unexpected error occurred',
        details: null
      };
    }
  },
  
  isAuthenticated: () => {
    return !!tokenManager.getToken();
  },
  
  getCurrentUser: () => {
    return tokenManager.getUser();
  },
  
  isAdmin: () => {
    const user = tokenManager.getUser();
    return user && user.role === 'admin';
  },
  
  formatDate: (dateString) => {
    if (!dateString) return 'N/A';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
      return 'Invalid Date';
    }
  },
  
  formatDuration: (hours) => {
    if (!hours || hours === 0) return '0h';
    
    if (hours < 1) {
      return `${Math.round(hours * 60)}m`;
    } else if (hours < 24) {
      const h = Math.floor(hours);
      const m = Math.round((hours - h) * 60);
      return m > 0 ? `${h}h ${m}m` : `${h}h`;
    } else {
      const d = Math.floor(hours / 24);
      const h = Math.round(hours % 24);
      return h > 0 ? `${d}d ${h}h` : `${d}d`;
    }
  },
  
  getPriorityColor: (priority) => {
    const colors = {
      urgent: 'text-red-600 bg-red-50',
      high: 'text-orange-600 bg-orange-50',
      medium: 'text-yellow-600 bg-yellow-50',
      low: 'text-green-600 bg-green-50'
    };
    return colors[priority] || colors.medium;
  },
  
  getStatusColor: (status) => {
    const colors = {
      pending: 'text-gray-600 bg-gray-50',
      in_progress: 'text-blue-600 bg-blue-50',
      completed: 'text-green-600 bg-green-50'
    };
    return colors[status] || colors.pending;
  },
  
  getPriorityEmoji: (priority) => {
    const emojis = {
      urgent: '🔴',
      high: '🟠',
      medium: '🟡',
      low: '🟢'
    };
    return emojis[priority] || emojis.medium;
  },
  
  getStatusEmoji: (status) => {
    const emojis = {
      pending: '⏳',
      in_progress: '🔄',
      completed: '✅'
    };
    return emojis[status] || emojis.pending;
  }
};

export default api;

