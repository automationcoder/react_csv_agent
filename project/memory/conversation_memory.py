from typing import List, Dict, Optional

from project.db.transaction import transaction
from project.memory.memory_repository import MemoryRepository


class ConversationMemory:
    def __init__(
        self,
        session_key: str = "default-session",
        user_id: Optional[str] = None,
        window_size: int = 10,
    ):
        self.session_key = session_key
        self.user_id = user_id
        self.window_size = window_size

    def add_user_message(self, content: str) -> None:
        self._save_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        self._save_message("assistant", content)

    def _save_message(self, role: str, content: str) -> None:
        with transaction() as db:
            repo = MemoryRepository(db)
            session = repo.get_or_create_session(
                session_key=self.session_key,
                user_id=self.user_id,
            )
            repo.save_message(
                session_id=session.id,
                role=role,
                content=content,
            )

    def get_recent_messages(self) -> List[Dict[str, str]]:
        with transaction() as db:
            repo = MemoryRepository(db)
            session = repo.get_or_create_session(
                session_key=self.session_key,
                user_id=self.user_id,
            )

            messages = repo.get_recent_messages(
                session_id=session.id,
                limit=self.window_size,
            )

            return [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ]

    def get_context(self) -> str:
        messages = self.get_recent_messages()

        if not messages:
            return ""

        lines = []

        for message in messages:
            lines.append(f"{message['role']}: {message['content']}")

        return "\n".join(lines)
