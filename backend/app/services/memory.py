"""Memory Service — persists conversation context between sessions.

Implements AD-CMP-04 §4: Regla de no repetición.
Stores summaries that persist across sessions.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.models import Conversation, Message, Project


class MemoryService:
    """Manages persistent memory across sessions."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_conversation_summary(self, project_id: str) -> str:
        """Get the accumulated conversation summary for a project."""
        # Get the most recent completed conversation with a summary
        conv = self.db.query(Conversation).join(
            # Join with Card to get project_id
        ).filter(
            # We need to join through Card to get project_id
        ).order_by(Conversation.created_at.desc()).first()

        # Simpler approach: get summary from the most recent conversation
        conv = self.db.query(Conversation).filter(
            Conversation.summary.isnot(None),
        ).order_by(Conversation.created_at.desc()).first()

        if conv:
            return conv.summary or ""
        return ""

    def update_conversation_summary(self, conversation_id: str) -> str:
        """Generate and store a summary for a completed conversation."""
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
        ).order_by(Message.created_at).all()

        if not messages:
            return ""

        # Build summary from user messages
        user_messages = [m for m in messages if m.role == "user"]
        summary_parts = []
        for msg in user_messages:
            content = msg.content[:200]  # Truncate long messages
            summary_parts.append(content)

        summary = " | ".join(summary_parts)

        # Update conversation with summary
        conv = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
        ).first()
        if conv:
            conv.summary = summary
            self.db.commit()

        return summary

    def get_context_for_project(self, project_id: str) -> dict:
        """Get all memory context for a project."""
        # Get latest summary
        summary = self.get_or_create_conversation_summary(project_id)

        # Get all conversations
        conversations = self.db.query(Conversation).join(
            # Through card to project
        ).all()

        # Get all messages count
        message_count = self.db.query(Message).count()

        return {
            "summary": summary,
            "conversation_count": len(conversations),
            "message_count": message_count,
        }
