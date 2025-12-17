import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

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
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",

  /**
   * Secret used for signing tokens and encrypting sessions
   * Must match the BETTER_AUTH_SECRET in backend for JWT validation
   */
  secret: process.env.BETTER_AUTH_SECRET,

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
