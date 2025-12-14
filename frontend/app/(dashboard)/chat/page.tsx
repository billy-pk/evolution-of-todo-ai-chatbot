'use client';

/**
 * Chat Page - AI-Powered Conversational Interface with OpenAI ChatKit
 *
 * Integrates ChatKit component with custom FastAPI backend using CustomApiConfig
 */

import { useState, useEffect } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { authClient } from '@/lib/auth-client';

console.log('🔴 FILE LOADED - chat/page.tsx');

export default function ChatPage() {
  const [error, setError] = useState<string | null>(null);
  const [clientToken, setClientToken] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  console.log('🟢 COMPONENT RENDERING, apiUrl:', apiUrl);
  console.log('🟢 State:', { isLoading, hasToken: !!clientToken, initialized });

  // Get session token on mount - simplified to avoid hydration issues
  useEffect(() => {
    if (initialized) return; // Prevent double execution in strict mode

    setInitialized(true);
    console.log('useEffect triggered!');

    (async () => {
      try {
        console.log('Getting session token...');

        // Get JWT from Better Auth
        const { data, error: authError } = await authClient.token();
        console.log('Better Auth token result:', { hasToken: !!data?.token, error: authError });

        if (authError || !data?.token) {
          throw new Error('Not authenticated - please sign in');
        }

        // Create ChatKit session with JWT
        console.log('Calling session endpoint:', `${apiUrl}/api/chatkit/session`);
        const response = await fetch(`${apiUrl}/api/chatkit/session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${data.token}`,
          },
        });

        console.log('Session endpoint response:', response.status, response.statusText);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Failed to initialize chat (${response.status})`
          );
        }

        const sessionData = await response.json();
        console.log('Session data received, has client_secret:', !!sessionData.client_secret);
        setClientToken(sessionData.client_secret);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to get session token';
        console.error('Session token error:', err);
        setError(message);
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  // Use CustomApiConfig for self-hosted backend
  const chatKitResult = useChatKit({
    api: {
      url: `${apiUrl}/chatkit`,
      domainKey: 'task-manager',
      fetch: async (url: string, options: RequestInit = {}) => {
        console.log('ChatKit fetch called:', url, options);

        // Add Authorization header with session token if available
        const headers = new Headers(options.headers);
        if (clientToken) {
          headers.set('Authorization', `Bearer ${clientToken}`);
          console.log('Added Authorization header with token');
        } else {
          console.warn('No clientToken available yet');
        }

        return fetch(url, {
          ...options,
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
          name: 'Create a task',
          prompt: 'Create a new task for me',
          icon: 'pencil',
        },
        {
          name: 'List tasks',
          prompt: 'Show me all my tasks',
          icon: 'list',
        },
        {
          name: 'Get help',
          prompt: 'Help me organize my tasks',
          icon: 'lightbulb',
        },
      ],
    },
    onError: ({ error: err }) => {
      console.error('ChatKit error:', err);
      console.error('Error details:', JSON.stringify(err, null, 2));
      setError(err?.message || 'An error occurred');
    },
  });

  console.log('ChatKit isLoading:', isLoading, 'clientToken present:', !!clientToken);
  console.log('Will render ChatKit?', !isLoading && clientToken);

  console.log('useChatKit result:', chatKitResult);
  console.log('control object:', chatKitResult.control);

  const { control, setThreadId } = chatKitResult;

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
        <p className="text-sm text-gray-500 mt-1">Chat with your AI-powered task manager</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mx-6 mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800 text-xs mt-2 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block">
              <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            </div>
            <p className="text-gray-600 mt-4">Initializing chat...</p>
          </div>
        </div>
      )}

      {/* ChatKit Component */}
      {!isLoading && clientToken ? (
        <div className="flex-1 overflow-hidden">
          {console.log('Rendering ChatKit component now...')}
          <ChatKit
            control={control}
            className="h-full w-full"
          />
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            {console.log('NOT rendering ChatKit:', { isLoading, hasToken: !!clientToken })}
            <p className="text-gray-600">
              {isLoading ? 'Loading...' : 'Please wait...'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
