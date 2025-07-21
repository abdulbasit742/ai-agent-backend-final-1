# AI Agent System - Full Stack Web Application

A comprehensive AI-powered task management system built with Flask (Python 3.10) and React.js, featuring OpenAI GPT integration, Telegram notifications, JWT authentication, and performance tracking.

## 🚀 Features

### Backend (Flask)
- **Python 3.10 Compatible** - Fully tested and optimized for Python 3.10
- **JWT Authentication** - Secure token-based authentication with role-based access (Admin/Team Member)
- **Task CRUD Management** - Complete task lifecycle management with status tracking
- **OpenAI GPT Integration** - AI-powered task generation and suggestions using OpenAI API
- **Telegram Bot Integration** - Real-time notifications via Telegram Bot API
- **SQLite Database** - Lightweight, efficient database with SQLAlchemy ORM
- **Performance Tracking** - Team member performance scoring and analytics
- **RESTful API** - Clean, well-documented API endpoints

### Frontend (React)
- **Modern React.js** - Built with React 18+ and modern hooks
- **Tailwind CSS** - Beautiful, responsive UI with utility-first CSS
- **JWT Authentication** - Secure login/logout with protected routes
- **Task Dashboard** - Intuitive task management interface
- **Real-time Updates** - Live task status updates via API calls
- **Responsive Design** - Mobile-friendly interface
- **Performance Analytics** - Visual performance tracking for team members

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10 (tested and optimized)
- **Python**: Version 3.10 (required)
- **Node.js**: Version 16+ (for React frontend)
- **VS Code**: Recommended IDE with terminal support

### API Keys Required
- **OpenAI API Key**: For AI task generation features
- **Telegram Bot Token**: For notification system

## 🛠️ Installation & Setup

### Backend Setup (Flask)

1. **Navigate to backend directory**:
```powershell
cd backend
```

2. **Create virtual environment**:
```powershell
python -m venv venv
```

3. **Activate virtual environment**:
```powershell
venv\Scripts\activate
```

4. **Upgrade pip**:
```powershell
pip install --upgrade pip
```

5. **Install dependencies**:
```powershell
pip install -r requirements.txt
```

6. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Add your API keys (see Configuration section below)

7. **Start the Flask server**:
```powershell
python app.py
```

The backend will be available at: `http://localhost:5000`

### Frontend Setup (React)

1. **Navigate to frontend directory**:
```powershell
cd frontend
```

2. **Install dependencies**:
```powershell
npm install
```

3. **Start the development server**:
```powershell
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## ⚙️ Configuration

### Backend Environment Variables (.env)

Create a `.env` file in the `backend/` directory with the following content:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

# Database Configuration
DATABASE_URL=sqlite:///ai_agent_system.db

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Telegram Configuration
TELEGRAM_BOT_TOKEN=7411580150:AAFRN8a0hFY5DSA4SkFKDFocjMkYnVFjQ_Q
TELEGRAM_USER_ID=7491215797

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### Frontend Environment Variables (.env)

Create a `.env` file in the `frontend/` directory with the following content:

```env
# API Configuration
VITE_API_URL=http://localhost:5000/api
```

## 👤 Default User Accounts

The system comes with pre-configured demo accounts:

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator (full access)

### Team Member Accounts
- **Username**: `john_doe` | **Password**: `user123`
- **Username**: `jane_smith` | **Password**: `user123`
- **Username**: `mike_wilson` | **Password**: `user123`
- **Role**: Team Member (limited access)

## 🔧 Development

### Project Structure

```
AI-AGENT-SYSTEM-FULL-2/
├── backend/                    # Flask Backend
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── venv/                  # Virtual environment
│   └── src/
│       ├── models/            # Database models
│       │   ├── user.py        # User model
│       │   └── task.py        # Task model
│       ├── routes/            # API endpoints
│       │   ├── auth.py        # Authentication routes
│       │   ├── tasks.py       # Task management routes
│       │   ├── chat.py        # OpenAI integration routes
│       │   └── telegram.py    # Telegram integration routes
│       └── services/          # Business logic
│           ├── chatgpt_service.py    # OpenAI service
│           └── telegram_service.py   # Telegram service
│
└── frontend/                  # React Frontend
    ├── package.json          # Node.js dependencies
    ├── vite.config.js        # Vite configuration
    ├── tailwind.config.js    # Tailwind CSS configuration
    └── src/
        ├── App.jsx           # Main application component
        ├── main.jsx          # Application entry point
        ├── components/       # React components
        │   ├── Login.jsx     # Login component
        │   ├── Dashboard.jsx # Dashboard component
        │   └── TaskCard.jsx  # Task card component
        └── services/         # API services
            └── api.js        # Backend API integration
```

### API Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

#### Tasks
- `GET /api/tasks` - Get all tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `GET /api/tasks/stats` - Get task statistics

#### AI Integration
- `POST /api/chat/generate-tasks` - Generate AI tasks
- `POST /api/chat/suggest-assignment` - AI assignment suggestions

#### Telegram
- `POST /api/telegram/send-notification` - Send Telegram notification
- `GET /api/telegram/status` - Check Telegram bot status

## 🧪 Testing

### Backend Testing
```powershell
cd backend
venv\Scripts\activate
python -m pytest tests/
```

### Frontend Testing
```powershell
cd frontend
npm test
```

### Manual Testing
1. Start both backend and frontend servers
2. Navigate to `http://localhost:5173`
3. Login with admin credentials: `admin` / `admin123`
4. Test task creation, assignment, and status updates
5. Verify Telegram notifications (if configured)

## 🚀 Deployment

### Backend Deployment (Render.com)
1. Push code to GitHub repository
2. Connect repository to Render.com
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`
5. Configure environment variables in Render dashboard

### Frontend Deployment (Vercel/Netlify)
1. Build the frontend: `npm run build`
2. Deploy the `dist/` folder to Vercel or Netlify
3. Configure `VITE_API_URL` to point to your deployed backend

## 🔍 Troubleshooting

### Common Issues

#### Backend Issues
- **Import Errors**: Ensure you're in the correct directory and virtual environment is activated
- **Database Errors**: Delete `ai_agent_system.db` and restart the server to recreate the database
- **API Key Errors**: Verify your OpenAI API key and Telegram bot token in `.env` file

#### Frontend Issues
- **Build Errors**: Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- **API Connection**: Verify backend is running and `VITE_API_URL` is correct
- **Authentication Issues**: Clear browser localStorage and try logging in again

### Performance Optimization
- Use production builds for deployment
- Enable gzip compression
- Implement caching strategies
- Monitor API response times

## 📚 Documentation

### API Documentation
- Swagger/OpenAPI documentation available at: `http://localhost:5000/api/docs`
- Postman collection included in `docs/` folder

### Code Documentation
- All functions and classes are documented with docstrings
- Type hints used throughout the codebase
- Comments explain complex business logic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the API documentation

## 🔄 Version History

- **v1.0.0** - Initial release with core features
- **v1.1.0** - Added AI task generation
- **v1.2.0** - Telegram integration
- **v1.3.0** - Performance tracking

---

**Built with ❤️ using Flask, React, and modern web technologies**

