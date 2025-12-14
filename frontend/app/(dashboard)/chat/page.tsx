'use client';

/**
 * Chat Page - AI-Powered Conversational Interface with OpenAI ChatKit
 *
 * Integrates ChatKit component with custom FastAPI backend using clientToken auth
 */

import { useEffect, useState } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { authClient } from '@/lib/auth-client';

export default function ChatPage() {
  const [clientToken, setClientToken] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Always pass a valid config to useChatKit (required)
  const { control } = useChatKit({
    api: {
      clientToken: clientToken || '',
      baseURL: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/chatkit`,
    },
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
      setError(err?.message || 'An error occurred');
    },
  });

  // Get JWT token and create session
  useEffect(() => {
    const initializeChat = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Get JWT from Better Auth
        const { data, error: authError } = await authClient.token();

        if (authError || !data?.token) {
          throw new Error('Not authenticated - please sign in');
        }

        // Create ChatKit session with JWT
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/chatkit/session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${data.token}`,
          },
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.detail || `Failed to initialize chat (${response.status})`
          );
        }

        const sessionData = await response.json();
        setClientToken(sessionData.client_secret);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to initialize chat';
        console.error('Chat initialization error:', err);
        setError(message);
      } finally {
        setIsLoading(false);
      }
    };

    initializeChat();
  }, []);

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
      {!isLoading && clientToken && (
        <div className="flex-1 overflow-hidden">
          <ChatKit control={control} className="h-full w-full" />
        </div>
      )}

      {/* No Token State */}
      {!isLoading && !clientToken && !error && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-600">Please sign in to use the chat</p>
          </div>
        </div>
      )}
    </div>
  );
}
