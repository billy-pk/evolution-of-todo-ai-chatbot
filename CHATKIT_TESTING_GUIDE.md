# ChatKit Integration Testing Guide

This guide provides step-by-step instructions to test the OpenAI ChatKit integration end-to-end.

## Prerequisites

Before testing, ensure you have:
1. Backend running on port 8000: `uvicorn main:app --reload`
2. MCP server running on port 8001: `cd tools && python server.py`
3. Frontend running on port 3000: `npm run dev`
4. A test user account (sign up in the app)
5. Valid `.env` files with:
   - `DATABASE_URL` (PostgreSQL)
   - `OPENAI_API_KEY`
   - `BETTER_AUTH_SECRET`
   - `BETTER_AUTH_JWKS_URL`

## Testing Workflow

### 1. Backend API Testing

#### Test Session Endpoint
```bash
# First, get a valid JWT token from the frontend or create one for testing

# Create a session
curl -X POST http://localhost:8000/api/chatkit/session \
  -H "Authorization: Bearer {your_jwt_token}" \
  -H "Content-Type: application/json"

# Expected response:
{
  "client_secret": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "user_uuid"
}
```

#### Verify Token Format
```bash
# Decode the client_secret JWT (use https://jwt.io or jq)
echo "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." | base64 -d | jq .

# Should contain:
# {
#   "user_id": "your_user_id",
#   "type": "chatkit_session",
#   "iat": 1704067200,
#   "exp": 1704069000
# }
```

#### Test Thread Creation
```bash
# Save the client_secret from previous step
CLIENT_SECRET="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# Create a new thread
curl -X POST http://localhost:8000/api/chatkit/threads \
  -H "Authorization: Bearer $CLIENT_SECRET" \
  -H "Content-Type: application/json"

# Expected response:
{
  "id": "thread_uuid",
  "created_at": "2024-01-01T00:00:00Z"
}

# Save thread_id for next tests
THREAD_ID="thread_uuid"
```

#### Test Listing Threads
```bash
curl -X GET http://localhost:8000/api/chatkit/threads \
  -H "Authorization: Bearer $CLIENT_SECRET"

# Expected response: list of threads with metadata
```

#### Test Getting Thread Details
```bash
curl -X GET http://localhost:8000/api/chatkit/threads/$THREAD_ID \
  -H "Authorization: Bearer $CLIENT_SECRET"

# Expected response: thread with messages array (empty for new thread)
```

#### Test Sending a Message
```bash
curl -X POST http://localhost:8000/api/chatkit/messages \
  -H "Authorization: Bearer $CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "'$THREAD_ID'",
    "message": "Create a task to buy groceries"
  }'

# Expected response:
{
  "message_id": "message_uuid",
  "response_id": "response_uuid",
  "response": "I've created a task 'buy groceries' for you.",
  "thread_id": "thread_uuid"
}
```

### 2. Frontend UI Testing

#### Test ChatKit Component Rendering
1. Open http://localhost:3000
2. Sign in with test account
3. Navigate to `/chat` route (or dashboard → chat)
4. **Expected:** ChatKit component renders with:
   - Blue header with "AI Assistant" title
   - Empty message area with chat icon
   - Start screen with 3 suggested prompts:
     - "Create a task"
     - "List tasks"
     - "Get help"
   - Input composer at bottom with blue send button

#### Test Session Creation
1. Open browser DevTools (F12) → Console tab
2. Open `/chat` page
3. Check console logs for:
   ```
   "ChatKit is ready"
   (or similar initialization message)
   ```
4. No error messages should appear

#### Test Message Sending (Manual)
1. In ChatKit composer, type: `Create a task to buy milk`
2. Press Enter or click Send
3. **Expected:**
   - User message appears on right side (blue bubble)
   - Loading indicator appears on left (spinning loader)
   - After ~2-5 seconds: AI response appears (white bubble with assistant icon)
   - Response should reference the task creation

#### Test Conversation Persistence
1. Create a message and get response (from previous test)
2. Reload the page (F5)
3. **Expected:**
   - ChatKit component still shows conversation history
   - Both user message and assistant response are visible
   - Last thread ID is loaded from localStorage

#### Test Click Start Screen Prompts
1. Create new thread (should clear conversation)
2. Click "List tasks" prompt
3. **Expected:**
   - Prompt text is sent as message
   - Response shows list of tasks (or "no tasks yet")

#### Test Error Handling
1. Stop the backend server (Ctrl+C)
2. Try to send a message
3. **Expected:**
   - Error message displays in red alert box
   - Message: "Server error. Please try again later."
   - Dismissible error banner with close button

#### Test Token Refresh
1. Open `/chat` page
2. Wait 25+ minutes (or modify token expiry in chatkit.py for testing)
3. Try to send a message
4. **Expected:**
   - `getClientSecret(existing)` is called
   - `/api/chatkit/refresh` endpoint is hit
   - Message sends successfully with new token

### 3. Database Verification

#### Check Conversations Table
```sql
-- Connect to your PostgreSQL database
psql $DATABASE_URL

-- List all conversations for a user
SELECT id, user_id, created_at, updated_at
FROM conversation
WHERE user_id = 'your_user_id'
ORDER BY created_at DESC;

-- Should show conversation(s) created via ChatKit
```

