import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

/**
 * Better Auth client for React
 *
 * This client runs on the browser and provides:
 * - Authentication methods (signUp, signIn, signOut)
 * - Session hooks (useSession)
 * - JWT token retrieval (via jwtClient plugin)
 * - Reactive state management with nano-store
 */
export const authClient = createAuthClient({
  /**
   * Base URL where the auth API is hosted
   * This should point to your Next.js app where the auth route handler is mounted
   *
   * In production (Vercel), automatically use the current domain
   * This allows the app to work with any Vercel deployment URL
   *
   * For local development, uncomment the line below:
   * baseURL: "http://localhost:3000",
   */
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL ||
    (typeof window !== 'undefined' ? window.location.origin : "http://localhost:3000"),

  /**
   * Plugins for extended functionality
   * - jwtClient: Enables authClient.token() to retrieve JWT tokens
   */
  plugins: [
    jwtClient(),
  ],
});

/**
 * Export convenient aliases for authentication methods
 */
export const { signIn, signUp, signOut, useSession } = authClient;
