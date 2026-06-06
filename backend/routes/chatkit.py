"""
ChatKit Integration Routes

This module provides endpoints to integrate OpenAI ChatKit with our custom
conversation database. It acts as a bridge between ChatKit's expected API
and our conversation/message storage.

Endpoints:
- POST /chatkit - Main ChatKit protocol endpoint (no /api prefix)
- GET  /api/chatkit/threads - List conversation threads
- GET  /api/chatkit/threads/{thread_id} - Get thread with messages
- POST /api/chatkit/threads - Create new thread
- POST /api/chatkit/messages - Add message and get AI response
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse, Response
from sqlmodel import Session, select
from datetime import datetime, UTC
import logging
from limiter import limiter, CHAT_RATE_LIMIT

from db import get_session
from models import Conversation, Message
from middleware import verify_token
from services.chatkit_server import TaskManagerChatKitServer, SimpleMemoryStore
from chatkit.server import StreamingResult, NonStreamingResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatkit", tags=["chatkit"])
chatkit_router = APIRouter(tags=["chatkit-protocol"])

# Initialize ChatKit server instance
data_store = SimpleMemoryStore()
chatkit_server = TaskManagerChatKitServer(data_store)


def _get_user_id(request: Request) -> str:
    """
    Extract and validate user_id from Bearer JWT token using JWKS (EdDSA).
    Raises 401 if token is missing or invalid.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = auth_header[7:]
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user_id


@router.get("/threads")
async def list_threads(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    List all conversation threads for the authenticated user.
    """
    try:
        user_id = _get_user_id(request)

        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        conversations = session.exec(statement).all()

        threads = [
            {
                "id": str(conv.id),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
            }
            for conv in conversations
        ]

        return {"threads": threads}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing threads: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list threads")


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Get a specific thread with its messages.
    """
    try:
        user_id = _get_user_id(request)

        statement = select(Conversation).where(
            Conversation.id == thread_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Thread not found")

        msg_statement = (
            select(Message)
            .where(Message.conversation_id == thread_id)
            .order_by(Message.created_at.asc())
        )
        messages = session.exec(msg_statement).all()

        return {
            "id": str(conversation.id),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get thread")


@router.post("/threads")
async def create_thread(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Create a new thread (conversation).
    """
    try:
        user_id = _get_user_id(request)

        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        logger.info(f"Created new thread {conversation.id} for user {user_id}")

        return {
            "id": str(conversation.id),
            "created_at": conversation.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create thread")


@router.post("/messages")
async def add_message(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Add a message to a thread and get AI response.
    """
    try:
        user_id = _get_user_id(request)

        body = await request.json()
        thread_id = body.get("thread_id")
        message_text = body.get("message")

        if not thread_id or not message_text:
            raise HTTPException(status_code=400, detail="Missing thread_id or message")

        statement = select(Conversation).where(
            Conversation.id == thread_id,
            Conversation.user_id == user_id
        )
        conversation = session.exec(statement).first()

        if not conversation:
            raise HTTPException(status_code=404, detail="Thread not found")

        from services.agent import process_message

        msg_statement = (
            select(Message)
            .where(Message.conversation_id == thread_id)
            .order_by(Message.created_at.asc())
        )
        existing_messages = session.exec(msg_statement).all()

        message_history = [
            {"role": msg.role, "content": msg.content}
            for msg in existing_messages
        ]

        user_message = Message(
            conversation_id=thread_id,
            user_id=user_id,
            role="user",
            content=message_text
        )
        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        try:
            agent_result = await process_message(
                user_id=user_id,
                message=message_text,
                conversation_history=message_history
            )

            assistant_message = Message(
                conversation_id=thread_id,
                user_id=user_id,
                role="assistant",
                content=agent_result["response"],
                tool_calls=str(agent_result.get("tool_calls", []))
            )
            session.add(assistant_message)

            conversation.updated_at = datetime.now(UTC)
            session.add(conversation)
            session.commit()
            session.refresh(assistant_message)

            logger.info(f"Added message to thread {thread_id} for user {user_id}")

            return {
                "message_id": str(user_message.id),
                "response_id": str(assistant_message.id),
                "response": agent_result["response"],
                "thread_id": str(thread_id)
            }

        except Exception as agent_error:
            logger.error(f"Error processing message through agent: {str(agent_error)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to process message: {str(agent_error)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to add message")


# ============================================================================
# ChatKit Protocol Endpoint (for ChatKit.js client)
# ============================================================================

@chatkit_router.post("/chatkit")
@limiter.limit(CHAT_RATE_LIMIT)
async def chatkit_endpoint(request: Request):
    """
    Main ChatKit protocol endpoint.

    Receives requests from the ChatKit.js client and forwards them to the
    ChatKitServer for processing. Returns streaming SSE or JSON response.
    """
    try:
        logger.info("=== ChatKit endpoint received request ===")

        user_id = _get_user_id(request)
        logger.info(f"ChatKit request authenticated for user {user_id}")

        context = {"user_id": user_id}
        body = await request.body()

        result = await chatkit_server.process(body, context)

        if isinstance(result, StreamingResult):
            logger.info("Returning streaming response")
            return StreamingResponse(result, media_type="text/event-stream")
        elif isinstance(result, NonStreamingResult):
            logger.info("Returning JSON response")
            return Response(content=result.json, media_type="application/json")
        else:
            return Response(content=str(result), media_type="application/json")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ChatKit endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ChatKit endpoint error: {str(e)}")
