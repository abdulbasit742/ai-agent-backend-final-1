"""
Telegram Service - Telegram Bot API Integration
Compatible with Python 3.10
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramService:
    """Service for Telegram Bot API integration"""
    
    def __init__(self):
        """Initialize Telegram service"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.user_id = os.getenv('TELEGRAM_USER_ID')
        
        if not self.bot_token or not self.user_id:
            logger.warning("Telegram credentials not found. Telegram features will be disabled.")
            self.is_configured = False
        else:
            self.is_configured = True
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
            logger.info("Telegram service initialized successfully")
    
    def is_available(self) -> bool:
        """Check if Telegram service is available"""
        return self.is_configured
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Telegram bot connection"""
        if not self.is_available():
            return {
                'success': False,
                'error': 'Telegram service not configured',
                'message': 'Bot token or user ID missing'
            }
        
        try:
            # Test bot info
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    return {
                        'success': True,
                        'bot_info': bot_info.get('result', {}),
                        'message': 'Telegram bot connection successful'
                    }
            
            return {
                'success': False,
                'error': 'Bot API error',
                'message': f"HTTP {response.status_code}: {response.text}"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram connection test failed: {e}")
            return {
                'success': False,
                'error': 'Connection failed',
                'message': str(e)
            }
    
    def send_message(self, message: str, parse_mode: str = 'MarkdownV2', 
                    disable_notification: bool = False) -> Dict[str, Any]:
        """Send message to configured user"""
        if not self.is_available():
            logger.warning("Telegram service not available")
            return {
                'success': False,
                'error': 'Service not configured'
            }
        
        try:
            payload = {
                'chat_id': self.user_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info("Telegram message sent successfully")
                    return {
                        'success': True,
                        'message_id': result.get('result', {}).get('message_id'),
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            logger.error(f"Telegram API error: {response.text}")
            return {
                'success': False,
                'error': 'API error',
                'details': response.text
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return {
                'success': False,
                'error': 'Network error',
                'details': str(e)
            }
    
    def send_task_assignment_notification(self, task_data: Dict[str, Any], 
                                        assignee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send task assignment notification"""
        try:
            # Format task assignment message
            message = self._format_task_assignment_message(task_data, assignee_data)
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending task assignment notification: {e}")
            return {
                'success': False,
                'error': 'Formatting error',
                'details': str(e)
            }
    
    def send_task_completion_notification(self, task_data: Dict[str, Any], 
                                        assignee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send task completion notification"""
        try:
            # Format task completion message
            message = self._format_task_completion_message(task_data, assignee_data)
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending task completion notification: {e}")
            return {
                'success': False,
                'error': 'Formatting error',
                'details': str(e)
            }
    
    def send_task_status_update(self, task_data: Dict[str, Any], 
                              old_status: str, new_status: str,
                              assignee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send task status update notification"""
        try:
            # Format status update message
            message = self._format_task_status_message(task_data, old_status, new_status, assignee_data)
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending task status notification: {e}")
            return {
                'success': False,
                'error': 'Formatting error',
                'details': str(e)
            }
    
    def send_performance_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send performance report notification"""
        try:
            # Format performance report message
            message = self._format_performance_report_message(report_data)
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending performance report: {e}")
            return {
                'success': False,
                'error': 'Formatting error',
                'details': str(e)
            }
    
    def send_ai_task_generation_notification(self, tasks: List[Dict[str, Any]], 
                                           context: str = "") -> Dict[str, Any]:
        """Send AI task generation notification"""
        try:
            # Format AI task generation message
            message = self._format_ai_task_generation_message(tasks, context)
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending AI task notification: {e}")
            return {
                'success': False,
                'error': 'Formatting error',
                'details': str(e)
            }
    
    def _format_task_assignment_message(self, task_data: Dict[str, Any], 
                                      assignee_data: Dict[str, Any]) -> str:
        """Format task assignment message with MarkdownV2"""
        priority_emoji = task_data.get('priority_emoji', '🟡')
        status_emoji = task_data.get('status_emoji', '⏳')
        
        # Escape special characters for MarkdownV2
        title = self._escape_markdown(task_data.get('title', 'Unknown Task'))
        assignee = self._escape_markdown(assignee_data.get('username', 'Unknown'))
        description = self._escape_markdown(task_data.get('description', 'No description')[:200])
        priority = self._escape_markdown(task_data.get('priority', 'medium').title())
        
        # Format due date
        due_date = task_data.get('due_date')
        due_date_str = ""
        if due_date:
            try:
                if isinstance(due_date, str):
                    due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                else:
                    due_date_obj = due_date
                # Format due date
                due_date_format = '%Y-%m-%d %H:%M'
                due_date_str = f"\\n📅 *Due:* {due_date_obj.strftime(due_date_format)}"
            except:
                due_date_str = ""
        
        message = f"""🎯 *Task Assignment Notification*
        
{priority_emoji} *Task:* {title}
{status_emoji} *Status:* Assigned
👤 *Assigned to:* @{assignee}
⚡ *Priority:* {priority}{due_date_str}

📝 *Description:*
{description}

🤖 *AI Agent System* \\- Task Management"""
        
        return message
    
    def _format_task_completion_message(self, task_data: Dict[str, Any], 
                                      assignee_data: Dict[str, Any]) -> str:
        """Format task completion message with MarkdownV2"""
        title = self._escape_markdown(task_data.get('title', 'Unknown Task'))
        assignee = self._escape_markdown(assignee_data.get('username', 'Unknown'))
        
        # Calculate completion time
        duration_hours = task_data.get('duration_hours', 0)
        duration_str = f"{duration_hours:.1f} hours" if duration_hours > 0 else "Unknown"
        duration_escaped = self._escape_markdown(duration_str)
        
        message = f"""✅ *Task Completed\\!*
        
🎯 *Task:* {title}
👤 *Completed by:* @{assignee}
⏱️ *Duration:* {duration_escaped}
📊 *Score:* {task_data.get('completion_score', 0):.0f}/100

🎉 Great work\\! Keep up the excellent performance\\.

🤖 *AI Agent System* \\- Task Management"""
        
        return message
    
    def _format_task_status_message(self, task_data: Dict[str, Any], 
                                   old_status: str, new_status: str,
                                   assignee_data: Dict[str, Any]) -> str:
        """Format task status update message with MarkdownV2"""
        title = self._escape_markdown(task_data.get('title', 'Unknown Task'))
        assignee = self._escape_markdown(assignee_data.get('username', 'Unknown'))
        old_status_escaped = self._escape_markdown(old_status.replace('_', ' ').title())
        new_status_escaped = self._escape_markdown(new_status.replace('_', ' ').title())
        
        status_emoji = task_data.get('status_emoji', '🔄')
        
        message = f"""🔄 *Task Status Update*
        
🎯 *Task:* {title}
👤 *Assignee:* @{assignee}
{status_emoji} *Status:* {old_status_escaped} → {new_status_escaped}

🤖 *AI Agent System* \\- Task Management"""
        
        return message
    
    def _format_performance_report_message(self, report_data: Dict[str, Any]) -> str:
        """Format performance report message with MarkdownV2"""
        timeframe = self._escape_markdown(report_data.get('timeframe', '30 days'))
        overall_score = report_data.get('overall_score', 0)
        trend = report_data.get('productivity_trend', 'stable')
        
        # Trend emoji
        trend_emoji = {
            'improving': '📈',
            'stable': '📊',
            'declining': '📉'
        }.get(trend, '📊')
        
        # Format key insights
        insights = report_data.get('key_insights', [])
        insights_text = ""
        if insights:
            insights_escaped = [self._escape_markdown(insight) for insight in insights[:3]]
            insights_text = "\\n".join([f"• {insight}" for insight in insights_escaped])
        
        message = f"""📊 *Performance Report*
        
📅 *Period:* {timeframe}
🎯 *Overall Score:* {overall_score}/100
{trend_emoji} *Trend:* {self._escape_markdown(trend.title())}

💡 *Key Insights:*
{insights_text}

🤖 *AI Agent System* \\- Performance Analytics"""
        
        return message
    
    def _format_ai_task_generation_message(self, tasks: List[Dict[str, Any]], 
                                         context: str = "") -> str:
        """Format AI task generation message with MarkdownV2"""
        task_count = len(tasks)
        context_escaped = self._escape_markdown(context) if context else "AI analysis"
        
        # Format task list
        task_list = ""
        for i, task in enumerate(tasks[:5], 1):  # Limit to 5 tasks
            title = self._escape_markdown(task.get('title', 'Unknown Task'))
            priority = task.get('priority', 'medium')
            priority_emoji = {
                'urgent': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(priority, '🟡')
            
            task_list += f"{i}\\. {priority_emoji} {title}\\n"
        
        message = f"""🤖 *AI Task Generation*
        
✨ Generated {task_count} new tasks based on {context_escaped}

📋 *New Tasks:*
{task_list}

🎯 Tasks are ready for assignment and prioritization\\.

🤖 *AI Agent System* \\- Intelligent Task Management"""
        
        return message
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for MarkdownV2"""
        if not text:
            return ""
        
        # Characters that need escaping in MarkdownV2
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        escaped_text = str(text)
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        
        return escaped_text
    
    def send_custom_message(self, title: str, content: str, 
                          emoji: str = "📢") -> Dict[str, Any]:
        """Send custom formatted message"""
        try:
            title_escaped = self._escape_markdown(title)
            content_escaped = self._escape_markdown(content)
            
            message = f"""{emoji} *{title_escaped}*
            
{content_escaped}

🤖 *AI Agent System*"""
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending custom message: {e}")
            return {
                'success': False,
                'error': 'Formatting error',
                'details': str(e)
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get Telegram service status"""
        return {
            'is_configured': self.is_configured,
            'bot_token_set': bool(self.bot_token),
            'user_id_set': bool(self.user_id),
            'service_available': self.is_available()
        }