#### Check Messages Table
```sql
-- List all messages in a conversation
SELECT id, conversation_id, role, content, created_at
FROM message
WHERE conversation_id = 'thread_uuid'
ORDER BY created_at ASC;

-- Should show alternating user/assistant messages
```

### 4. Multi-User Isolation Testing

#### Create Second Test User
1. Sign out from first account
2. Sign up with different email
3. Navigate to `/chat`
4. Send a message: `Create a task for user 2`

#### Verify Isolation
```sql
-- Check that each user only sees their own conversations
SELECT user_id, COUNT(*) as conversation_count
FROM conversation
GROUP BY user_id;

-- Should show 2 different user_ids with their own conversations
```

### 5. AI Integration Testing

#### Test Task Creation via Chat
1. Send message: `Create a task to call mom at 3pm`
2. **Expected:** AI response: "I've created a task 'call mom at 3pm'"
3. Verify in tasks page: new task should appear

#### Test Task Listing via Chat
1. Send message: `What are my tasks?` or click "List tasks" prompt
2. **Expected:** AI response shows list of tasks
3. Verify response matches tasks page

#### Test Tool Calls
1. Open DevTools → Network tab
2. Send message that triggers MCP tools
3. **Expected:**
   - POST to `/api/{user_id}/chat` endpoint
   - MCP server processes tool calls
   - Response includes task modifications

### 6. Error Scenarios

#### Test Missing JWT
```bash
# Try to create session without JWT
curl -X POST http://localhost:8000/api/chatkit/session \
  -H "Content-Type: application/json"

# Expected: 401 "Missing or invalid Authorization header"
```

#### Test Invalid JWT
```bash
curl -X POST http://localhost:8000/api/chatkit/session \
  -H "Authorization: Bearer invalid_token" \
  -H "Content-Type: application/json"

# Expected: 401 "Invalid token"
```

#### Test Missing Thread ID in Message
```bash
CLIENT_SECRET="..."
curl -X POST http://localhost:8000/api/chatkit/messages \
  -H "Authorization: Bearer $CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello without thread"}'

# Expected: 400 "Missing thread_id or message"
```

#### Test Non-Existent Thread
```bash
curl -X POST http://localhost:8000/api/chatkit/messages \
  -H "Authorization: Bearer $CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "nonexistent_uuid",
    "message": "Test message"
  }'

# Expected: 404 "Thread not found"
```

## Troubleshooting

### ChatKit Component Not Rendering
**Symptom:** Empty chat page or white screen
**Solution:**
1. Check browser console for JavaScript errors
2. Verify `@openai/chatkit-react` is installed: `npm list @openai/chatkit-react`
3. Rebuild frontend: `npm run build`

### Session Creation Fails
**Symptom:** "Failed to create chat session" error
**Solution:**
1. Verify JWT token is valid: decode at jwt.io
2. Check backend logs for validation errors
3. Verify `BETTER_AUTH_SECRET` matches frontend configuration
4. Ensure backend is running on port 8000

### Messages Not Persisting
**Symptom:** Conversation disappears after reload
**Solution:**
1. Check PostgreSQL connection: run `/health` endpoint
2. Verify `DATABASE_URL` is correct
3. Check migrations have run: `conversation` and `message` tables should exist
4. Check browser localStorage is enabled

### AI Not Responding
**Symptom:** Message sent but no response appears
**Solution:**
1. Verify MCP server is running on port 8001
2. Verify `OPENAI_API_KEY` is set in backend `.env`
3. Check backend logs for agent processing errors
4. Test with simple message like "Hello"

### Token Refresh Not Working
**Symptom:** "Invalid token" error after 30 minutes
**Solution:**
1. Verify token expiry in `chatkit.py` (should be 30 minutes)
2. Check `/api/chatkit/refresh` endpoint accepts expired tokens
3. Restart frontend to clear any cached tokens

## Performance Considerations

### Message Processing Time
- First message: 3-5 seconds (includes AI processing)
- Subsequent messages: 2-4 seconds (shorter context)
- Tool calls: +1-2 seconds (MCP processing)

### Database Queries
- Each message triggers ~5 database operations:
  1. Load conversation
  2. Load message history
  3. Save user message
  4. Save assistant response
  5. Update conversation timestamp

### Optimization Tips
1. Implement message pagination (currently loads all messages)
2. Cache conversation history (currently loads every time)
3. Add message compression (store large responses separately)
4. Implement async processing (return response ID before full processing)

## Success Criteria

All tests pass when:
- ✅ Backend starts without errors
- ✅ ChatKit session endpoint returns valid JWT
- ✅ Frontend authenticates and renders ChatKit component
- ✅ Messages can be sent and responses received
- ✅ Conversations persist across page reloads
- ✅ AI correctly processes task-related requests
- ✅ Multi-user isolation works (users see only their data)
- ✅ Error messages display correctly
- ✅ Token refresh works when expired

## Debugging Tips

### Enable Verbose Logging
```python
# In backend main.py, set logging level
logging.basicConfig(level=logging.DEBUG)
```

### Monitor API Calls
1. Open DevTools → Network tab
2. Filter by XHR/Fetch
3. Watch requests to `/api/chatkit/*` endpoints

### Check Token Contents
```javascript
// In browser console
const token = "your_client_secret";
const parts = token.split('.');
const payload = JSON.parse(atob(parts[1]));
console.log(payload);
```

### Database Logging
```sql
-- Enable query logging in PostgreSQL
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();
```
