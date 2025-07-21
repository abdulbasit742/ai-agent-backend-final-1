/**
 * TaskCard Component - Individual Task Display and Management
 * Compatible with Flask JWT backend
 */

import { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  Clock, 
  User, 
  Calendar, 
  CheckCircle, 
  Play, 
  Pause,
  AlertCircle,
  Bot,
  MessageSquare,
  Edit,
  Trash2
} from 'lucide-react';
import { apiUtils } from '../services/api';
import '../App.css';

const TaskCard = ({ task, onUpdate, isAdmin = false }) => {
  const [updating, setUpdating] = useState(false);

  const handleStatusChange = async (newStatus) => {
    if (updating) return;
    
    setUpdating(true);
    try {
      await onUpdate(task.id, { status: newStatus });
    } catch (error) {
      console.error('Failed to update task status:', error);
    } finally {
      setUpdating(false);
    }
  };

  const getStatusButton = () => {
    switch (task.status) {
      case 'pending':
        return (
          <Button
            size="sm"
            onClick={() => handleStatusChange('in_progress')}
            disabled={updating}
            className="w-full"
          >
            <Play className="h-4 w-4 mr-2" />
            Start Task
          </Button>
        );
      case 'in_progress':
        return (
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleStatusChange('pending')}
              disabled={updating}
              className="flex-1"
            >
              <Pause className="h-4 w-4 mr-2" />
              Pause
            </Button>
            <Button
              size="sm"
              onClick={() => handleStatusChange('completed')}
              disabled={updating}
              className="flex-1"
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Complete
            </Button>
          </div>
        );
      case 'completed':
        return (
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleStatusChange('in_progress')}
            disabled={updating}
            className="w-full"
          >
            <Edit className="h-4 w-4 mr-2" />
            Reopen
          </Button>
        );
      default:
        return null;
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'bg-red-100 text-red-800 border-red-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-green-100 text-green-800 border-green-200'
    };
    return colors[priority] || colors.medium;
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-gray-100 text-gray-800 border-gray-200',
      in_progress: 'bg-blue-100 text-blue-800 border-blue-200',
      completed: 'bg-green-100 text-green-800 border-green-200'
    };
    return colors[status] || colors.pending;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No deadline';
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = date - now;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays < 0) {
        return `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) !== 1 ? 's' : ''}`;
      } else if (diffDays === 0) {
        return 'Due today';
      } else if (diffDays === 1) {
        return 'Due tomorrow';
      } else {
        return `Due in ${diffDays} days`;
      }
    } catch (error) {
      return 'Invalid date';
    }
  };

  const isOverdue = (dateString) => {
    if (!dateString) return false;
    try {
      const date = new Date(dateString);
      const now = new Date();
      return date < now && task.status !== 'completed';
    } catch (error) {
      return false;
    }
  };

  return (
    <Card className={`transition-all duration-200 hover:shadow-md ${
      task.status === 'completed' ? 'opacity-75' : ''
    } ${isOverdue(task.deadline) ? 'border-red-200 bg-red-50' : ''}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-900 mb-2">
              {task.title}
            </CardTitle>
            <div className="flex items-center gap-2 mb-2">
              <Badge className={getPriorityColor(task.priority)}>
                {apiUtils.getPriorityEmoji(task.priority)} {task.priority?.toUpperCase()}
              </Badge>
              <Badge className={getStatusColor(task.status)}>
                {apiUtils.getStatusEmoji(task.status)} {task.status?.replace('_', ' ').toUpperCase()}
              </Badge>
              {task.is_ai_generated && (
                <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                  <Bot className="h-3 w-3 mr-1" />
                  AI
                </Badge>
              )}
            </div>
          </div>
        </div>
        
        {task.description && (
          <CardDescription className="text-sm text-gray-600 line-clamp-2">
            {task.description}
          </CardDescription>
        )}
      </CardHeader>

      <CardContent className="pt-0">
        {/* Task Details */}
        <div className="space-y-3 mb-4">
          {/* Deadline */}
          {task.deadline && (
            <div className="flex items-center text-sm">
              <Calendar className="h-4 w-4 mr-2 text-gray-400" />
              <span className={isOverdue(task.deadline) ? 'text-red-600 font-medium' : 'text-gray-600'}>
                {formatDate(task.deadline)}
              </span>
              {isOverdue(task.deadline) && (
                <AlertCircle className="h-4 w-4 ml-2 text-red-500" />
              )}
            </div>
          )}

          {/* Estimated Hours */}
          {task.estimated_hours && (
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="h-4 w-4 mr-2 text-gray-400" />
              <span>Est. {apiUtils.formatDuration(task.estimated_hours)}</span>
            </div>
          )}

          {/* Assignee */}
          {task.assignee_info && (
            <div className="flex items-center text-sm text-gray-600">
              <User className="h-4 w-4 mr-2 text-gray-400" />
              <span>Assigned to {task.assignee_info.username}</span>
              {task.assignee_info.performance_score && (
                <Badge variant="outline" className="ml-2 text-xs">
                  {task.assignee_info.performance_score}% score
                </Badge>
              )}
            </div>
          )}

          {/* AI Context */}
          {task.is_ai_generated && task.ai_context && (
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
              <div className="flex items-center mb-1">
                <Bot className="h-4 w-4 mr-2 text-purple-600" />
                <span className="text-sm font-medium text-purple-800">AI Insight</span>
              </div>
              <p className="text-xs text-purple-700 line-clamp-2">
                {task.ai_context}
              </p>
            </div>
          )}

          {/* Difficulty Rating */}
          {task.difficulty_rating && (
            <div className="flex items-center text-sm text-gray-600">
              <div className="flex items-center mr-2">
                <span className="text-gray-400 mr-1">Difficulty:</span>
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <div
                      key={star}
                      className={`w-3 h-3 rounded-full mr-1 ${
                        star <= task.difficulty_rating
                          ? 'bg-yellow-400'
                          : 'bg-gray-200'
                      }`}
                    />
                  ))}
                </div>
              </div>
              <span className="text-xs">({task.difficulty_rating}/5)</span>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="space-y-2">
          {getStatusButton()}
          
          {/* Admin Actions */}
          {isAdmin && (
            <div className="flex gap-2 pt-2 border-t border-gray-100">
              <Button
                size="sm"
                variant="outline"
                className="flex-1"
                onClick={() => {
                  // Handle edit task
                  console.log('Edit task:', task.id);
                }}
              >
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="flex-1"
                onClick={() => {
                  // Handle send notification
                  console.log('Send notification for task:', task.id);
                }}
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Notify
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={() => {
                  // Handle delete task
                  if (confirm('Are you sure you want to delete this task?')) {
                    console.log('Delete task:', task.id);
                  }
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        {/* Task Metadata */}
        <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-500">
          <div className="flex justify-between items-center">
            <span>
              Created {apiUtils.formatDate(task.created_at)}
            </span>
            {task.updated_at && task.updated_at !== task.created_at && (
              <span>
                Updated {apiUtils.formatDate(task.updated_at)}
              </span>
            )}
          </div>
          {task.completed_at && (
            <div className="mt-1">
              <span className="text-green-600">
                ✅ Completed {apiUtils.formatDate(task.completed_at)}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default TaskCard;

