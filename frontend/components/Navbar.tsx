"use client";

/**
 * T048: Navbar component with user info and logout button
 * T072: Responsive breakpoints (hamburger menu on mobile, full nav on desktop)
 * T073: ARIA labels for accessibility
 *
 * Displays application navigation, user information,
 * and provides logout functionality.
 */

import { useSession, signOut } from "@/lib/auth-client";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function Navbar() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await signOut();
      router.push("/signin");
    } catch (error) {
      console.error("Logout failed:", error);
      setLoggingOut(false);
    }
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200" aria-label="Main navigation">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-14 sm:h-16">
          {/* Logo/Title */}
          <div className="flex items-center gap-6">
            <h1 className="text-lg sm:text-xl font-bold text-gray-900">
              📝 Todo App
            </h1>
            {/* T071: Navigation Links */}
            {session?.user && (
              <div className="hidden md:flex items-center gap-4">
                <a
                  href="/tasks"
                  className="text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
                >
                  Tasks
                </a>
                <a
                  href="/chat"
                  className="text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
                >
                  Chat
                </a>
              </div>
            )}
          </div>

          {/* Desktop navigation - hidden on mobile */}
          <div className="hidden md:flex items-center gap-3 sm:gap-4">
            {isPending ? (
              <div className="text-sm text-gray-500" role="status" aria-live="polite">
                Loading...
              </div>
            ) : session?.user ? (
              <>
                <div className="text-xs sm:text-sm">
                  <span className="text-gray-500">Signed in as </span>
                  <span className="font-medium text-gray-900">
                    {session.user.email || session.user.name || "User"}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  disabled={loggingOut}
                  className="px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  aria-label="Sign out of your account"
                >
                  {loggingOut ? "Logging out..." : "Logout"}
                </button>
              </>
            ) : (
              <a
                href="/signin"
                className="px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                aria-label="Sign in to your account"
              >
                Sign In
              </a>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle mobile menu"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="1.5"
                stroke="currentColor"
                aria-hidden="true"
              >
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu - shown when hamburger is clicked */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-3" role="menu" aria-label="Mobile navigation menu">
            {isPending ? (
              <div className="text-sm text-gray-500 px-2" role="status" aria-live="polite">
                Loading...
              </div>
            ) : session?.user ? (
              <div className="space-y-3">
                {/* Mobile navigation links */}
                <div className="space-y-1 px-2">
                  <a
                    href="/tasks"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Tasks
                  </a>
                  <a
                    href="/chat"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Chat
                  </a>
                </div>
                <div className="text-sm px-2">
                  <span className="text-gray-500 block">Signed in as</span>
                  <span className="font-medium text-gray-900 block mt-1">
                    {session.user.email || session.user.name || "User"}
                  </span>
                </div>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                  disabled={loggingOut}
                  className="w-full px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  aria-label="Sign out of your account"
                  role="menuitem"
                >
                  {loggingOut ? "Logging out..." : "Logout"}
                </button>
              </div>
            ) : (
              <a
                href="/signin"
                className="block w-full px-4 py-2 text-sm font-medium text-center text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                aria-label="Sign in to your account"
                role="menuitem"
              >
                Sign In
              </a>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
