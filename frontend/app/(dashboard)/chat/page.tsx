'use client';

/**
 * Chat Page - AI-Powered Conversational Interface with OpenAI ChatKit
 *
 * Integrates ChatKit component with custom FastAPI backend using getClientSecret
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from '@/lib/auth-client';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { authClient } from '@/lib/auth-client';

export default function ChatPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push('/signin');
    }
  }, [session, isPending, router]);

  // ChatKit configuration for custom backend
  const { control } = useChatKit({
    api: {
      // Custom backend URL - ChatKit will POST requests here
      url: `${apiUrl}/chatkit`,
      // Domain key - required for production, skipped on localhost
      domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || 'localhost-dev',
      // Custom fetch to inject our auth headers
      async fetch(input: RequestInfo | URL, init?: RequestInit) {
        console.log('🔵 ChatKit: Custom fetch called', { url: input });

        // Get Better Auth JWT for authenticating with our backend
        const { data, error: authError } = await authClient.token();
        if (authError || !data?.token) {
          console.error('ChatKit: Auth error', authError);
          throw new Error('Not authenticated - please sign in');
        }

        // Inject auth header
        const headers = {
          ...init?.headers,
          'Authorization': `Bearer ${data.token}`,
        };

        console.log('ChatKit: Fetching with auth header');
        return fetch(input, {
          ...init,
          headers,
        });
      },
    },
    initialThread: null,  // Start with new thread view
    theme: {
      colorScheme: 'light',
      color: {
        accent: {
          primary: '#2563eb', // blue-600
          level: 2,
        },
      },
      radius: 'round',
      density: 'normal',
      typography: { fontFamily: 'system-ui, -apple-system, sans-serif' },
    },
    composer: {
      placeholder: 'Ask me to create tasks, list tasks, or help you manage your todo list...',
    },
    startScreen: {
      greeting: 'Welcome to AI Assistant',
      prompts: [
        {
          label: 'Create a task',
          prompt: 'Create a new task for me',
          icon: 'notebook-pencil',
        },
        {
          label: 'List tasks',
          prompt: 'Show me all my tasks',
          icon: 'search',
        },
        {
          label: 'Get help',
          prompt: 'Help me organize my tasks',
          icon: 'lightbulb',
        },
      ],
    },
    onError: ({ error: err }) => {
      console.error('ChatKit error:', err);
      setError(err?.message || 'An error occurred');
    },
    onThreadChange: ({ threadId }) => {
      console.log('ChatKit: Thread changed', { threadId });
    },
  });

  // Show loading state while checking authentication
  if (isPending) {
    return (
      <div className="flex flex-col h-screen bg-white items-center justify-center">
        <div className="text-center">
          <div className="inline-block">
            <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
          <p className="text-gray-600 mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render ChatKit if not authenticated (will redirect)
  if (!session?.user) {
    return null;
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Error Display */}
      {error && (
        <div className="mx-4 mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex-shrink-0">
          <p className="text-red-800 text-sm">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800 text-xs mt-2 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* ChatKit Component - Full height, ChatKit provides its own greeting */}
      <ChatKit
        control={control}
        className="flex-1 w-full"
        style={{ minHeight: '400px' }}
      />
    </div>
  );
}
