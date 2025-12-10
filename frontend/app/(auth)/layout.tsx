/**
 * T025: Auth layout - Centered layout for authentication pages
 *
 * This layout component provides a centered, card-based design
 * for authentication pages (signin, signup).
 */

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md">
        {children}
      </div>
    </div>
  );
}
