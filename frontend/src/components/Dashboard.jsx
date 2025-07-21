/**
 * Dashboard Component - Team Member Dashboard
 * Compatible with Flask JWT backend
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { 
  User, 
  LogOut, 
  Plus, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  BarChart3,
  Bot,
  MessageSquare,
  Settings,
  Refresh
} from 'lucide-react';
import { authAPI, tasksAPI, chatAPI, telegramAPI, apiUtils } from '../services/api';
import TaskCard from './TaskCard';
import '../App.css';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load user info
      const userResponse = await authAPI.getCurrentUser();
      if (userResponse.status === 'success') {
        setUser(userResponse.user);
      }

      // Load tasks
      const tasksResponse = await tasksAPI.getTasks();
      if (tasksResponse.status === 'success') {
        setTasks(tasksResponse.tasks || []);
      }

      // Load stats
      const statsResponse = await tasksAPI.getTaskStats();
      if (statsResponse.status === 'success') {
        setStats(statsResponse.stats || {});
      }

    } catch (error) {
      const errorInfo = apiUtils.handleError(error);
      setError(errorInfo.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/login');
    }
  };

  const handleTaskUpdate = async (taskId, updates) => {
    try {
      const response = await tasksAPI.updateTask(taskId, updates);
      if (response.status === 'success') {
        // Update local tasks
        setTasks(prev => prev.map(task => 
          task.id === taskId ? { ...task, ...updates } : task
        ));
        
        // Refresh stats
        const statsResponse = await tasksAPI.getTaskStats();
        if (statsResponse.status === 'success') {
          setStats(statsResponse.stats || {});
        }
      }
    } catch (error) {
      const errorInfo = apiUtils.handleError(error);
      setError(errorInfo.message);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getTasksByStatus = (status) => {
    return tasks.filter(task => task.status === status);
  };

  const isAdmin = user && user.role === 'admin';

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo and Title */}
            <div className="flex items-center">
              <div className="bg-blue-600 p-2 rounded-lg mr-3">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">AI Agent System</h1>
                <p className="text-sm text-gray-500">Task Management Dashboard</p>
              </div>
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <Refresh className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              
              <div className="flex items-center space-x-2">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.full_name || user?.username}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">
                    {user?.role} {isAdmin && '(Admin)'}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleLogout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {getGreeting()}, {user?.full_name || user?.username}!
          </h2>
          <p className="text-gray-600">
            Here's what's happening with your tasks today.
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{tasks.length}</div>
              <p className="text-xs text-muted-foreground">
                All assigned tasks
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {getTasksByStatus('pending').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Awaiting action
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">In Progress</CardTitle>
              <AlertCircle className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {getTasksByStatus('in_progress').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Currently working
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {getTasksByStatus('completed').length}
              </div>
              <p className="text-xs text-muted-foreground">
                Successfully finished
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Performance Card */}
        {user && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="h-5 w-5 mr-2" />
                Your Performance
              </CardTitle>
              <CardDescription>
                Track your productivity and task completion metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {user.performance_score || 0}%
                  </div>
                  <p className="text-sm text-gray-600">Performance Score</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {user.total_tasks_completed || 0}
                  </div>
                  <p className="text-sm text-gray-600">Tasks Completed</p>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {apiUtils.formatDuration(user.average_completion_time || 0)}
                  </div>
                  <p className="text-sm text-gray-600">Avg. Completion Time</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Tasks Section */}
        <div className="space-y-6">
          {/* Pending Tasks */}
          {getTasksByStatus('pending').length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Clock className="h-5 w-5 mr-2 text-yellow-600" />
                Pending Tasks ({getTasksByStatus('pending').length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {getTasksByStatus('pending').map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onUpdate={handleTaskUpdate}
                    isAdmin={isAdmin}
                  />
                ))}
              </div>
            </div>
          )}

          {/* In Progress Tasks */}
          {getTasksByStatus('in_progress').length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <AlertCircle className="h-5 w-5 mr-2 text-blue-600" />
                In Progress ({getTasksByStatus('in_progress').length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {getTasksByStatus('in_progress').map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onUpdate={handleTaskUpdate}
                    isAdmin={isAdmin}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Completed Tasks */}
          {getTasksByStatus('completed').length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
                Completed ({getTasksByStatus('completed').length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {getTasksByStatus('completed').slice(0, 6).map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onUpdate={handleTaskUpdate}
                    isAdmin={isAdmin}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {tasks.length === 0 && (
            <Card className="text-center py-12">
              <CardContent>
                <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No tasks assigned yet
                </h3>
                <p className="text-gray-600 mb-4">
                  Tasks will appear here once they are assigned to you.
                </p>
                {isAdmin && (
                  <Button onClick={() => navigate('/admin')}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create New Task
                  </Button>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Admin Quick Actions */}
        {isAdmin && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                Admin Quick Actions
              </CardTitle>
              <CardDescription>
                Manage tasks, generate AI suggestions, and send notifications
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <Button onClick={() => navigate('/admin')}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Task
                </Button>
                <Button variant="outline" onClick={() => navigate('/admin/ai')}>
                  <Bot className="h-4 w-4 mr-2" />
                  AI Task Generator
                </Button>
                <Button variant="outline" onClick={() => navigate('/admin/performance')}>
                  <BarChart3 className="h-4 w-4 mr-2" />
                  Performance Analytics
                </Button>
                <Button variant="outline" onClick={() => navigate('/admin/notifications')}>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Send Notification
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default Dashboard;

