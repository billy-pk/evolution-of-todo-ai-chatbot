"use client";

/**
 * T046: TaskItem component to display a single task
 * T070: Responsive breakpoints for mobile/desktop layouts
 * T073: ARIA labels for accessibility
 *
 * Shows task title, description, timestamps, and action buttons
 * (toggle complete, edit, delete).
 */

import { Task } from "@/lib/types";
import { useState } from "react";

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => Promise<void>;
}

export function TaskItem({
  task,
  onToggleComplete,
  onEdit,
  onDelete,
}: TaskItemProps) {
  const [loading, setLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleToggleComplete = async () => {
    setLoading(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      await onDelete(task.id);
      setShowDeleteConfirm(false);
    } catch (error) {
      setLoading(false);
      // Error handling is done in parent component
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div
      className={`bg-white p-3 sm:p-4 rounded-lg shadow-sm border ${
        task.completed ? "border-green-200 bg-green-50" : "border-gray-200"
      }`}
      role="listitem"
      aria-label={`Task: ${task.title}, ${task.completed ? "completed" : "pending"}`}
    >
      <div className="flex items-start gap-2 sm:gap-3">
        {/* Checkbox for completion */}
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggleComplete}
          disabled={loading}
          className="mt-0.5 sm:mt-1 h-4 w-4 sm:h-5 sm:w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
          aria-label={task.completed ? "Mark task as incomplete" : "Mark task as complete"}
          aria-describedby={`task-title-${task.id}`}
        />

        {/* Task content */}
        <div className="flex-1 min-w-0">
          <h3
            id={`task-title-${task.id}`}
            className={`text-base sm:text-lg font-medium ${
              task.completed ? "line-through text-gray-500" : "text-gray-900"
            }`}
          >
            {task.title}
          </h3>

          {task.description && (
            <p className={`mt-1 text-xs sm:text-sm ${
              task.completed ? "text-gray-400" : "text-gray-600"
            }`}>
              {task.description}
            </p>
          )}

          <div className="mt-2 flex flex-wrap gap-2 sm:gap-4 text-xs text-gray-500">
            <span>Created: {formatDate(task.created_at)}</span>
            {task.updated_at !== task.created_at && (
              <span>Updated: {formatDate(task.updated_at)}</span>
            )}
          </div>
        </div>

        {/* Action buttons - stack on mobile, side-by-side on desktop */}
        <div className="flex flex-col sm:flex-row gap-1 sm:gap-2">
          <button
            onClick={() => onEdit(task)}
            disabled={loading}
            className="px-2 sm:px-3 py-1 text-xs sm:text-sm text-blue-600 hover:bg-blue-50 rounded disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label={`Edit task: ${task.title}`}
          >
            Edit
          </button>

          {!showDeleteConfirm ? (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              disabled={loading}
              className="px-2 sm:px-3 py-1 text-xs sm:text-sm text-red-600 hover:bg-red-50 rounded disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
              aria-label={`Delete task: ${task.title}`}
            >
              Delete
            </button>
          ) : (
            <div className="flex gap-1" role="group" aria-label="Delete confirmation">
              <button
                onClick={handleDelete}
                disabled={loading}
                className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
                aria-label="Confirm deletion"
              >
                Confirm
              </button>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={loading}
                className="px-2 py-1 text-xs border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
                aria-label="Cancel deletion"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
