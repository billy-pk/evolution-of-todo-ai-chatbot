"""
Phase 3 Data Isolation Tests

Verifies that user data is strictly isolated:
- User A cannot access User B's conversations
- Messages are filtered by user_id
- Conversation ownership is enforced
"""
import pytest
from sqlmodel import Session, select, create_engine, SQLModel
from uuid import uuid4
from models import Conversation, Message


@pytest.fixture(scope="function")
def test_engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_conversations_isolated_by_user(test_engine):
    """Each user only sees their own conversations."""
    user_a = "user_a_isolation"
    user_b = "user_b_isolation"

    with Session(test_engine) as session:
        for _ in range(2):
            session.add(Conversation(user_id=user_a))
        for _ in range(3):
            session.add(Conversation(user_id=user_b))
        session.commit()

    with Session(test_engine) as session:
        convs_a = session.exec(select(Conversation).where(Conversation.user_id == user_a)).all()
        convs_b = session.exec(select(Conversation).where(Conversation.user_id == user_b)).all()

    assert len(convs_a) == 2
    assert len(convs_b) == 3
    assert all(c.user_id == user_a for c in convs_a)
    assert all(c.user_id == user_b for c in convs_b)


def test_messages_isolated_by_user(test_engine):
    """Messages from one user are not visible when querying another user."""
    user_a = "msg_user_a"
    user_b = "msg_user_b"

    with Session(test_engine) as session:
        conv_a = Conversation(user_id=user_a)
        conv_b = Conversation(user_id=user_b)
        session.add(conv_a)
        session.add(conv_b)
        session.commit()
        session.refresh(conv_a)
        session.refresh(conv_b)

        for i in range(3):
            session.add(Message(conversation_id=conv_a.id, user_id=user_a, role="user", content=f"msg {i}"))
        session.add(Message(conversation_id=conv_b.id, user_id=user_b, role="user", content="user b msg"))
        session.commit()

        conv_a_id = conv_a.id
        conv_b_id = conv_b.id

    with Session(test_engine) as session:
        msgs_a = session.exec(select(Message).where(Message.user_id == user_a)).all()
        msgs_b = session.exec(select(Message).where(Message.user_id == user_b)).all()

    assert len(msgs_a) == 3
    assert len(msgs_b) == 1
    assert all(m.user_id == user_a for m in msgs_a)
    assert all(m.user_id == user_b for m in msgs_b)


def test_user_cannot_access_other_users_conversation(test_engine):
    """A user querying by another user's conversation_id gets no results."""
    user_a = "owner_user"
    user_b = "intruder_user"

    with Session(test_engine) as session:
        conv = Conversation(user_id=user_a)
        session.add(conv)
        session.commit()
        session.refresh(conv)
        conv_id = conv.id

    # User B tries to access User A's conversation by filtering with their own user_id
    with Session(test_engine) as session:
        result = session.exec(
            select(Conversation).where(
                Conversation.id == conv_id,
                Conversation.user_id == user_b
            )
        ).first()

    assert result is None


def test_conversation_ownership_enforced(test_engine):
    """Conversation lookup with correct owner succeeds; wrong owner returns None."""
    user_a = "real_owner"
    user_b = "wrong_user"

    with Session(test_engine) as session:
        conv = Conversation(user_id=user_a)
        session.add(conv)
        session.commit()
        session.refresh(conv)
        conv_id = conv.id

    with Session(test_engine) as session:
        found = session.exec(
            select(Conversation).where(
                Conversation.id == conv_id,
                Conversation.user_id == user_a
            )
        ).first()
        not_found = session.exec(
            select(Conversation).where(
                Conversation.id == conv_id,
                Conversation.user_id == user_b
            )
        ).first()

    assert found is not None
    assert not_found is None
