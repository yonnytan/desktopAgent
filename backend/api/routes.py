import json
from flask import Flask, request, jsonify, render_template

from services.bash import Bash
from messaging.messages import ConversationMemory
from llm import LLM

def register_routes(app: Flask, bash_service: Bash, llm_service: LLM, messages: ConversationMemory):

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/chat", methods=["POST"])
    def chat():
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Add user message to conversation memory
        messages.add_user_message(user_message)

        # Query the LLM
        response_text, tool_calls = llm_service.query(messages, [bash_service.to_json_schema()])

        if tool_calls:
            for tc in tool_calls:
                function_name = tc.name
                function_args = tc.args

                if function_name == "exec_bash_command" and "cmd" in function_args:
                    command = function_args["cmd"]
                    # In a web context, you might want to confirm execution with the user
                    # before running it. For a barebones version, we can auto-execute.
                    tool_call_result = bash_service.exec_bash_command(command)
                    messages.add_tool_message(tool_call_result, tc.id)
                    # If there's an error, send it back to the user
                    if tool_call_result.get("stderr"):
                        return jsonify({"response": tool_call_result["stderr"], "is_tool_output": True})
                    # Otherwise, send the stdout
                    else:
                        return jsonify({"response": tool_call_result["stdout"], "is_tool_output": True})
                else:
                    return jsonify({"error": "Incorrect tool or function argument"}), 400
        else:
            # Add assistant response to conversation memory
            messages.add_assistant_message(response_text)
            return jsonify({"response": response_text})

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500