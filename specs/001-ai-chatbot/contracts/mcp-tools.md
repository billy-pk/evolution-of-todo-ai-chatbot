# API Contract: MCP Tools

**Feature**: 001-ai-chatbot
**Date**: 2025-12-12
**Status**: Design Complete

---

## Overview

MCP (Model Context Protocol) tools are standardized interfaces that allow the AI agent to perform task operations. All tools enforce user isolation and verify task ownership before executing operations.

---

## Common Patterns

### Security Requirements (All Tools)
1. **User Isolation**: Every tool MUST accept `user_id` as the first parameter
2. **Ownership Verification**: Before modifying/deleting tasks, verify `task.user_id == user_id`
3. **SQL Injection Prevention**: Use parameterized queries
4. **Error Handling**: Return structured errors for unauthorized access

### Input Validation (All Tools)
- `user_id`: Required, non-empty string, max 255 characters
- All parameters validated before database operations
- Invalid parameters return error with field-specific message

### Output Format (All Tools)
```json
{
  "status": "success|error",
  "data": {...},
  "error": "error message (if status=error)"
}
```

---

## Tool 1: add_task

### Purpose
Create a new task for the user.

### Parameters

| Parameter   | Type   | Required | Constraints          | Description                  |
|-------------|--------|----------|----------------------|------------------------------|
| user_id     | string | Yes      | 1-255 characters     | User ID from JWT token       |
| title       | string | Yes      | 1-200 characters     | Task title                   |
| description | string | No       | Max 1000 characters  | Optional task description    |

### Pydantic Schema
```python
from pydantic import BaseModel, Field

class AddTaskParams(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255, description="User ID from JWT token")
    title: str = Field(..., min_length=1, max_length=200, description="Task title (required)")
    description: str | None = Field(None, max_length=1000, description="Optional task description")
```

### MCP Tool Definition
```python
from mcp import Tool

add_task_tool = Tool(
    name="add_task",
    description="Create a new task for the user. Returns the created task with its ID.",
    parameters=AddTaskParams,
    function=add_task_handler
)
```

### Success Response
```json
{
  "status": "success",
  "data": {
    "task_id": "uuid-string",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-12T10:30:00Z"
  }
}
```

### Error Responses

#### Invalid Title (Empty or Too Long)
```json
{
  "status": "error",
  "error": "Title must be between 1 and 200 characters"
}
```

#### Description Too Long
```json
{
  "status": "error",
  "error": "Description must be 1000 characters or less"
}
```

#### Database Error
```json
{
  "status": "error",
  "error": "Failed to create task: database connection error"
}
```

### Implementation Pattern
```python
async def add_task_handler(user_id: str, title: str, description: str | None = None) -> dict:
    with Session(engine) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description
        )
        session.add(task)
        session.commit()
        session.refresh(task)

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
```

### Test Cases
- ✅ Valid title and description → Task created
- ✅ Valid title, no description → Task created with null description
- ❌ Empty title → Error
- ❌ Title >200 characters → Error
- ❌ Description >1000 characters → Error
- ❌ Database connection failure → Error

---

## Tool 2: list_tasks

### Purpose
List tasks for a user, optionally filtered by completion status.

### Parameters

| Parameter | Type   | Required | Constraints                      | Description                        |
|-----------|--------|----------|----------------------------------|------------------------------------|
| user_id   | string | Yes      | 1-255 characters                 | User ID from JWT token             |
| status    | string | No       | "all", "pending", or "completed" | Filter by completion status        |

### Pydantic Schema
```python
from pydantic import BaseModel, Field, validator

class ListTasksParams(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255, description="User ID from JWT token")
    status: str = Field(default="all", description="Filter: 'all', 'pending', or 'completed'")

    @validator('status')
    def validate_status(cls, v):
        if v not in ['all', 'pending', 'completed']:
            raise ValueError("status must be 'all', 'pending', or 'completed'")
        return v
```

### MCP Tool Definition
```python
list_tasks_tool = Tool(
    name="list_tasks",
    description="List user's tasks, optionally filtered by status (all, pending, completed).",
    parameters=ListTasksParams,
    function=list_tasks_handler
)
```

