"""
AI Agent Service

This module provides the AI agent service that connects to the MCP server
and processes user messages. It uses the OpenAI Agents SDK with MCP integration.

Architecture:
- Connects to MCP server via MCPServerStreamableHttp (separate mode)
- Uses direct function tools (mounted mode)
- Uses OpenAI GPT-4o model for natural language understanding
- Stateless design: loads conversation history from database
- Returns structured responses with tool calls
"""

from agents import Agent, Runner, function_tool
from agents.mcp import MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from config import settings
from typing import List, Dict, Any
import logging
import os

# Set OpenAI API key in environment for agents SDK
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Global MCP server instance (singleton pattern for connection reuse)
_mcp_server = None
_mcp_server_lock = None


async def get_mcp_server():
    """
    Get or create the global MCP server instance.
    Uses singleton pattern to reuse connection across requests.

    Returns:
        MCPServerStreamableHttp: Shared MCP server instance
    """
    global _mcp_server, _mcp_server_lock

    # Initialize lock on first call
    if _mcp_server_lock is None:
        import asyncio
        _mcp_server_lock = asyncio.Lock()

    async with _mcp_server_lock:
        if _mcp_server is None:
            mcp_url = settings.mcp_server_url
            logger.info(f"🔌 Initializing MCP server connection (first time) to: {mcp_url}")
            logger.info(f"   MOUNT_MCP_SERVER={settings.MOUNT_MCP_SERVER}, API_PORT={settings.API_PORT}")
            _mcp_server = MCPServerStreamableHttp(
                name="Task MCP Server",
                params={
                    "url": mcp_url,
                    "timeout": settings.OPENAI_API_TIMEOUT,
                },
                cache_tools_list=True,
                max_retry_attempts=3,
            )
            logger.info("🔌 MCP server instance created")
        return _mcp_server


async def create_task_agent(user_id: str):
    """
    Create an AI agent with task management tools.

    Args:
        user_id: User ID for contextualizing agent responses

    Returns:
        Tuple of (agent, server_or_none) for use in async context manager
        - If MOUNT_MCP_SERVER=true: (agent, None) - uses direct function tools
        - If MOUNT_MCP_SERVER=false: (agent, mcp_server) - uses HTTP MCP connection
    """
    instructions = f"""You are a helpful assistant that manages todo tasks for users.

You have access to tools to create, list, update, complete, and delete tasks.

Current user ID: {user_id}

IMPORTANT - Task ID Handling:
- Task IDs are UUIDs (e.g., "123e4567-e89b-12d3-a456-426614174000")
- Users will refer to tasks by TITLE (e.g., "Buy groceries"), NOT by ID
- When updating, completing, or deleting a task:
  1. FIRST call list_tasks_tool to get all tasks
  2. Find the task that matches the user's description (by title)
  3. Extract the task_id (UUID) from that task
  4. THEN call update_task_tool/complete_task_tool/delete_task_tool with that task_id

Guidelines:
- Always use the provided user_id when calling tools
- Be concise and friendly in your responses
- When creating tasks, extract the task title from user input
- When listing tasks, format them in a clear, readable way
- Confirm actions after completing them (e.g., "I've marked 'Buy groceries' as complete")
- If multiple tasks match the user's description, ask which one they mean
- If no tasks match, tell the user the task wasn't found
"""

    if settings.MOUNT_MCP_SERVER:
        # Mounted mode: Use direct function tools (no HTTP to avoid deadlock)
        logger.info("🔧 Creating agent with direct function tools (mounted mode)")
        from tools.server import add_task, list_tasks, complete_task, update_task, delete_task

        # Wrap tools with user_id binding
        @function_tool
        def add_task_tool(title: str, description: str = None) -> dict:
            """Create a new task for the user.

            Args:
                title: Task title (required, 1-200 characters)
                description: Optional task description (max 1000 characters)

            Returns:
                Dict with status and task data
            """
            return add_task(user_id, title, description)

        @function_tool
        def list_tasks_tool(status: str = "all") -> dict:
            """List user's tasks with optional status filter.

            Args:
                status: Filter by status - "all", "pending", or "completed" (default: "all")

            Returns:
                Dict with status and list of tasks
            """
            return list_tasks(user_id, status)

        @function_tool
        def complete_task_tool(task_id: str) -> dict:
            """Mark a task as completed.

            Args:
                task_id: Task ID (UUID string)

            Returns:
                Dict with status and updated task data
            """
            return complete_task(user_id, task_id)

        @function_tool
        def update_task_tool(task_id: str, title: str = None, description: str = None) -> dict:
            """Update a task's title and/or description.

            Args:
                task_id: Task ID (UUID string)
                title: New task title (optional, 1-200 characters)
                description: New task description (optional, max 1000 characters)

            Returns:
                Dict with status and updated task data
            """
            return update_task(user_id, task_id, title, description)

        @function_tool
        def delete_task_tool(task_id: str) -> dict:
            """Delete a task.

            Args:
                task_id: Task ID (UUID string)

            Returns:
                Dict with status and deletion confirmation
            """
            return delete_task(user_id, task_id)

        agent = Agent(
            name="TaskAssistant",
            instructions=instructions,
            tools=[add_task_tool, list_tasks_tool, complete_task_tool, update_task_tool, delete_task_tool],
            model=settings.OPENAI_MODEL,
        )

        return agent, None  # No server context needed

    else:
        # Separate mode: Use HTTP MCP connection
        logger.info("🔧 Creating agent with MCP HTTP connection (separate mode)")
        server = await get_mcp_server()
        agent = Agent(
            name="TaskAssistant",
            instructions=instructions,
            mcp_servers=[server],
            model=settings.OPENAI_MODEL,
        )

        return agent, server


