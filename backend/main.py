import json

from config import Config
from services.bash import Bash
from messaging.messages import ConversationMemory as Messages
from llm import LLM

def confirm_execution(cmd: str) -> bool:
    return input(f"    ▶️   Execute '{cmd}'? [y/N]: ").strip().lower() == "y"

def main(config: Config):
    bash = Bash(config)
    llm = LLM(config)
    
    print(config.system_prompt)
    print("[INFO] Type 'quit' at any time to exit the agent loop.\n")
    
    messages = Messages(config.system_prompt)
    
    while True:
        user = input(f"['{bash.cwd}' 🙂] ").strip()
        if user.lower() == "quit":
            print("\n[🤖] Shutting down. Bye!\n")
            break
        if not user:
            continue
        user += f"\n Current working directory: `{bash.cwd}`"
        messages.add_user_message(user)

        while True:
            response, tool_calls = llm.query(messages, [bash.to_json_schema()])

            if response:
                response = response.strip()
                if "</think>" in response:
                    response = response.split("</think>")[-1].strip()
                if response:
                    messages.add_assistant_message(response)

            if tool_calls:
                for tc in tool_calls:
                    function_name = tc.name
                    function_args = tc.args

                    if function_name != "exec_bash_command" or "cmd" not in function_args:
                        tool_call_result = json.dumps({"error": "Incorrect tool or function argument"})
                    else:
                        command = function_args["cmd"]
                        if confirm_execution(command):
                            tool_call_result = bash.exec_bash_command(command)
                        else:
                            tool_call_result = {"error": "The user declined the execution of this command."}

                    messages.add_tool_message(tool_call_result, tc.id)
            else:
                if response:
                    print(response)
                    print("-" * 80 + "\n")
                break

if __name__ == "__main__":
    config = Config()
    main(config)