### Success Response
```json
{
  "status": "success",
  "data": {
    "tasks": [
      {
        "task_id": "uuid-1",
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "created_at": "2025-12-12T10:30:00Z",
        "updated_at": "2025-12-12T10:30:00Z"
      },
      {
        "task_id": "uuid-2",
        "title": "Call dentist",
        "description": null,
        "completed": false,
        "created_at": "2025-12-12T09:15:00Z",
        "updated_at": "2025-12-12T09:15:00Z"
      }
    ],
    "count": 2,
    "filter": "pending"
  }
}
```

### Empty Result
```json
{
  "status": "success",
  "data": {
    "tasks": [],
    "count": 0,
    "filter": "completed"
  }
}
```

### Error Responses

#### Invalid Status Filter
```json
{
  "status": "error",
  "error": "Invalid status filter: must be 'all', 'pending', or 'completed'"
}
```

### Implementation Pattern
```python
async def list_tasks_handler(user_id: str, status: str = "all") -> dict:
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)

        tasks = session.exec(statement).all()

        return {
            "status": "success",
            "data": {
                "tasks": [
                    {
                        "task_id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ],
                "count": len(tasks),
                "filter": status
            }
        }
```

### Test Cases
- ✅ List all tasks → Returns all user's tasks
- ✅ List pending tasks → Returns only incomplete tasks
- ✅ List completed tasks → Returns only completed tasks
- ✅ No tasks → Returns empty list with count=0
- ❌ Invalid status filter → Error

---

## Tool 3: update_task

### Purpose
Update a task's title and/or description.

### Parameters

| Parameter   | Type   | Required | Constraints         | Description                     |
|-------------|--------|----------|---------------------|---------------------------------|
| user_id     | string | Yes      | 1-255 characters    | User ID from JWT token          |
| task_id     | string | Yes      | Valid UUID          | Task ID to update               |
| title       | string | No       | 1-200 characters    | New task title                  |
| description | string | No       | Max 1000 characters | New task description            |

### Pydantic Schema
```python
class UpdateTaskParams(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255, description="User ID from JWT token")
    task_id: str = Field(..., description="Task ID (UUID)")
    title: str | None = Field(None, min_length=1, max_length=200, description="New title (optional)")
    description: str | None = Field(None, max_length=1000, description="New description (optional)")

    @validator('task_id')
    def validate_task_id(cls, v):
        try:
            UUID(v)
        except ValueError:
            raise ValueError("task_id must be a valid UUID")
        return v
```

### MCP Tool Definition
```python
update_task_tool = Tool(
    name="update_task",
    description="Update a task's title and/or description. At least one field must be provided.",
    parameters=UpdateTaskParams,
    function=update_task_handler
)
```

### Success Response
```json
{
  "status": "success",
  "data": {
    "task_id": "uuid-string",
    "title": "Buy groceries and milk",
    "description": "Updated description",
    "completed": false,
    "updated_at": "2025-12-12T11:00:00Z"
  }
}
```

### Error Responses

#### Task Not Found
```json
{
  "status": "error",
  "error": "Task not found"
}
```

#### Unauthorized (Task Belongs to Different User)
```json
{
  "status": "error",
  "error": "Unauthorized: task does not belong to user"
}
```

#### No Fields to Update
```json
{
  "status": "error",
  "error": "At least one field (title or description) must be provided"
}
```

### Implementation Pattern
```python
async def update_task_handler(user_id: str, task_id: str, title: str | None = None, description: str | None = None) -> dict:
    if title is None and description is None:
        return {"status": "error", "error": "At least one field (title or description) must be provided"}

    with Session(engine) as session:
        task = session.get(Task, UUID(task_id))

        if not task:
            return {"status": "error", "error": "Task not found"}

        if task.user_id != user_id:
            return {"status": "error", "error": "Unauthorized: task does not belong to user"}

        if title:
            task.title = title
        if description is not None:  # Allow setting to empty string
            task.description = description

        task.updated_at = datetime.now(UTC)
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "status": "success",
            "data": {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }
```

### Test Cases
- ✅ Update title only → Title changed, description unchanged
- ✅ Update description only → Description changed, title unchanged
- ✅ Update both → Both fields changed
- ❌ Neither field provided → Error
- ❌ Task ID doesn't exist → Error
- ❌ Task belongs to different user → Error
- ❌ Invalid UUID format → Error

