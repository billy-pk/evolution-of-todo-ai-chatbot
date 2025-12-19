import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

// Calculate baseURL and trustedOrigins
const baseURL = process.env.BETTER_AUTH_URL ||
  (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "http://localhost:3000");

const trustedOrigins = (() => {
  const origins: string[] = [];

  // Always add localhost for development
  origins.push("http://localhost:3000");

  // Add Vercel auto-generated URL if available
  if (process.env.VERCEL_URL) {
    // Add with https
    origins.push(`https://${process.env.VERCEL_URL}`);
    // Also try without www
    origins.push(`https://www.${process.env.VERCEL_URL}`);
  }

  // Add custom production domain if set
  if (process.env.NEXT_PUBLIC_SITE_URL) {
    origins.push(process.env.NEXT_PUBLIC_SITE_URL);
  }

  console.log("📍 Calculated trusted origins:", origins);

  return origins;
})();

// Debug logging (only in development or when needed)
console.log("🔐 Better Auth Configuration:");
console.log("  baseURL:", baseURL);
console.log("  trustedOrigins:", trustedOrigins);
console.log("  VERCEL_URL:", process.env.VERCEL_URL);
console.log("  BETTER_AUTH_SECRET set:", !!process.env.BETTER_AUTH_SECRET);
console.log("  DATABASE_URL set:", !!process.env.DATABASE_URL);

/**
 * Better Auth server configuration
 *
 * This configuration runs on the server side and handles:
 * - Email/password authentication
 * - Session management
 * - JWT token generation
 * - User data storage in PostgreSQL
 */
export const auth = betterAuth({
  /**
   * PostgreSQL database connection for storing users and sessions
   * Note: Node.js pg library needs explicit SSL config for Neon
   */
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.DATABASE_URL?.includes('neon.tech')
      ? { rejectUnauthorized: false }
      : undefined,
  }),

  /**
   * Base URL where the auth endpoints are hosted
   */
  baseURL,

  /**
   * Secret used for signing tokens and encrypting sessions
   * Must match the BETTER_AUTH_SECRET in backend for JWT validation
   */
  secret: process.env.BETTER_AUTH_SECRET,

  /**
   * Trusted origins - Allow Vercel URLs and localhost
   * Better Auth validates requests come from trusted domains
   */
  trustedOrigins,

  /**
   * Advanced options for production deployment
   */
  advanced: {
    /**
     * Disable origin check temporarily for debugging
     * TODO: Remove this after fixing trustedOrigins issue
     */
    disableCSRFCheck: true,
  },

  /**
   * Enable email and password authentication
   */
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
    /**
     * Automatically sign in users after successful signup
     */
    autoSignIn: true,
  },

  /**
   * Session configuration
   */
  session: {
    /**
     * Session expires in 7 days
     */
    expiresIn: 60 * 60 * 24 * 7,
    /**
     * Update session every 24 hours
     */
    updateAge: 60 * 60 * 24,
  },

  /**
   * Enable JWT plugin for token-based authentication
   * This generates JWT tokens that include user_id in the payload
   * Note: JWT plugin configuration is handled by Better Auth defaults
   */
  plugins: [
    jwt(),
  ],
});

/**
 * Type inference for session data
 * Use this type for type-safe session handling
 */
export type Session = typeof auth.$Infer.Session;
