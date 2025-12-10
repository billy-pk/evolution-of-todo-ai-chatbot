"use client";

/**
 * T047: TaskList component to render array of TaskItem components
 * T070: Responsive breakpoints for mobile/desktop layouts
 * T073: ARIA labels for accessibility
 * T077: Loading states (spinner already implemented)
 *
 * Displays a list of tasks with support for empty states
 * and action handlers passed down to TaskItem components.
 */

import { Task } from "@/lib/types";
import { TaskItem } from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (taskId: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => Promise<void>;
  loading?: boolean;
}

export function TaskList({
  tasks,
  onToggleComplete,
  onEdit,
  onDelete,
  loading = false,
}: TaskListProps) {
  if (loading) {
    return (
      <div className="text-center py-12" role="status" aria-live="polite">
        <div
          className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"
          aria-label="Loading tasks"
        ></div>
        <p className="mt-2 text-gray-600">Loading tasks...</p>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div
        className="text-center py-8 sm:py-12 bg-gray-50 rounded-lg px-4"
        role="status"
        aria-label="No tasks available"
      >
        <svg
          className="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <h3 className="mt-2 text-base sm:text-lg font-medium text-gray-900">No tasks yet</h3>
        <p className="mt-1 text-xs sm:text-sm text-gray-500">
          Get started by creating your first task!
        </p>
      </div>
    );
  }

  return (
    <div
      className="space-y-2 sm:space-y-3"
      role="list"
      aria-label="Task list"
    >
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggleComplete={onToggleComplete}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