---

## Tool 4: complete_task

### Purpose
Mark a task as completed.

### Parameters

| Parameter | Type   | Required | Constraints      | Description            |
|-----------|--------|----------|------------------|------------------------|
| user_id   | string | Yes      | 1-255 characters | User ID from JWT token |
| task_id   | string | Yes      | Valid UUID       | Task ID to complete    |

### Pydantic Schema
```python
class CompleteTaskParams(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255, description="User ID from JWT token")
    task_id: str = Field(..., description="Task ID (UUID)")

    @validator('task_id')
    def validate_task_id(cls, v):
        try:
            UUID(v)
        except ValueError:
            raise ValueError("task_id must be a valid UUID")
        return v
```

### MCP Tool Definition
```python
complete_task_tool = Tool(
    name="complete_task",
    description="Mark a task as completed.",
    parameters=CompleteTaskParams,
    function=complete_task_handler
)
```

### Success Response
```json
{
  "status": "success",
  "data": {
    "task_id": "uuid-string",
    "title": "Buy groceries",
    "completed": true,
    "updated_at": "2025-12-12T12:00:00Z"
  }
}
```

### Error Responses

#### Task Not Found
```json
{
  "status": "error",
  "error": "Task not found"
}
```

#### Unauthorized
```json
{
  "status": "error",
  "error": "Unauthorized: task does not belong to user"
}
```

#### Already Completed (Idempotent)
```json
{
  "status": "success",
  "data": {
    "task_id": "uuid-string",
    "title": "Buy groceries",
    "completed": true,
    "updated_at": "2025-12-12T12:00:00Z"
  }
}
```

### Implementation Pattern
```python
async def complete_task_handler(user_id: str, task_id: str) -> dict:
    with Session(engine) as session:
        task = session.get(Task, UUID(task_id))

        if not task:
            return {"status": "error", "error": "Task not found"}

        if task.user_id != user_id:
            return {"status": "error", "error": "Unauthorized: task does not belong to user"}

        if not task.completed:
            task.completed = True
            task.updated_at = datetime.now(UTC)
            session.add(task)
            session.commit()
            session.refresh(task)

        return {
            "status": "success",
            "data": {
                "task_id": str(task.id),
                "title": task.title,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            }
        }
```

### Test Cases
- ✅ Complete pending task → Task marked complete
- ✅ Complete already completed task → Idempotent (no error)
- ❌ Task ID doesn't exist → Error
- ❌ Task belongs to different user → Error
- ❌ Invalid UUID format → Error

---

## Tool 5: delete_task

### Purpose
Delete a task (hard delete).

### Parameters

| Parameter | Type   | Required | Constraints      | Description            |
|-----------|--------|----------|------------------|------------------------|
| user_id   | string | Yes      | 1-255 characters | User ID from JWT token |
| task_id   | string | Yes      | Valid UUID       | Task ID to delete      |

### Pydantic Schema
```python
class DeleteTaskParams(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255, description="User ID from JWT token")
    task_id: str = Field(..., description="Task ID (UUID)")

    @validator('task_id')
    def validate_task_id(cls, v):
        try:
            UUID(v)
        except ValueError:
            raise ValueError("task_id must be a valid UUID")
        return v
```

### MCP Tool Definition
```python
delete_task_tool = Tool(
    name="delete_task",
    description="Delete a task permanently.",
    parameters=DeleteTaskParams,
    function=delete_task_handler
)
```

### Success Response
```json
{
  "status": "success",
  "data": {
    "task_id": "uuid-string",
    "title": "Buy groceries",
    "deleted": true
  }
}
```

### Error Responses

#### Task Not Found
```json
{
  "status": "error",
  "error": "Task not found"
}
```

#### Unauthorized
```json
{
  "status": "error",
  "error": "Unauthorized: task does not belong to user"
}
```

### Implementation Pattern
```python
async def delete_task_handler(user_id: str, task_id: str) -> dict:
    with Session(engine) as session:
        task = session.get(Task, UUID(task_id))

        if not task:
            return {"status": "error", "error": "Task not found"}

        if task.user_id != user_id:
            return {"status": "error", "error": "Unauthorized: task does not belong to user"}

        title = task.title  # Save for response
        session.delete(task)
        session.commit()

        return {
            "status": "success",
            "data": {
                "task_id": task_id,
                "title": title,
                "deleted": true
            }
        }
```

