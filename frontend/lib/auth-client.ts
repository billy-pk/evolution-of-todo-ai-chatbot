import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

/**
 * Better Auth client for React
 *
 * This client runs on the browser and provides:
 * - Authentication methods (signUp, signIn, signOut)
 * - Session hooks (useSession)
 * - Reactive state management with nano-store
 * - JWT token retrieval via jwtClient plugin
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
  /**
   * Plugins for extended functionality
   * - jwtClient: Enables authClient.token() for JWT retrieval
   */
  plugins: [
    jwtClient()
  ],
});

/**
 * Export convenient aliases for authentication methods
 */
export const { signIn, signUp, signOut, useSession } = authClient;

/**
 * Fetch JWT token using Better Auth jwtClient plugin
 *
 * Uses authClient.token() which properly handles authentication
 * and retrieves the JWT token for API requests.
 */
export async function fetchJWTToken(): Promise<string | null> {
  try {
    const { data, error } = await authClient.token();

    if (error) {
      console.error('Failed to fetch JWT token:', error);
      return null;
    }

    return data?.token || null;
  } catch (error) {
    console.error('Error fetching JWT token:', error);
    return null;
  }
}
