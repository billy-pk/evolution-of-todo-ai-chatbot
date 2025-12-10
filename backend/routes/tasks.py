"""
Task CRUD Endpoints

T036: Router initialization
T037: POST /api/{user_id}/tasks - Create task
T038: GET /api/{user_id}/tasks - List tasks
T039: Add status filter query parameter
T040: Verify user_id in URL matches JWT
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlmodel import Session, select
from typing import Literal, Optional
from uuid import UUID

from db import get_session
from models import Task
from schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

# T036: Initialize router
router = APIRouter(tags=["tasks"])


def verify_user_access(request: Request, user_id: str = Path(...)) -> str:
    """
    T040: Verify user_id in URL matches user_id from JWT token.

    Args:
        request: FastAPI request object with user_id in state (from JWT middleware)
        user_id: User ID from URL path parameter

    Returns:
        Validated user_id

    Raises:
        HTTPException: 403 if user_id mismatch
    """
    token_user_id = getattr(request.state, "user_id", None)

    if not token_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    if token_user_id != user_id:
        print(f"=== DEBUG BACKEND: USER_ID MISMATCH ===")
        print(f"=== Token user_id: {token_user_id}")
        print(f"=== URL user_id: {user_id}")
        raise HTTPException(
            status_code=403,
            detail=f"Access denied: Token user_id '{token_user_id}' does not match URL user_id '{user_id}'"
        )

    return user_id


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    T037: Create a new task for the authenticated user.

    - Validates user_id from JWT matches URL
    - Creates task with user_id from token
    - Returns created task with generated ID and timestamps
    """
    # Create new task with user_id from JWT token
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # Convert Task model to TaskResponse with from_attributes
    return TaskResponse.model_validate(task)


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str = Depends(verify_user_access),
    status: Literal["all", "pending", "completed"] = Query("all", description="Filter tasks by completion status"),
    session: Session = Depends(get_session)
):
    """
    T038: List tasks for the authenticated user.
    T039: Support status filter (all/pending/completed).

    - Validates user_id from JWT matches URL
    - Filters tasks by user_id
    - Sorts by created_at DESC (newest first)
    - Optionally filters by completion status
    """
    # T038: Base query - filter by user_id and sort by created_at DESC
    query = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())

    # T039: Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)
    # "all" status returns all tasks (no additional filter)

    tasks = session.exec(query).all()

    # Convert Task models to TaskResponse with from_attributes
    task_responses = [TaskResponse.model_validate(task) for task in tasks]

    return TaskListResponse(
        tasks=task_responses,
        total=len(tasks)
    )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    user_id: str = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Get a single task by ID.

    - Validates user_id from JWT matches URL
    - Verifies task ownership (user_id match)
    - Returns 404 if task not found or doesn't belong to user
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Task belongs to another user"
        )

    # Convert Task model to TaskResponse
    return TaskResponse.model_validate(task)


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: str = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Update a task's title and/or description.

    - Validates user_id from JWT matches URL
    - Verifies task ownership
    - Updates only provided fields
    - Returns updated task with new updated_at timestamp
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Cannot update another user's task"
        )

    # Update only provided fields
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description

    session.add(task)
    session.commit()
    session.refresh(task)

    # Convert Task model to TaskResponse
    return TaskResponse.model_validate(task)


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    task_id: UUID,
    user_id: str = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status.

    - Validates user_id from JWT matches URL
    - Verifies task ownership
    - Toggles completed field
    - Returns updated task
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Cannot modify another user's task"
        )

    # Toggle completion status
    task.completed = not task.completed

    session.add(task)
    session.commit()
    session.refresh(task)

    # Convert Task model to TaskResponse
    return TaskResponse.model_validate(task)


@router.delete("/{user_id}/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: UUID,
    user_id: str = Depends(verify_user_access),
    session: Session = Depends(get_session)
):
    """
    Delete a task.

    - Validates user_id from JWT matches URL
    - Verifies task ownership
    - Deletes task from database
    - Returns 204 No Content on success
    """
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: Cannot delete another user's task"
        )

    session.delete(task)
    session.commit()

    return None
