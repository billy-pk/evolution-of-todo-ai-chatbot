"use client";

/**
 * T045: TaskForm component for creating/editing tasks
 * T071: Responsive breakpoints (stack on mobile, side-by-side on desktop)
 * T073: ARIA labels for accessibility
 * T074: Keyboard navigation (Enter to submit, Escape to cancel)
 *
 * This component provides a form for creating new tasks
 * with title and description inputs, along with validation.
 */

import { useState, useEffect } from "react";
import { CreateTaskData } from "@/lib/types";

interface TaskFormProps {
  onSubmit: (data: CreateTaskData) => Promise<void>;
  onCancel?: () => void;
  initialData?: CreateTaskData;
  isEdit?: boolean;
}

export function TaskForm({
  onSubmit,
  onCancel,
  initialData,
  isEdit = false,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || "");
  const [description, setDescription] = useState(initialData?.description || "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    if (title.length > 200) {
      setError("Title must be 200 characters or less");
      return;
    }

    if (description && description.length > 1000) {
      setError("Description must be 1000 characters or less");
      return;
    }

    setLoading(true);

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
      });

      // Reset form after successful creation (not edit)
      if (!isEdit) {
        setTitle("");
        setDescription("");
      }
    } catch (err: any) {
      setError(err.message || "Failed to save task");
    } finally {
      setLoading(false);
    }
  };

  // T074: Keyboard navigation - Escape to cancel
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && onCancel) {
        onCancel();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onCancel]);

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 bg-white p-4 sm:p-6 rounded-lg shadow-md"
      aria-label={isEdit ? "Edit task form" : "Create task form"}
    >
      <h2 className="text-lg sm:text-xl font-semibold">
        {isEdit ? "Edit Task" : "Create New Task"}
      </h2>

      {error && (
        <div
          className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm"
          role="alert"
          aria-live="polite"
        >
          {error}
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title *
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={200}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
          placeholder="Enter task title"
          disabled={loading}
          aria-required="true"
          aria-describedby="title-help"
        />
        <p id="title-help" className="text-xs text-gray-500 mt-1">
          {title.length}/200 characters
        </p>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description (optional)
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={1000}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm sm:text-base"
          placeholder="Enter task description"
          disabled={loading}
          aria-describedby="description-help"
        />
        <p id="description-help" className="text-xs text-gray-500 mt-1">
          {description.length}/1000 characters
        </p>
      </div>

      {/* T071: Responsive button layout - stack on mobile, side-by-side on larger screens */}
      <div className="flex flex-col sm:flex-row gap-2">
        <button
          type="submit"
          disabled={loading || !title.trim()}
          className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
          aria-label={isEdit ? "Update task" : "Add task"}
        >
          {loading ? "Saving..." : isEdit ? "Update Task" : "Add Task"}
        </button>

        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 transition-colors text-sm sm:text-base"
            aria-label="Cancel editing"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
