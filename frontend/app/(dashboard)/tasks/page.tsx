"use client";

/**
 * T050: Tasks page with TaskList and TaskForm integration
 * T051: Implement optimistic UI updates
 *
 * This page displays the task list, creation form, and handles
 * all task operations with optimistic updates and error handling.
 */

import { useEffect, useState } from "react";
import { useSession } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { api, APIError } from "@/lib/api";
import { Task, CreateTaskData, UpdateTaskData } from "@/lib/types";
import { TaskForm } from "@/components/TaskForm";
import { TaskList } from "@/components/TaskList";

export default function TasksPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [statusFilter, setStatusFilter] = useState<"all" | "pending" | "completed">("all");

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/signin");
    }
  }, [session, isPending, router]);

  // Load tasks on mount and when filter changes
  useEffect(() => {
    if (session?.user?.id) {
      loadTasks();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.user?.id, statusFilter]);

  const loadTasks = async () => {
    if (!session?.user?.id) return;

    // Debug: Log the session object to see what we're working with
    console.log("=== DEBUG: Session object ===", JSON.stringify(session, null, 2));
    console.log("=== DEBUG: User ID ===", session.user.id);

    try {
      setLoading(true);
      setError("");
      const tasks = await api.listTasks(session.user.id, statusFilter);
      setTasks(tasks || []);
    } catch (err: any) {
      console.error("=== DEBUG: Error loading tasks ===", err);
      if (err instanceof APIError && err.status === 401) {
        router.push("/signin");
      } else {
        setError(err.message || "Failed to load tasks");
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * T051: Optimistic UI - Create task
   * Immediately adds task to list, rollback on error
   */
  const handleCreateTask = async (data: CreateTaskData) => {
    if (!session?.user?.id) return;

    // Create optimistic task (new tasks are always pending)
    const optimisticTask: Task = {
      id: `temp-${Date.now()}`,
      user_id: session.user.id,
      title: data.title,
      description: data.description || null,
      completed: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    // T051: Optimistically add to list ONLY if current filter would show it
    // New tasks are always pending, so only add if filter is "all" or "pending"
    if (statusFilter === "all" || statusFilter === "pending") {
      setTasks((prev) => [optimisticTask, ...prev]);
    }

    try {
      // Make actual API call
      const createdTask = await api.createTask(session.user.id, data);

      // Replace optimistic task with real one (only if it was added)
      if (statusFilter === "all" || statusFilter === "pending") {
        setTasks((prev) =>
          prev.map((task) => (task.id === optimisticTask.id ? createdTask : task))
        );
      }
    } catch (err: any) {
      // T051: Rollback on error (only if it was added)
      if (statusFilter === "all" || statusFilter === "pending") {
        setTasks((prev) => prev.filter((task) => task.id !== optimisticTask.id));
      }

      if (err instanceof APIError && err.status === 401) {
        router.push("/signin");
      } else {
        setError(err.message || "Failed to create task");
      }
      throw err;
    }
  };

  /**
   * T051: Optimistic UI - Toggle completion
   */
  const handleToggleComplete = async (taskId: string) => {
    if (!session?.user?.id) return;

    // Find the task
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    // T051: Optimistically update
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed, updated_at: new Date().toISOString() } : t
      )
    );

    try {
      await api.toggleComplete(session.user.id, taskId);
      // Success - no need to update again
    } catch (err: any) {
      // T051: Rollback on error
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? task : t))
      );

      if (err instanceof APIError && err.status === 401) {
        router.push("/signin");
      } else {
        setError(err.message || "Failed to update task");
      }
    }
  };

  /**
   * T051: Optimistic UI - Delete task
   */
  const handleDelete = async (taskId: string) => {
    if (!session?.user?.id) return;

    // Store the task for rollback
    const deletedTask = tasks.find((t) => t.id === taskId);
    if (!deletedTask) return;

    // T051: Optimistically remove
    setTasks((prev) => prev.filter((t) => t.id !== taskId));

    try {
      await api.deleteTask(session.user.id, taskId);
      // Success - task already removed
    } catch (err: any) {
      // T051: Rollback on error
      setTasks((prev) => [...prev, deletedTask].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ));

      if (err instanceof APIError && err.status === 401) {
        router.push("/signin");
      } else {
        setError(err.message || "Failed to delete task");
      }
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleUpdateTask = async (data: CreateTaskData) => {
    if (!session?.user?.id || !editingTask) return;

    const originalTask = editingTask;

    // T051: Optimistically update - preserve existing fields, only update title/description
    setTasks((prev) =>
      prev.map((t) =>
        t.id === editingTask.id
          ? {
              ...t,
              title: data.title,
              description: data.description !== undefined ? data.description : t.description,
              updated_at: new Date().toISOString()
            }
          : t
      )
    );

    try {
      const updated = await api.updateTask(session.user.id, editingTask.id, data);
      setTasks((prev) =>
        prev.map((t) => (t.id === updated.id ? updated : t))
      );
      setEditingTask(null);
    } catch (err: any) {
      // T051: Rollback on error
      setTasks((prev) =>
        prev.map((t) => (t.id === originalTask.id ? originalTask : t))
      );

      if (err instanceof APIError && err.status === 401) {
        router.push("/signin");
      } else {
        setError(err.message || "Failed to update task");
      }
      throw err;
    }
  };

  if (isPending || loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    );
  }

  if (!session?.user) {
    return null; // Will redirect to signin
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
        <p className="mt-2 text-gray-600">
          Manage your tasks and stay organized
        </p>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
          <button
            onClick={() => setError("")}
            className="ml-2 text-red-900 hover:text-red-700"
          >
            ✕
          </button>
        </div>
      )}

      {/* Task creation/edit form */}
      {editingTask ? (
        <TaskForm
          onSubmit={handleUpdateTask}
          onCancel={() => setEditingTask(null)}
          initialData={{
            title: editingTask.title,
            description: editingTask.description || undefined,
          }}
          isEdit={true}
        />
      ) : (
        <TaskForm onSubmit={handleCreateTask} />
      )}

      {/* Filter controls */}
      <div className="flex gap-2 items-center">
        <span className="text-sm font-medium text-gray-700">Filter:</span>
        <div className="flex gap-2">
          {(["all", "pending", "completed"] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setStatusFilter(filter)}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                statusFilter === filter
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-700 hover:bg-gray-50 border border-gray-300"
              }`}
            >
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </button>
          ))}
        </div>
        <span className="ml-auto text-sm text-gray-600">
          {tasks.length} {tasks.length === 1 ? "task" : "tasks"}
        </span>
      </div>

      {/* Task list */}
      <TaskList
        tasks={tasks}
        onToggleComplete={handleToggleComplete}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}
