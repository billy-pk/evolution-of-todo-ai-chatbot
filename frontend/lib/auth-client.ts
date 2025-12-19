import { createAuthClient } from "better-auth/react";

/**
 * Better Auth client for React
 *
 * This client runs on the browser and provides:
 * - Authentication methods (signUp, signIn, signOut)
 * - Session hooks (useSession)
 * - Reactive state management with nano-store
 */
export const authClient = createAuthClient({
  /**
   * Base URL where the auth API is hosted
   * This should point to your Next.js app where the auth route handler is mounted
   *
   * In production (Vercel), automatically use the current domain
   * This allows the app to work with any Vercel deployment URL
   */
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL ||
    (typeof window !== 'undefined' ? window.location.origin : "http://localhost:3000"),
});

/**
 * Export convenient aliases for authentication methods
 */
export const { signIn, signUp, signOut, useSession } = authClient;

/**
 * Fetch JWT token from Better Auth /api/auth/token endpoint
 *
 * This directly calls the token endpoint which requires an active session.
 * The session cookie is automatically included with credentials: 'include'.
 */
export async function fetchJWTToken(): Promise<string | null> {
  try {
    const response = await fetch('/api/auth/token', {
      method: 'GET',
      credentials: 'include', // Include session cookies
    });

    if (!response.ok) {
      console.error('Failed to fetch JWT token:', response.status, response.statusText);
      return null;
    }

    const data = await response.json();
    return data.token || null;
  } catch (error) {
    console.error('Error fetching JWT token:', error);
    return null;
  }
}
