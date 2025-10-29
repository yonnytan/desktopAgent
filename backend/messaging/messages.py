"""Conversation memory utilities for the desktop agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

MessageRole = Literal["system", "user", "assistant", "tool"]


@dataclass
class Message:
    """Represents a single conversation entry."""

    role: MessageRole
    content: str
    tool_call_id: str | None = None


@dataclass
class ConversationMemory:
    """Maintains ordered messages exchanged with the LLM."""
    system_prompt: str
    _messages: List[Message] = field(default_factory=list)

    def __init__(self, system_prompt) -> None:
        self.system_prompt = system_prompt
        self._messages = []
        self.add_system_message(self.system_prompt)

    def add_system_message(self, content: str) -> None:
        self._messages.append(Message(role="model", content=content))

    def add_user_message(self, content: str) -> None:
        self._messages.append(Message(role="user", content=content))

    def add_assistant_message(self, content: str, *, tool_call_id: str | None = None) -> None:
        self._messages.append(Message(role="model", content=content, tool_call_id=tool_call_id))

    def add_tool_message(self, payload: Dict[str, Any], tool_call_id: str) -> None:
        self._messages.append(
            Message(
                role="model",
                content=self._serialize_payload(payload),
                tool_call_id=tool_call_id,
            )
        )

    def history(self) -> List[Dict[str, Any]]:
        """Return the conversation formatted for chat-completion APIs."""

        formatted: List[Dict[str, Any]] = []
        for msg in self._messages:
            record: Dict[str, Any] = {"role": msg.role, "parts": [{"text": msg.content}]}
            # if msg.tool_call_id:
            #     record["tool_call_id"] = msg.tool_call_id
            formatted.append(record)
        return formatted

    @staticmethod
    def _serialize_payload(payload: Dict[str, Any]) -> str:
        try:
            import json

            return json.dumps(payload)
        except Exception:  # noqa: BLE001
            return str(payload)
