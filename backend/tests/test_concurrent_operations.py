"""
Phase 3 Concurrent Operations Tests

Tests that concurrent database operations work correctly:
- Concurrent conversation creation
- Concurrent message saving
- No data corruption under parallel writes
"""
import pytest
import threading
from sqlmodel import Session, select, create_engine, SQLModel
from models import Conversation, Message


@pytest.fixture(scope="function")
def test_engine():
    engine = create_engine(
        "sqlite:///./test_concurrent.db",
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


def test_concurrent_conversation_creation(test_engine):
    """Multiple threads can create conversations simultaneously without corruption."""
    results = []
    errors = []

    def create_conversation(user_id):
        try:
            with Session(test_engine) as session:
                conv = Conversation(user_id=user_id)
                session.add(conv)
                session.commit()
                session.refresh(conv)
                results.append(str(conv.id))
        except Exception as e:
            errors.append(str(e))

    threads = [
        threading.Thread(target=create_conversation, args=(f"user_{i}",))
        for i in range(5)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Errors during concurrent creation: {errors}"
    assert len(results) == 5
    assert len(set(results)) == 5  # All IDs unique


def test_concurrent_message_saving(test_engine):
    """Multiple threads can save messages to the same conversation without corruption."""
    with Session(test_engine) as session:
        conv = Conversation(user_id="user_concurrent")
        session.add(conv)
        session.commit()
        session.refresh(conv)
        conv_id = conv.id

    errors = []

    def save_message(i):
        try:
            with Session(test_engine) as session:
                msg = Message(
                    conversation_id=conv_id,
                    user_id="user_concurrent",
                    role="user",
                    content=f"Message {i}"
                )
                session.add(msg)
                session.commit()
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=save_message, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Errors during concurrent saves: {errors}"

    with Session(test_engine) as session:
        messages = session.exec(
            select(Message).where(Message.conversation_id == conv_id)
        ).all()
    assert len(messages) == 5


def test_conversation_user_id_isolation_under_concurrency(test_engine):
    """Each user's conversations remain isolated under concurrent access."""
    errors = []

    def create_user_convs(user_id):
        try:
            with Session(test_engine) as session:
                for _ in range(3):
                    conv = Conversation(user_id=user_id)
                    session.add(conv)
                session.commit()
        except Exception as e:
            errors.append(str(e))

    threads = [
        threading.Thread(target=create_user_convs, args=(f"isolated_user_{i}",))
        for i in range(3)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0

    for i in range(3):
        with Session(test_engine) as session:
            convs = session.exec(
                select(Conversation).where(Conversation.user_id == f"isolated_user_{i}")
            ).all()
        assert len(convs) == 3
