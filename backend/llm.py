from google import genai as genai
from config import Config
from google.genai import types
from typing import Any, Dict, List, Tuple
from messaging.messages import ConversationMemory as Messages
class LLM:
    """
    An abstraction to prompt an LLM with OpenAI compatible endpoint.
    """
    def __init__(self, config: Config):
        super().__init__()
        
        self.client = genai.Client(api_key=config.llm_api_key)
        self.config = config

    def query(
        self,
        messages: Messages,
        tools: List[Dict[str, Any]],
        max_tokens=None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        
        config = types.GenerateContentConfig(
            system_instruction=messages.system_prompt,
            tools=[types.Tool(function_declarations=tools)]
        )
        
        # Create a chat session (tools support may require custom handling if available)
        chat = self.client.chats.create(model=self.config.llm_model_name, 
                                        history=messages.history(),
                                        config=config)
        
        # Send latest user message; Gemini keeps context
        response = chat.send_message(
            messages.history()[-1]['parts'][0]['text']
        )

        # For tools/function calling, check attributes (may require additional SDK version/config)
        tool_calls = getattr(response, "function_calls", []) or []
        return response.text, tool_calls