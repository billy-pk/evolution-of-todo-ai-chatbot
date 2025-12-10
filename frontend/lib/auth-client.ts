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
   */
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
});

/**
 * Export convenient aliases for authentication methods
 */
export const { signIn, signUp, signOut, useSession } = authClient;
