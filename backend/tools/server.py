"""
MCP Server for Task Operations

This module implements an MCP (Model Context Protocol) server using FastMCP
from the official MCP Python SDK. The server exposes tools for task operations
that the AI agent can call.

Architecture:
- Built with FastMCP (stateless HTTP server)
- Exposes tools via @mcp.tool() decorator
- Connects to PostgreSQL via SQLModel
- Used by OpenAI Agent via MCPServerStreamableHttp
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import backend modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from mcp.server import FastMCP
from models import Task
from db import engine
from sqlmodel import Session
from pydantic import ValidationError


# Initialize FastMCP server with stateless HTTP transport
mcp = FastMCP(
    "TaskMCPServer",
    stateless_http=True,
    json_response=True
)


def add_task(user_id: str, title: str, description: str = None, _session: Session = None) -> dict:
    """Create a new task for the user. Returns the created task with its ID.

    Args:
        user_id: User ID from JWT token (1-255 characters)
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)
        _session: Optional database session (for testing)

    Returns:
        Dict with status and task data
    """
    # Validate input parameters
    if not title or len(title.strip()) == 0:
        return {
            "status": "error",
            "error": "Title must be between 1 and 200 characters"
        }

    if len(title) > 200:
        return {
            "status": "error",
            "error": "Title must be between 1 and 200 characters"
        }

    if description and len(description) > 1000:
        return {
            "status": "error",
            "error": "Description must be 1000 characters or less"
        }

    if not user_id or len(user_id) > 255:
        return {
            "status": "error",
            "error": "User ID must be between 1 and 255 characters"
        }

    try:
        # Use provided session or create new one
        if _session:
            # Create task
            task = Task(
                user_id=user_id,
                title=title.strip(),
                description=description
            )
            _session.add(task)
            _session.commit()
            _session.refresh(task)

            # Return success response
            return {
                "status": "success",
                "data": {
                    "task_id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
            }
        else:
            with Session(engine) as session:
                # Create task
                task = Task(
                    user_id=user_id,
                    title=title.strip(),
                    description=description
                )
                session.add(task)
                session.commit()
                session.refresh(task)

                # Return success response
                return {
                    "status": "success",
                    "data": {
                        "task_id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat()
                    }
                }
    except ValidationError as e:
        return {
            "status": "error",
            "error": f"Validation error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to create task: {str(e)}"
        }


# Register the tool with MCP
@mcp.tool()
def add_task_tool(user_id: str, title: str, description: str = None) -> dict:
    """MCP tool wrapper for add_task. Create a new task for the user.

    Args:
        user_id: User ID from JWT token (1-255 characters)
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)

    Returns:
        Dict with status and task data
    """
    return add_task(user_id, title, description)


if __name__ == "__main__":
    # Run MCP server on HTTP transport
    # This will start the server at http://localhost:8000/mcp
    mcp.run(transport="streamable-http")