### Test Cases
- ✅ Delete existing task → Task removed from database
- ❌ Task ID doesn't exist → Error
- ❌ Task belongs to different user → Error
- ❌ Invalid UUID format → Error
- ❌ Delete already deleted task → Error (task not found)

---

## Tool Registration

### MCP Server Setup
```python
# backend/mcp/server.py
from mcp import MCPServer
from backend.mcp.tools import (
    add_task_tool,
    list_tasks_tool,
    update_task_tool,
    complete_task_tool,
    delete_task_tool
)

mcp_server = MCPServer(name="TaskMCPServer")

# Register all tools
mcp_server.register_tool(add_task_tool)
mcp_server.register_tool(list_tasks_tool)
mcp_server.register_tool(update_task_tool)
mcp_server.register_tool(complete_task_tool)
mcp_server.register_tool(delete_task_tool)
```

### Agent Integration
```python
# backend/services/agent.py
from openai import OpenAI
from openai.agents import Agent
from backend.mcp.server import mcp_server

client = OpenAI(api_key=settings.OPENAI_API_KEY)

agent = Agent(
    name="TaskAssistant",
    instructions="""You are a helpful assistant that manages todo tasks for users.

    You can:
    - Create new tasks (add_task)
    - List tasks (list_tasks) with filters (all, pending, completed)
    - Update task titles and descriptions (update_task)
    - Mark tasks as complete (complete_task)
    - Delete tasks (delete_task)

    Always confirm operations to the user in a friendly, conversational tone.
    When listing tasks, present them in a clear, numbered format.
    If a user's request is ambiguous (e.g., "delete task" without specifying which one), ask for clarification.
    """,
    tools=mcp_server.get_tools(),  # Get all registered MCP tools
    model="gpt-4o"
)
```

---

## Security Summary

### User Isolation (Enforced by All Tools)
- Every tool verifies `task.user_id == user_id` before operations
- Database queries always include `WHERE user_id = ?`
- No cross-user data leakage possible

### Authorization Flow
1. JWT validated at endpoint level (user_id extracted)
2. user_id passed to agent as context
3. Agent includes user_id in all tool calls
4. Tools verify ownership before database operations

### SQL Injection Prevention
- Use parameterized queries (SQLModel)
- No string concatenation for SQL
- ORM handles escaping automatically

### Error Handling
- Never expose database structure in errors
- Generic error messages for unauthorized access
- Log unauthorized attempts for audit

---

## Testing

### Unit Tests (Per Tool)
```python
# backend/tests/test_mcp_tools.py

def test_add_task_creates_task():
    result = add_task_handler(user_id="test-user", title="Test task")
    assert result["status"] == "success"
    assert "task_id" in result["data"]

def test_list_tasks_filters_by_user():
    # Create tasks for user-1 and user-2
    # Assert list_tasks("user-1") only returns user-1's tasks

def test_update_task_rejects_unauthorized():
    # Create task for user-1
    # Attempt update with user-2
    result = update_task_handler(user_id="user-2", task_id=task_id, title="Hacked")
    assert result["status"] == "error"
    assert "Unauthorized" in result["error"]

def test_complete_task_is_idempotent():
    # Complete task twice
    # Assert both calls succeed

def test_delete_task_removes_from_database():
    # Create task, delete task
    # Assert task no longer in database
```

### Integration Tests (With Agent)
```python
def test_agent_calls_add_task_on_create_request():
    response = agent.run(messages=[{"role": "user", "content": "Create a task to test"}])
    assert "add_task" in response.tool_calls
    assert response.tool_calls[0]["result"]["status"] == "success"
```

---

## Summary

5 MCP tools defined with complete contracts:
1. ✅ **add_task**: Create new tasks
2. ✅ **list_tasks**: List tasks with status filter
3. ✅ **update_task**: Modify task title/description
4. ✅ **complete_task**: Mark task as completed
5. ✅ **delete_task**: Remove task permanently

All tools enforce user isolation, validate inputs, and return structured responses.

**Next**: Create quickstart.md for development setup.
