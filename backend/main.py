from flask import Flask, render_template # Add render_template for the root route

from config import Config
from services.bash import Bash
from messaging.messages import ConversationMemory as Messages
from llm import LLM
from api.routes import register_routes # This import should already be there


if __name__ == "__main__":
    config = Config()
    bash_service = Bash(config)
    llm_service = LLM(config)
    # Initialize ConversationMemory with the system prompt
    message_service = Messages(config.system_prompt)

    # Initialize the Flask application
    app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

    # Register the routes with the Flask app
    register_routes(app, bash_service, llm_service, message_service)

    print("[INFO] Flask app starting...")
    # Run the Flask app
    app.run(debug=True, port=5000)