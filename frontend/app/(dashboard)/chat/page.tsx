'use client';

/**
 * Chat Page - AI-Powered Conversational Interface with OpenAI ChatKit
 *
 * Phase 10: ChatKit Integration (002-chatkit-refactor)
 *
 * Features:
 * - OpenAI ChatKit component for professional chat UI
 * - Message history display with streaming support
 * - Loading indicator with "thinking" status
 * - New conversation button
 * - Error handling for API responses
 * - Theme customization
 *
 * Success Criteria: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-048
 */

import { useState, useEffect, useCallback } from 'react';
import { ChatKit, useChatKit, type ChatKitOptions } from '@openai/chatkit-react';
import { authClient } from '@/lib/auth-client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: any[];
  messages: Message[];
  metadata: {
    model: string;
    tokens_used: number;
    conversation_message_count: number;
  };
}

/**
 * Get JWT token from Better Auth for authenticated API requests
 */
async function getAuthToken(): Promise<string | null> {
  try {
    const { data, error } = await authClient.token();
    if (error || !data?.token) {
      return null;
    }
    return data.token;
  } catch (err) {
    console.error('Error getting auth token:', err);
    return null;
  }
}

export default function ChatPage() {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Initialize ChatKit with custom backend integration
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        try {
          // Get JWT token from Better Auth
          const token = await getAuthToken();
          if (!token) {
            throw new Error('Not authenticated - no valid token');
          }

          const endpoint = existing ? '/api/chatkit/refresh' : '/api/chatkit/session';
          const body = existing ? { token: existing } : {};

          const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: Object.keys(body).length > 0 ? JSON.stringify(body) : undefined,
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
              errorData.detail || `Failed to create chat session (${response.status})`
            );
          }

          const data = await response.json();
          return data.client_secret;
        } catch (err) {
          console.error('Error getting client secret:', err);
          throw err;
        }
      },
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
      tools: [],
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
    onError: ({ error: chatError }) => {
      console.error('ChatKit error:', chatError);
      handleError(chatError);
    },
    onThreadChange: ({ threadId }) => {
      // Update conversation ID when thread changes
      setConversationId(threadId || null);
      if (threadId) {
        // Save to localStorage for persistence
        localStorage.setItem('lastThreadId', threadId);
      }
    },
  } as ChatKitOptions);

  // Handle errors from ChatKit
  const handleError = useCallback((err: any) => {
    const errorMessage =
      err?.status === 401
        ? 'Authentication required. Please sign in again.'
        : err?.status === 403
        ? 'Access denied. You do not have permission to access this conversation.'
        : err?.status === 404
        ? 'Conversation not found.'
        : err?.status === 429
        ? 'Rate limit exceeded. Please wait a moment and try again.'
        : err?.status === 500
        ? 'Server error. Please try again later.'
        : err?.message || 'Failed to send message. Please try again.';

    setError(errorMessage);
  }, []);

  // Load last conversation from localStorage if available
  useEffect(() => {
    const lastThreadId = localStorage.getItem('lastThreadId');
    if (lastThreadId) {
      setConversationId(lastThreadId);
    }
  }, []);

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
          <p className="text-sm text-gray-500 mt-1">
            {conversationId
              ? `Conversation: ${conversationId.slice(0, 8)}...`
              : 'Start a new conversation'}
          </p>
        </div>
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

      {/* ChatKit Component */}
      <div className="flex-1 overflow-hidden">
        <ChatKit control={control} className="h-full w-full" />
      </div>
    </div>
  );
}
