"""
ChatKit Server Implementation

This module implements a custom ChatKit server that integrates with our existing
PostgreSQL database and OpenAI Agents SDK.
"""

import json
from typing import Any, AsyncIterator, Optional
from datetime import datetime, UTC
from uuid import uuid4

from chatkit.server import (
    ChatKitServer,
    ThreadMetadata,
    UserMessageItem,
    ClientToolCallItem,
    StreamingResult,
    AssistantMessageItem,
    ThreadStreamEvent,
)
from chatkit.store import Store, StoreItemType, Page
from chatkit.agents import stream_agent_response, simple_to_agent_input, AgentContext as ChatKitAgentContext
from chatkit.server import ThreadItem
from sqlmodel import Session, select
from openai import AsyncOpenAI
from openai.lib.streaming import AsyncAssistantEventHandler

from db import engine
from models import Conversation, Message
from config import settings


class SimpleMemoryStore(Store):
    """
    Simple in-memory store implementation for ChatKit.

    This is a minimal implementation to get ChatKit working.
    We'll integrate with PostgreSQL properly later.
    """

    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, dict[str, Any]] = {}  # thread_id -> {item_id -> item}
        self.attachments: dict[str, bytes] = {}

    def generate_thread_id(self, context: Any) -> str:
        """Generate a unique thread ID."""
        return str(uuid4())

    def generate_item_id(self, item_type: StoreItemType, thread: ThreadMetadata, context: Any) -> str:
        """Generate a unique item ID."""
        return str(uuid4())

    async def load_thread(self, thread_id: str, context: Any) -> ThreadMetadata:
        """Load a thread by ID."""
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} not found")
        return self.threads[thread_id]

    async def load_threads(self, limit: int, before: str | None, context: Any) -> Page[ThreadMetadata]:
        """Load multiple threads."""
        thread_list = list(self.threads.values())
        return Page(data=thread_list[:limit], has_more=False)

    async def save_thread(self, thread: ThreadMetadata, context: Any) -> None:
        """Save a thread."""
        self.threads[thread.id] = thread
        if thread.id not in self.items:
            self.items[thread.id] = {}

    async def delete_thread(self, thread_id: str, context: Any) -> None:
        """Delete a thread."""
        if thread_id in self.threads:
            del self.threads[thread_id]
        if thread_id in self.items:
            del self.items[thread_id]

    async def load_thread_items(
        self, thread_id: str, limit: int, before: str | None, context: Any
    ) -> Page[ThreadItem]:
        """Load items for a thread."""
        if thread_id not in self.items:
            return Page(data=[], has_more=False)

        items = list(self.items[thread_id].values())
        return Page(data=items[:limit], has_more=False)

    async def load_item(self, thread_id: str, item_id: str, context: Any) -> ThreadItem:
        """Load a specific item."""
        if thread_id not in self.items or item_id not in self.items[thread_id]:
            raise ValueError(f"Item {item_id} not found in thread {thread_id}")
        return self.items[thread_id][item_id]

    async def save_item(self, thread_id: str, item: ThreadItem, context: Any) -> None:
        """Save an item."""
        if thread_id not in self.items:
            self.items[thread_id] = {}
        self.items[thread_id][item.id] = item

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: Any) -> None:
        """Add an item to a thread."""
        await self.save_item(thread_id, item, context)

    async def delete_thread_item(self, thread_id: str, item_id: str, context: Any) -> None:
        """Delete an item from a thread."""
        if thread_id in self.items and item_id in self.items[thread_id]:
            del self.items[thread_id][item_id]

    async def load_attachment(self, attachment_id: str, context: Any) -> bytes:
        """Load attachment data."""
        if attachment_id not in self.attachments:
            raise ValueError(f"Attachment {attachment_id} not found")
        return self.attachments[attachment_id]

    async def save_attachment(self, attachment_id: str, data: bytes, context: Any) -> None:
        """Save attachment data."""
        self.attachments[attachment_id] = data

    async def delete_attachment(self, attachment_id: str, context: Any) -> None:
        """Delete an attachment."""
        if attachment_id in self.attachments:
            del self.attachments[attachment_id]


class TaskManagerChatKitServer(ChatKitServer):
    """
    Custom ChatKit server for task management.

    Integrates with our existing database and provides AI-powered task management.
    """

    def __init__(self, data_store: Store):
        super().__init__(data_store)
        self.engine = engine
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | ClientToolCallItem,
        context: Any,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Handle incoming messages and stream responses.

        This is called whenever a user sends a message or a client tool completes.
        """
        # For now, just echo back a simple response
        # We'll integrate with the actual agent later

        # Get the user's message
        if isinstance(input, UserMessageItem):
            user_message = ""
            for content in input.content:
                if hasattr(content, 'text'):
                    user_message += content.text
                elif isinstance(content, dict) and 'text' in content:
                    user_message += content['text']

            # Save user message to database
            with Session(self.engine) as session:
                user_id = context.get("user_id")
                msg = Message(
                    conversation_id=thread.id,
                    user_id=user_id,
                    role="user",
                    content=user_message
                )
                session.add(msg)
                session.commit()

            # Create a simple assistant response
            response_text = f"I received your message: '{user_message}'. Full task management integration coming soon!"

            # Save assistant message to database
            with Session(self.engine) as session:
                assistant_msg = Message(
                    conversation_id=thread.id,
                    user_id=user_id,
                    role="assistant",
                    content=response_text
                )
                session.add(assistant_msg)
                session.commit()
                session.refresh(assistant_msg)

                # Yield assistant message event
                yield AssistantMessageItem(
                    id=str(assistant_msg.id),
                    content=[{"type": "text", "text": response_text}],
                    created_at=assistant_msg.created_at.isoformat(),
                )
