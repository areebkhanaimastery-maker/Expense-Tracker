"""
Conversation Memory — session-based in-memory message store.

Tracks messages within a single application session.
Does NOT persist to disk or database.
"""


class ConversationMemory:
    """Session-based conversation history."""

    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self._messages: list[dict] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self._messages.append({
            "role": role,
            "content": content,
        })
        # Trim oldest messages if over limit
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages:]

    def get_messages(self) -> list[dict]:
        """Get all messages in conversation history."""
        return list(self._messages)

    def get_recent_messages(self, count: int = 10) -> list[dict]:
        """Get the most recent messages."""
        return list(self._messages[-count:])

    def clear(self) -> None:
        """Clear all conversation history."""
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)
