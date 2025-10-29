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
        hello = 0
        # Initialize variables for text response and tool calls
        text_response = ""
        tool_calls = []

        if hasattr(response, 'candidates') and response.candidates:
            if hasattr(response.candidates[0], 'content') and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text is not None:
                        text_response += part.text
                    if hasattr(part, "function_call") and part.function_call is not None:
                        tool_calls.append(part.function_call)

        return text_response, tool_calls