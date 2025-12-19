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
   *
   * Automatically uses Vercel deployment URL in production
   * For local development, uncomment: "http://localhost:3000"
   */
  baseURL: process.env.BETTER_AUTH_URL ||
    (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "http://localhost:3000"),

  /**
   * Secret used for signing tokens and encrypting sessions
   * Must match the BETTER_AUTH_SECRET in backend for JWT validation
   */
  secret: process.env.BETTER_AUTH_SECRET,

  /**
   * Trusted origins - Allow Vercel URLs and localhost
   * Better Auth validates requests come from trusted domains
   *
   * Environment variables used:
   * - VERCEL_URL: Auto-provided by Vercel (current deployment URL)
   * - NEXT_PUBLIC_SITE_URL: Your production domain (set in Vercel env vars)
   */
  trustedOrigins: (() => {
    const origins: string[] = [];

    // Always add localhost for development
    origins.push("http://localhost:3000");

    // Add Vercel auto-generated URL if available
    if (process.env.VERCEL_URL) {
      origins.push(`https://${process.env.VERCEL_URL}`);
    }

    // Add custom production domain if set
    if (process.env.NEXT_PUBLIC_SITE_URL) {
      origins.push(process.env.NEXT_PUBLIC_SITE_URL);
    }

    return origins;
  })(),

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
