"""
ChatKit Server Implementation

This module implements a custom ChatKit server that integrates with our existing
PostgreSQL database and OpenAI Agents SDK.
"""

import json
import logging
from typing import Any, AsyncIterator, Optional, Literal
from datetime import datetime, UTC
from uuid import uuid4

from chatkit.server import (
    ChatKitServer,
    ThreadStreamEvent,
    ThreadMetadata,
    ThreadItem,
    Page,
    UserMessageItem,
    AssistantMessageItem,
    Store,
    StoreItemType,
)
from chatkit.agents import (
    stream_agent_response,
    simple_to_agent_input,
    AgentContext,
    Attachment,
)
from agents import Agent, Runner
from sqlmodel import Session, select
from openai import AsyncOpenAI

from db import engine
from models import Conversation, Message
from config import settings

logger = logging.getLogger(__name__)


class SimpleMemoryStore(Store[dict]):
    """
    Simple in-memory store implementation for ChatKit.

    This is a minimal implementation to get ChatKit working.
    We'll integrate with PostgreSQL properly later.
    """

    def __init__(self):
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, dict[str, ThreadItem]] = {}  # thread_id -> {item_id -> item}
        self.attachments: dict[str, Attachment] = {}

    def generate_thread_id(self, context: dict) -> str:
        """Generate a unique thread ID."""
        return str(uuid4())

    def generate_item_id(
        self,
        item_type: Literal["message", "tool_call", "task", "workflow", "attachment"],
        thread: ThreadMetadata,
        context: dict,
    ) -> str:
        """Generate a unique item ID."""
        return str(uuid4())

    async def load_thread(self, thread_id: str, context: dict) -> ThreadMetadata:
        """Load a thread by ID."""
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} not found")
        return self.threads[thread_id]

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: dict
    ) -> Page[ThreadMetadata]:
        """Load multiple threads."""
        thread_list = list(self.threads.values())
        return Page(data=thread_list[:limit], has_more=False)

    async def save_thread(self, thread: ThreadMetadata, context: dict) -> None:
        """Save a thread."""
        self.threads[thread.id] = thread
        if thread.id not in self.items:
            self.items[thread.id] = {}

    async def delete_thread(self, thread_id: str, context: dict) -> None:
        """Delete a thread."""
        if thread_id in self.threads:
            del self.threads[thread_id]
        if thread_id in self.items:
            del self.items[thread_id]

    async def load_thread_items(
        self, thread_id: str, after: str | None, limit: int, order: str, context: dict
    ) -> Page[ThreadItem]:
        """Load items for a thread."""
        if thread_id not in self.items:
            return Page(data=[], has_more=False)

        items = list(self.items[thread_id].values())
        return Page(data=items[:limit], has_more=False)

    async def load_item(self, thread_id: str, item_id: str, context: dict) -> ThreadItem:
        """Load a specific item."""
        if thread_id not in self.items or item_id not in self.items[thread_id]:
            raise ValueError(f"Item {item_id} not found in thread {thread_id}")
        return self.items[thread_id][item_id]

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        """Save an item."""
        if thread_id not in self.items:
            self.items[thread_id] = {}
        self.items[thread_id][item.id] = item

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: dict) -> None:
        """Add an item to a thread."""
        await self.save_item(thread_id, item, context)

    async def delete_thread_item(self, thread_id: str, item_id: str, context: dict) -> None:
        """Delete an item from a thread."""
        if thread_id in self.items and item_id in self.items[thread_id]:
            del self.items[thread_id][item_id]

    async def load_attachment(self, attachment_id: str, context: dict) -> Attachment:
        """Load attachment data."""
        if attachment_id not in self.attachments:
            raise ValueError(f"Attachment {attachment_id} not found")
        return self.attachments[attachment_id]

    async def save_attachment(self, attachment: Attachment, context: dict) -> None:
        """Save attachment data."""
        self.attachments[attachment.id] = attachment

    async def delete_attachment(self, attachment_id: str, context: dict) -> None:
        """Delete an attachment."""
        if attachment_id in self.attachments:
            del self.attachments[attachment_id]


class TaskManagerChatKitServer(ChatKitServer[dict]):
    """
    Custom ChatKit server for task management.

    Integrates with our existing database and provides AI-powered task management.
    """

    def __init__(self, data_store: Store):
        super().__init__(data_store)
        self.db_engine = engine
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Define the assistant agent
        self.assistant = Agent(
            model="gpt-4o",
            name="TaskAssistant",
            instructions="""You are a helpful task management assistant. You help users:
- Create new tasks
- List their existing tasks
- Update task details
- Mark tasks as complete
- Delete tasks

Be concise and helpful. When users ask about tasks, provide clear responses."""
        )

    async def respond(
        self,
        thread: ThreadMetadata,
        input: UserMessageItem | None,
        context: dict,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """
        Handle incoming messages and stream responses.

        This is called whenever a user sends a message.
        """
        logger.info(f"TaskManagerChatKitServer.respond called for thread {thread.id}")

        if input is None:
            logger.warning("No input provided to respond")
            return

        # Create agent context
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        # Convert ChatKit input to Agent SDK format
        agent_input = await simple_to_agent_input(input)

        if not agent_input:
            logger.warning("Failed to convert input to agent format")
            return

        logger.info(f"Running agent with input: {agent_input}")

        # Run the agent and stream the response
        result = Runner.run_streamed(
            self.assistant,
            input=agent_input,
            context=agent_context,
        )

        # Stream the agent response as ChatKit events
        async for event in stream_agent_response(agent_context, result):
            yield event
