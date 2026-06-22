from typing import List, Optional

from sqlalchemy import select

from project.db.models import ChatMessage, ConversationSession


class MemoryRepository:
    def __init__(self, db):
        self.db = db

    def get_or_create_session(
        self,
        session_key: str,
        user_id: Optional[str] = None,
    ) -> ConversationSession:
        stmt = select(ConversationSession).where(
            ConversationSession.session_key == session_key
        )
        session = self.db.execute(stmt).scalar_one_or_none()

        if session is not None:
            return session

        session = ConversationSession(
            session_key=session_key,
            user_id=user_id,
            doc_metadata={},
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def save_message(
        self,
        session_id: int,
        role: str,
        content: str,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_recent_messages(
        self,
        session_id: int,
        limit: int = 10,
    ) -> List[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )

        rows = self.db.execute(stmt).scalars().all()

        return list(reversed(rows))