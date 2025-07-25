import os
from flask import Flask
from flask_cors import CORS
from src.routes import register_routes
from src.database import init_db
from src.services.telegram_service import TelegramService
from src.services.chatgpt_service import ChatGPTService

# Load .env only when running locally
if os.environ.get("RENDER") != "true" and os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Flask app
app.config["SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///ai_agent_system.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize services
telegram_service = TelegramService()
chatgpt_service = ChatGPTService()

# Register routes
register_routes(app, telegram_service, chatgpt_service)

# Initialize the database
with app.app_context():
    init_db()

# Run server
if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "True") == "True"
    )
