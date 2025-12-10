/**
 * Type definitions for the Todo application
 */

/**
 * Task entity from the backend
 */
export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Data required to create a new task
 */
export interface CreateTaskData {
  title: string;
  description?: string;
}

/**
 * Data that can be updated in a task
 */
export interface UpdateTaskData {
  title?: string;
  description?: string;
  completed?: boolean;
}

/**
 * Response from the list tasks endpoint
 */
export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

/**
 * User session data from Better Auth
 */
export interface User {
  id: string;
  email: string;
  name: string;
  image?: string;
}

/**
 * Session data from Better Auth
 */
export interface Session {
  user: User;
  session: {
    id: string;
    userId: string;
    expiresAt: string;
    token: string;
  };
}