async def process_message(
    user_id: str,
    message: str,
    conversation_history: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Process a user message using the AI agent.

    Args:
        user_id: User ID from JWT token
        message: User's message text
        conversation_history: Previous messages in conversation (optional)

    Returns:
        Dict with:
            - response: AI assistant's text response
            - tool_calls: List of tool calls made (for logging)
            - model: Model used
            - tokens_used: Approximate token count
    """
    try:
        import time

        # Create agent with task tools
        start_total = time.time()
        start_agent = time.time()
        agent, server = await create_task_agent(user_id)
        agent_creation_time = time.time() - start_agent
        logger.info(f"⏱️  Agent creation took {agent_creation_time:.2f}s")

        # Handle both mounted and separate modes
        async def _run_agent():
            # Prepare messages for agent
            start_prep = time.time()
            messages = []
            if conversation_history:
                messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})
            prep_time = time.time() - start_prep
            logger.info(f"⏱️  Message preparation took {prep_time:.3f}s")

            # Run agent
            logger.info(f"🤖 Processing message for user {user_id}: {message[:100]}...")
            start_run = time.time()
            result = await Runner.run(agent, messages)
            run_time = time.time() - start_run
            logger.info(f"⏱️  Agent run took {run_time:.2f}s")

            # Extract tool calls from result
            start_extract = time.time()
            tool_calls = []
            if hasattr(result, 'tool_calls') and result.tool_calls:
                for tool_call in result.tool_calls:
                    tool_calls.append({
                        "tool": tool_call.name,
                        "parameters": tool_call.arguments,
                        "result": tool_call.result if hasattr(tool_call, 'result') else None
                    })
                logger.info(f"🔧 Tools called: {[tc['tool'] for tc in tool_calls]}")
            extract_time = time.time() - start_extract

            total_time = time.time() - start_total
            logger.info(f"⏱️  TOTAL process_message took {total_time:.2f}s (agent: {agent_creation_time:.2f}s, run: {run_time:.2f}s, extract: {extract_time:.3f}s)")

            # Return structured response
            return {
                "response": result.final_output if hasattr(result, 'final_output') else str(result),
                "tool_calls": tool_calls,
                "model": settings.OPENAI_MODEL,
                "tokens_used": 0,  # TODO: Extract from result if available
            }

        if server is None:
            # Mounted mode: Direct function tools (no context manager)
            return await _run_agent()
        else:
            # Separate mode: Use MCP server context manager
            async with server:
                return await _run_agent()

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        return {
            "response": "I'm sorry, I encountered an error processing your request. Please try again.",
            "tool_calls": [],
            "model": settings.OPENAI_MODEL,
            "tokens_used": 0,
            "error": str(e)
        }


async def process_message_streaming(
    user_id: str,
    message: str,
    conversation_history: List[Dict[str, str]] = None
):
    """
    Process a user message with streaming support (for future use).

    Args:
        user_id: User ID from JWT token
        message: User's message text
        conversation_history: Previous messages in conversation (optional)

    Yields:
        Stream events from the agent
    """
    try:
        agent, server = await create_task_agent(user_id)

        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})

        if server is None:
            # Mounted mode: Direct function tools (no context manager)
            result = Runner.run_streamed(agent, messages)
            async for event in result.stream_events():
                yield event
        else:
            # Separate mode: Use MCP server context manager
            async with server:
                result = Runner.run_streamed(agent, messages)
                async for event in result.stream_events():
                    yield event

    except Exception as e:
        logger.error(f"Error in streaming: {str(e)}", exc_info=True)
        yield {"type": "error", "error": str(e)}
