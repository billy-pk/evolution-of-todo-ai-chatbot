"""
Phase 3 Model and Schema Tests
"""
import pytest
from datetime import datetime
from uuid import uuid4
from models import Task, Conversation, Message
from schemas import ChatRequest, ChatResponse


def test_task_model_creation():
    task = Task(user_id="user_123", title="Test Task", description="Test Description")
    assert task.user_id == "user_123"
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False


def test_task_model_completed_default_false():
    task = Task(user_id="user_456", title="Task")
    assert task.completed is False


def test_task_model_can_be_completed():
    task = Task(user_id="user_456", title="Completed Task", completed=True)
    assert task.completed is True


def test_conversation_model_creation():
    conv = Conversation(user_id="user_123")
    assert conv.user_id == "user_123"


def test_message_model_creation():
    conv_id = uuid4()
    msg = Message(conversation_id=conv_id, user_id="user_123", role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.user_id == "user_123"


def test_chat_request_schema():
    req = ChatRequest(message="Add a task to buy milk")
    assert req.message == "Add a task to buy milk"
    assert req.conversation_id is None


def test_chat_request_with_conversation_id():
    conv_id = uuid4()
    req = ChatRequest(message="hello", conversation_id=conv_id)
    assert req.conversation_id == conv_id


def test_chat_request_requires_message():
    with pytest.raises(Exception):
        ChatRequest()
