# OpenAI ChatKit Integration Implementation

## Current Status
- ✅ Chat page refactored to use `@openai/chatkit-react` component
- ✅ ChatKit configured with custom theme, prompts, and error handling
- ✅ Backend ChatKit integration endpoints implemented
- ✅ Frontend authentication with Better Auth tokens
- ⏳ End-to-end testing

## Completed Implementation

### 1. Backend Endpoints (routes/chatkit.py)

#### POST /api/chatkit/session
Creates a new ChatKit session for the authenticated user.

**Request:**
```bash
curl -X POST http://localhost:8000/api/chatkit/session \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "client_secret": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "user_uuid"
}
```

**Purpose:**
- Validates Better Auth JWT token
- Creates HS256-signed session token with 30-minute expiry
- Returns client_secret for ChatKit component

#### POST /api/chatkit/refresh
Refreshes an expired ChatKit session token.

**Request:**
```json
{
  "token": "expired_client_secret"
}
```

**Response:**
```json
{
  "client_secret": "new_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "user_uuid"
}
```

#### GET /api/chatkit/threads
Lists all conversation threads (conversations) for the user.

**Response:**
```json
{
  "threads": [
    {
      "id": "conversation_uuid",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "message_count": 5
    }
  ]
}
```

#### POST /api/chatkit/threads
Creates a new thread (conversation).

**Response:**
```json
{
  "id": "new_conversation_uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/chatkit/threads/{thread_id}
Retrieves a specific thread with all its messages.

**Response:**
```json
{
  "id": "conversation_uuid",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "messages": [
    {
      "id": "message_uuid",
      "role": "user",
      "content": "Hello",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": "response_uuid",
      "role": "assistant",
      "content": "Hi there!",
      "created_at": "2024-01-01T00:00:01Z"
    }
  ]
}
```

#### POST /api/chatkit/messages
Sends a message to a thread and returns AI response.

**Request:**
```json
{
  "thread_id": "conversation_uuid",
  "message": "Create a task to buy groceries"
}
```

**Response:**
```json
{
  "message_id": "message_uuid",
  "response_id": "response_message_uuid",
  "response": "I've created a task 'buy groceries' for you.",
  "thread_id": "conversation_uuid"
}
```

**Flow:**
1. Validates ChatKit session token
2. Saves user message to database
3. Processes through AI agent with conversation history
4. Saves assistant response to database
5. Updates conversation timestamp
6. Returns both messages

### 2. Frontend Integration (chat/page.tsx)

#### Authentication Flow
```typescript
async function getAuthToken(): Promise<string | null> {
  const { data, error } = await authClient.token();
  return data?.token || null;
}
```

#### Session Management
```typescript
getClientSecret: async (existing) => {
  const token = await getAuthToken();
  const endpoint = existing ? '/api/chatkit/refresh' : '/api/chatkit/session';

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: existing ? JSON.stringify({ token: existing }) : undefined,
  });

  return (await response.json()).client_secret;
}
```

#### ChatKit Configuration
- **Theme:** Light mode with blue accent (#2563eb)
- **Start Screen Prompts:**
  - "Create a task" (pencil icon)
  - "List tasks" (list icon)
  - "Get help" (lightbulb icon)
- **Error Handling:** Custom error messages for HTTP status codes
- **Persistence:** localStorage tracks last thread ID

### 3. Architecture

```
ChatKit UI Component (React)
    ↓
getClientSecret() → /api/chatkit/session (with JWT)
    ↓
/api/chatkit/refresh (token renewal)
    ↓
User interactions stored in state
    ↓
Chat messages routed through AI Agent
    ↓
/api/chatkit/messages → Process message + AI response
    ↓
PostgreSQL (conversations + messages tables)
```

## Database Mapping

| ChatKit Concept | Our Database |
|-----------------|--------------|
| `client_secret` | JWT token with user_id + type |
| `thread_id` | `conversation.id` |
| `thread.messages` | `message` table records |
| Thread created_at | `conversation.created_at` |

## Authentication Security

**Session Token Format (HS256):**
```python
{
  "user_id": "uuid",
  "type": "chatkit_session",
  "iat": 1704067200,
  "exp": 1704069000  # 30 minutes
}
```

**Signed with:** `settings.BETTER_AUTH_SECRET` (same as JWT validation)

## Testing Checklist

- [ ] Backend can start without import errors
- [ ] ChatKit session endpoint returns valid token
- [ ] Frontend can authenticate and get client_secret
- [ ] ChatKit component renders properly
- [ ] Message sending triggers `/api/chatkit/messages`
- [ ] AI response appears in ChatKit UI
- [ ] Conversation persistence works (reload page)
- [ ] Error handling displays correctly
- [ ] Token refresh works when expired
- [ ] Multi-user isolation (different users, different conversations)

## Known Limitations

1. **No Real-Time Streaming:** Messages are processed completely before returning
   - Could implement SSE for streaming responses (future enhancement)

2. **No File Attachments:** ChatKit supports attachments, but not yet integrated
   - Would require S3/blob storage implementation

3. **Limited Entity Tagging:** ChatKit supports @-mentions, not yet implemented
   - Would need entity search endpoint implementation

## Future Enhancements

1. **Response Streaming**
   - Implement SSE for real-time token streaming
   - Configuration: `streaming: true` in ChatKitOptions

2. **File Attachments**
   - Add attachment storage (S3/local disk)
   - Implement ThreadItemConverter for attachment handling

3. **Entity References**
   - Add `/api/chatkit/entities/search` endpoint
   - Enable @-mention support in composer

4. **Conversation Management UI**
   - Thread list sidebar
   - Delete thread functionality
   - Search/filter conversations

## References

- [OpenAI ChatKit Documentation](https://github.com/openai/chatkit-js)
- [ChatKit React Binding](https://github.com/openai/chatkit-js/tree/main/packages/react)
- [ChatKit Advanced Samples](https://github.com/openai/openai-chatkit-advanced-samples)
- [JWT Token Format](https://jwt.io/)
