# OpenAI ChatKit Integration Notes

## Current Status
- ✅ Chat page refactored to use `@openai/chatkit-react` component
- ✅ ChatKit configured with custom theme, prompts, and error handling
- ⏳ Backend integration endpoints needed

## What's Required for Full Integration

### 1. ChatKit Session Endpoint
The frontend expects a `POST /api/chatkit/session` endpoint that returns:
```json
{
  "client_secret": "session_token_string"
}
```

**Purpose**: ChatKit uses session tokens to manage authentication and state. This endpoint should:
- Validate the user's JWT token
- Create or retrieve a ChatKit session for the user
- Return a secure session token

### 2. ChatKit Message Adapter
ChatKit uses OpenAI's Threads API format, but our backend uses a custom conversation model. We need to:

**Option A: Bridge Adapter**
- Create a middleware that translates ChatKit's expected message format to our database schema
- Map ChatKit threads → our conversations
- Map ChatKit messages → our messages table

**Option B: Native Integration**
- Implement ChatKit's expected API endpoints on the backend
- Use our conversation database as the backing store
- Handle message streaming and real-time updates

### 3. Frontend Integration Points

#### getClientSecret()
Currently calls `/api/chatkit/session`. This should:
```typescript
const response = await fetch('/api/chatkit/session', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}` // Include JWT from Better Auth
  },
});
```

#### Theme Customization
Currently set to light theme with blue accent. Can be updated via `ChatKitOptions.theme`

#### Start Screen Prompts
Configured with 3 default prompts:
- "Create a task"
- "List tasks"
- "Get help"

These can be customized in the `startScreen.prompts` array

## Architecture Overview

```
Frontend (ChatKit Component)
    ↓
ChatKit API Calls
    ↓
/api/chatkit/session → Backend Session Manager
/api/chatkit/threads → Backend Thread/Conversation Manager
/api/chatkit/messages → Backend Message Handler
    ↓
Custom Conversation Database (PostgreSQL)
```

## Key Differences from OpenAI's Threads API

| Feature | OpenAI Threads | Our Implementation |
|---------|---------------|--------------------|
| Session Model | JWT-based | Custom sessions |
| Storage | OpenAI servers | PostgreSQL (Neon) |
| Persistence | Automatic | Explicit DB saves |
| User Isolation | Thread ownership | user_id column |
| Conversations | threads | conversations table |
| Messages | messages | messages table |

## Next Steps

1. **Create Session Endpoint** (`POST /api/chatkit/session`)
   - Validate JWT token
   - Return ChatKit-compatible session token
   - Duration: 15-30 minutes (matching Better Auth session)

2. **Implement ChatKit API Bridge**
   - Add `/api/chatkit/threads` endpoint for thread management
   - Add `/api/chatkit/messages` endpoint for message handling
   - Map to existing conversation/message tables

3. **Test Integration**
   - Verify ChatKit component renders properly
   - Test message sending through ChatKit UI
   - Confirm conversation persistence
   - Check error handling

4. **Streaming Support** (Optional)
   - Implement Server-Sent Events (SSE) for real-time message streaming
   - Configure ChatKit for streaming responses

## References

- [OpenAI ChatKit Documentation](https://github.com/openai/chatkit-js)
- [ChatKit React Binding](https://github.com/openai/chatkit-js/tree/main/packages/react)
- [ChatKit Advanced Samples](https://github.com/openai/openai-chatkit-advanced-samples)
