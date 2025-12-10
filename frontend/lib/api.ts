/**
 * API client for interacting with the FastAPI backend
 *
 * This client automatically:
 * - Attaches JWT tokens from Better Auth
 * - Handles errors consistently
 * - Provides type-safe methods for all backend endpoints
 */

import { authClient } from "./auth-client";
import { Task, CreateTaskData, UpdateTaskData, TaskListResponse } from "./types";

/**
 * Base URL for the FastAPI backend
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

// Token cache to avoid fetching on every request (reduces cursor loading time)
let cachedToken: string | null = null;
let tokenExpiry: number = 0;

/**
 * Get the JWT token from Better Auth session (with caching)
 */
async function getAuthToken(): Promise<string | null> {
  try {
    // Return cached token if still valid (not expired in next 60 seconds)
    if (cachedToken && tokenExpiry > Date.now() + 60000) {
      return cachedToken;
    }

    const { data, error } = await authClient.token();

    if (error || !data?.token) {
      cachedToken = null;
      return null;
    }

    // Cache the token for 14 minutes (tokens expire in 15 minutes)
    cachedToken = data.token;
    tokenExpiry = Date.now() + (14 * 60 * 1000);

    return data.token;
  } catch (err) {
    console.error("Error getting auth token:", err);
    cachedToken = null;
    return null;
  }
}

/**
 * Make an authenticated API request
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  if (!token) {
    throw new APIError("Not authenticated - no valid token", 401);
  }

  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = `API error: ${response.status}`;
    let errorDetails;

    try {
      errorDetails = await response.json();
      errorMessage = errorDetails.detail || errorDetails.message || errorMessage;
    } catch {
      // If parsing JSON fails, use status text
      errorMessage = response.statusText || errorMessage;
    }

    throw new APIError(errorMessage, response.status, errorDetails);
  }

  // Handle 204 No Content responses (e.g., DELETE operations)
  if (response.status === 204 || response.headers.get("content-length") === "0") {
    return null as T;
  }

  // Only parse JSON if there's content
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }

  return null as T;
}

/**
 * API methods for task operations
 */
export const api = {
  /**
   * List all tasks for the authenticated user
   */
  listTasks: async (
    userId: string,
    status?: "all" | "pending" | "completed"
  ): Promise<Task[]> => {
    const queryParams = status && status !== "all" ? `?status=${status}` : "";
    const response = await fetchAPI<TaskListResponse>(
      `/api/${userId}/tasks${queryParams}`
    );
    return response.tasks;
  },

  /**
   * Get a single task by ID
   */
  getTask: async (userId: string, taskId: string): Promise<Task> => {
    return fetchAPI<Task>(`/api/${userId}/tasks/${taskId}`);
  },

  /**
   * Create a new task
   */
  createTask: async (
    userId: string,
    data: CreateTaskData
  ): Promise<Task> => {
    return fetchAPI<Task>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Update an existing task
   */
  updateTask: async (
    userId: string,
    taskId: string,
    data: UpdateTaskData
  ): Promise<Task> => {
    return fetchAPI<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * Toggle task completion status
   */
  toggleComplete: async (userId: string, taskId: string): Promise<Task> => {
    return fetchAPI<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
    });
  },

  /**
   * Delete a task
   */
  deleteTask: async (userId: string, taskId: string): Promise<void> => {
    await fetchAPI<void>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    });
  },
};
