# Tasks: AI-Powered Chatbot

**Input**: Design documents from `/specs/001-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Following TDD (Test-Driven Development) discipline - tests are written FIRST before implementation per Constitution Principle V.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

## Path Conventions

This is a **web application** with:
- Backend: `backend/` (Python/FastAPI)
- Frontend: `frontend/` (Next.js/React)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment setup and dependency installation

- [ ] T001 Add OPENAI_API_KEY and related config to backend/.env per quickstart.md
- [ ] T002 [P] Install OpenAI SDK in backend: `uv pip install openai`
- [ ] T003 [P] Install MCP SDK in backend: `uv pip install mcp`
- [ ] T004 [P] Install OpenAI ChatKit in frontend: `npm install @openai/chatkit`
- [ ] T005 Update backend/config.py to add OPENAI_API_KEY, OPENAI_MODEL, OPENAI_API_TIMEOUT, RATE_LIMIT_REQUESTS_PER_HOUR settings

**Checkpoint**: Dependencies installed, environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Add Conversation model to backend/models.py per data-model.md (lines 115-123)
- [ ] T007 Add Message model to backend/models.py per data-model.md (lines 177-193)
- [ ] T008 Create database migration script backend/scripts/migrate_conversations.py per data-model.md (lines 256-274)
- [ ] T009 Run migration to create conversations and messages tables
- [ ] T010 Verify tables created with test connection script per quickstart.md
- [ ] T011 Add ChatRequest schema to backend/schemas.py (message: str, conversation_id: Optional[UUID])
- [ ] T012 Add ChatResponse schema to backend/schemas.py (conversation_id: UUID, response: str, tool_calls: List, messages: List, metadata: dict)

**Checkpoint**: Foundation ready - database tables exist, schemas defined, user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks via natural language chat commands

**Independent Test**: Authenticate user, open /chat, type "add a task to buy groceries", verify task appears in chat response and task list UI

**Success Criteria**: FR-012, FR-013, FR-014, FR-015, FR-016, FR-021, SC-001, SC-003

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **CRITICAL**: Write these tests FIRST, ensure they FAIL, then implement to make them PASS

- [ ] T013 [P] [US1] Write unit test for add_task MCP tool in backend/tests/test_mcp_tools.py::test_add_task_creates_task
- [ ] T014 [P] [US1] Write unit test for add_task with description in backend/tests/test_mcp_tools.py::test_add_task_with_description
- [ ] T015 [P] [US1] Write unit test for add_task validation errors in backend/tests/test_mcp_tools.py::test_add_task_validation_errors
- [ ] T016 [P] [US1] Run pytest - confirm T013-T015 FAIL (Red phase)

### Implementation for User Story 1

- [ ] T017 [P] [US1] Create backend/mcp/__init__.py (empty init file)
- [ ] T018 [US1] Create AddTaskParams Pydantic schema in backend/mcp/tools.py per contracts/mcp-tools.md (lines 56-60)
- [ ] T019 [US1] Implement add_task_handler function in backend/mcp/tools.py per contracts/mcp-tools.md implementation pattern
- [ ] T020 [US1] Create add_task_tool definition in backend/mcp/tools.py per contracts/mcp-tools.md (lines 66-72)
- [ ] T021 [US1] Run pytest backend/tests/test_mcp_tools.py::test_add_task* - confirm tests PASS (Green phase)
- [ ] T022 [P] [US1] Create backend/mcp/server.py and register add_task_tool per contracts/mcp-tools.md (lines 548-560)
- [ ] T023 [P] [US1] Create backend/services/agent.py with OpenAI Agent initialization per research.md Agent Integration pattern
- [ ] T024 [US1] Configure agent with add_task_tool in backend/services/agent.py

**Checkpoint**: add_task MCP tool implemented and tested (US1 core functionality ready)

---

## Phase 4: User Story 2 - Task Listing and Retrieval (Priority: P1)

**Goal**: Enable users to list tasks via chat with status filtering

**Independent Test**: Create 3 tasks (2 pending, 1 completed) via UI, ask chatbot "show me my pending tasks", verify returns 2 tasks

**Success Criteria**: FR-012, FR-013, FR-014, FR-015, FR-022, SC-002, SC-003

### Tests for User Story 2 (TDD - Write FIRST) ⚠️

- [ ] T025 [P] [US2] Write unit test for list_tasks MCP tool in backend/tests/test_mcp_tools.py::test_list_tasks_all
- [ ] T026 [P] [US2] Write unit test for list_tasks with pending filter in backend/tests/test_mcp_tools.py::test_list_tasks_pending
- [ ] T027 [P] [US2] Write unit test for list_tasks with completed filter in backend/tests/test_mcp_tools.py::test_list_tasks_completed
- [ ] T028 [P] [US2] Write unit test for list_tasks user isolation in backend/tests/test_mcp_tools.py::test_list_tasks_filters_by_user
- [ ] T029 [P] [US2] Run pytest - confirm T025-T028 FAIL (Red phase)

### Implementation for User Story 2

- [ ] T030 [US2] Create ListTasksParams Pydantic schema in backend/mcp/tools.py per contracts/mcp-tools.md (lines 136-145)
- [ ] T031 [US2] Implement list_tasks_handler function in backend/mcp/tools.py per contracts/mcp-tools.md implementation pattern (lines 173-198)
- [ ] T032 [US2] Create list_tasks_tool definition in backend/mcp/tools.py
- [ ] T033 [US2] Register list_tasks_tool in backend/mcp/server.py
- [ ] T034 [US2] Add list_tasks_tool to agent configuration in backend/services/agent.py
- [ ] T035 [US2] Run pytest backend/tests/test_mcp_tools.py::test_list_tasks* - confirm tests PASS (Green phase)

**Checkpoint**: list_tasks MCP tool implemented and tested (US2 core functionality ready)

---

## Phase 5: User Story 6 - Conversation History Persistence (Priority: P2)

**Goal**: Persist and restore conversation history across sessions

**Independent Test**: Have 5-message conversation, close browser, reopen /chat, verify history displayed

**Success Criteria**: FR-026, FR-027, FR-028, FR-029, FR-030, FR-047, SC-004

**Note**: Implementing US6 before US3-US5 because chat endpoint infrastructure is needed for all remaining stories

### Tests for User Story 6 (TDD - Write FIRST) ⚠️

- [ ] T036 [P] [US6] Write integration test for chat endpoint creates conversation in backend/tests/test_chat_endpoint.py::test_chat_creates_conversation
- [ ] T037 [P] [US6] Write integration test for chat endpoint loads history in backend/tests/test_chat_endpoint.py::test_chat_loads_conversation_history
- [ ] T038 [P] [US6] Write integration test for chat endpoint requires JWT in backend/tests/test_chat_endpoint.py::test_chat_requires_jwt
- [ ] T039 [P] [US6] Write integration test for chat endpoint user isolation in backend/tests/test_chat_endpoint.py::test_chat_conversation_ownership
- [ ] T040 [P] [US6] Run pytest - confirm T036-T039 FAIL (Red phase)

### Implementation for User Story 6

- [ ] T041 [US6] Create backend/routes/chat.py file
- [ ] T042 [US6] Implement POST /api/{user_id}/chat endpoint skeleton in backend/routes/chat.py per contracts/chat-endpoint.md
- [ ] T043 [US6] Implement JWT validation in chat endpoint (extract user_id, verify match)
- [ ] T044 [US6] Implement conversation creation logic (if conversation_id not provided) in chat endpoint
- [ ] T045 [US6] Implement conversation loading logic (if conversation_id provided) in chat endpoint
- [ ] T046 [US6] Implement message history loading (last 100 messages) in chat endpoint per contracts/chat-endpoint.md (line 261)
- [ ] T047 [US6] Implement agent call with conversation context in chat endpoint per research.md
- [ ] T048 [US6] Implement message persistence (user + assistant messages) in atomic transaction in chat endpoint
- [ ] T049 [US6] Implement conversation updated_at timestamp update in chat endpoint
- [ ] T050 [US6] Add chat route to backend/main.py with JWTBearer dependency
- [ ] T051 [US6] Run pytest backend/tests/test_chat_endpoint.py - confirm tests PASS (Green phase)

**Checkpoint**: Chat endpoint functional with conversation persistence (US6 complete)

---

## Phase 6: User Story 3 - Task Completion via Chat (Priority: P2)

**Goal**: Enable users to mark tasks complete via chat commands

**Independent Test**: Create task "Write report", tell chatbot "mark 'Write report' as complete", verify status changes in chat and UI

**Success Criteria**: FR-012, FR-013, FR-014, FR-015, FR-016, FR-024

### Tests for User Story 3 (TDD - Write FIRST) ⚠️

- [ ] T052 [P] [US3] Write unit test for complete_task MCP tool in backend/tests/test_mcp_tools.py::test_complete_task_marks_complete
- [ ] T053 [P] [US3] Write unit test for complete_task idempotency in backend/tests/test_mcp_tools.py::test_complete_task_idempotent
- [ ] T054 [P] [US3] Write unit test for complete_task ownership in backend/tests/test_mcp_tools.py::test_complete_task_unauthorized
- [ ] T055 [P] [US3] Run pytest - confirm T052-T054 FAIL (Red phase)

### Implementation for User Story 3

- [ ] T056 [US3] Create CompleteTaskParams Pydantic schema in backend/mcp/tools.py per contracts/mcp-tools.md
- [ ] T057 [US3] Implement complete_task_handler function in backend/mcp/tools.py per contracts/mcp-tools.md implementation pattern (lines 349-376)
- [ ] T058 [US3] Create complete_task_tool definition in backend/mcp/tools.py
- [ ] T059 [US3] Register complete_task_tool in backend/mcp/server.py
- [ ] T060 [US3] Add complete_task_tool to agent configuration in backend/services/agent.py
- [ ] T061 [US3] Run pytest backend/tests/test_mcp_tools.py::test_complete_task* - confirm tests PASS (Green phase)

**Checkpoint**: complete_task MCP tool implemented and tested (US3 complete)

---

## Phase 7: User Story 4 - Task Updates and Modifications (Priority: P2)

**Goal**: Enable users to update task titles/descriptions via chat

**Independent Test**: Create task "Call mom", say "update 'Call mom' to 'Call mom about birthday'", verify change persists

**Success Criteria**: FR-012, FR-013, FR-014, FR-015, FR-016, FR-023

### Tests for User Story 4 (TDD - Write FIRST) ⚠️

- [ ] T062 [P] [US4] Write unit test for update_task title in backend/tests/test_mcp_tools.py::test_update_task_title
- [ ] T063 [P] [US4] Write unit test for update_task description in backend/tests/test_mcp_tools.py::test_update_task_description
- [ ] T064 [P] [US4] Write unit test for update_task both fields in backend/tests/test_mcp_tools.py::test_update_task_both
- [ ] T065 [P] [US4] Write unit test for update_task ownership in backend/tests/test_mcp_tools.py::test_update_task_unauthorized
- [ ] T066 [P] [US4] Run pytest - confirm T062-T065 FAIL (Red phase)

### Implementation for User Story 4

- [ ] T067 [US4] Create UpdateTaskParams Pydantic schema in backend/mcp/tools.py per contracts/mcp-tools.md (lines 240-251)
- [ ] T068 [US4] Implement update_task_handler function in backend/mcp/tools.py per contracts/mcp-tools.md implementation pattern (lines 283-315)
- [ ] T069 [US4] Create update_task_tool definition in backend/mcp/tools.py
- [ ] T070 [US4] Register update_task_tool in backend/mcp/server.py
- [ ] T071 [US4] Add update_task_tool to agent configuration in backend/services/agent.py
- [ ] T072 [US4] Run pytest backend/tests/test_mcp_tools.py::test_update_task* - confirm tests PASS (Green phase)

**Checkpoint**: update_task MCP tool implemented and tested (US4 complete)

---

## Phase 8: User Story 5 - Task Deletion via Chat (Priority: P3)

**Goal**: Enable users to delete tasks via chat commands

**Independent Test**: Create task "Test task", say "delete 'Test task'", verify removed from both interfaces

**Success Criteria**: FR-012, FR-013, FR-014, FR-015, FR-016, FR-025

### Tests for User Story 5 (TDD - Write FIRST) ⚠️

- [ ] T073 [P] [US5] Write unit test for delete_task removes task in backend/tests/test_mcp_tools.py::test_delete_task_removes
- [ ] T074 [P] [US5] Write unit test for delete_task ownership in backend/tests/test_mcp_tools.py::test_delete_task_unauthorized
- [ ] T075 [P] [US5] Write unit test for delete_task not found in backend/tests/test_mcp_tools.py::test_delete_task_not_found
- [ ] T076 [P] [US5] Run pytest - confirm T073-T075 FAIL (Red phase)

### Implementation for User Story 5

- [ ] T077 [US5] Create DeleteTaskParams Pydantic schema in backend/mcp/tools.py per contracts/mcp-tools.md
- [ ] T078 [US5] Implement delete_task_handler function in backend/mcp/tools.py per contracts/mcp-tools.md implementation pattern (lines 456-479)
- [ ] T079 [US5] Create delete_task_tool definition in backend/mcp/tools.py
- [ ] T080 [US5] Register delete_task_tool in backend/mcp/server.py
- [ ] T081 [US5] Add delete_task_tool to agent configuration in backend/services/agent.py
- [ ] T082 [US5] Run pytest backend/tests/test_mcp_tools.py::test_delete_task* - confirm tests PASS (Green phase)

**Checkpoint**: delete_task MCP tool implemented and tested (US5 complete, all 5 MCP tools functional)

---

## Phase 9: Frontend Chat UI (All User Stories)

**Purpose**: Build chat interface that serves all user stories (US1-US6)

**Success Criteria**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-048

### Tests for Frontend (TDD - Write FIRST) ⚠️

- [ ] T083 [P] Write frontend test for chat page renders in frontend/__tests__/chat/chat-page.test.tsx
- [ ] T084 [P] Write frontend test for message send in frontend/__tests__/chat/chat-flow.test.tsx::test_user_can_send_message
- [ ] T085 [P] Write frontend test for loading indicator in frontend/__tests__/chat/chat-flow.test.tsx::test_shows_loading_indicator
- [ ] T086 [P] Run npm test - confirm T083-T085 FAIL (Red phase)

### Frontend Implementation

- [ ] T087 [P] Create frontend/src/app/chat/page.tsx with ChatKit UI skeleton per research.md ChatKit integration pattern
- [ ] T088 [P] Add chat API client function to frontend/src/lib/api.ts (POST /api/{user_id}/chat with JWT header)
- [ ] T089 Update frontend/src/app/layout.tsx to add "Chat" navigation link
- [ ] T090 Implement message input and send functionality in frontend/src/app/chat/page.tsx
- [ ] T091 Implement message history display (user right-aligned, assistant left-aligned) in frontend/src/app/chat/page.tsx per FR-006
- [ ] T092 Implement loading indicator with "thinking" status in frontend/src/app/chat/page.tsx per FR-048
- [ ] T093 Implement "New Conversation" button in frontend/src/app/chat/page.tsx per FR-005
- [ ] T094 Add error handling for 401/403/404/429/500 responses in frontend/src/app/chat/page.tsx per FR-045
- [ ] T095 Run npm test frontend/__tests__/chat/ - confirm tests PASS (Green phase)

**Checkpoint**: Chat UI complete and functional

---

## Phase 10: Integration & End-to-End Testing

**Purpose**: Verify all user stories work together and independently

- [ ] T096 [P] Write E2E test for US1 (create task via chat) in backend/tests/test_integration.py::test_e2e_create_task_via_chat
- [ ] T097 [P] Write E2E test for US2 (list tasks via chat) in backend/tests/test_integration.py::test_e2e_list_tasks_via_chat
- [ ] T098 [P] Write E2E test for US3 (complete task via chat) in backend/tests/test_integration.py::test_e2e_complete_task_via_chat
- [ ] T099 [P] Write E2E test for US4 (update task via chat) in backend/tests/test_integration.py::test_e2e_update_task_via_chat
- [ ] T100 [P] Write E2E test for US5 (delete task via chat) in backend/tests/test_integration.py::test_e2e_delete_task_via_chat
- [ ] T101 [P] Write E2E test for US6 (conversation persistence) in backend/tests/test_integration.py::test_e2e_conversation_persistence
- [ ] T102 Write E2E test for Phase 2 compatibility (task created in UI visible in chat) in backend/tests/test_integration.py::test_phase2_compatibility
- [ ] T103 Run all integration tests - pytest backend/tests/test_integration.py -v
- [ ] T104 Run all backend unit tests - pytest backend/tests/ -v
- [ ] T105 Run all frontend tests - npm test frontend/__tests__/
- [ ] T106 Manual QA: Verify all acceptance scenarios from spec.md (US1-US6)

**Checkpoint**: All tests passing, all user stories verified

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Performance, security, documentation

- [ ] T107 Implement rate limiting (100 req/hour per user) in backend/routes/chat.py per research.md rate limiting pattern
- [ ] T108 [P] Add request logging with user_id, conversation_id, tool_calls in backend/routes/chat.py
- [ ] T109 [P] Add performance monitoring (response time tracking) in backend/routes/chat.py
- [ ] T110 [P] Update .env.example with all required Phase 3 environment variables per quickstart.md
- [ ] T111 [P] Verify Phase 2 tests still pass - run existing Phase 2 test suite to confirm no regressions (SC-008)
- [ ] T112 Load test chat endpoint with 50 concurrent users per SC-009 using locust or similar
- [ ] T113 [P] Add inline documentation for all MCP tools in backend/mcp/tools.py
- [ ] T114 [P] Add inline documentation for agent service in backend/services/agent.py
- [ ] T115 [P] Add inline documentation for chat endpoint in backend/routes/chat.py

**Final Checkpoint**: Feature complete, tested, documented, ready for deployment

---

## Dependencies & Execution Strategy

### User Story Dependency Graph

```
Phase 1: Setup (T001-T005)
    ↓
Phase 2: Foundational (T006-T012) ← BLOCKING - must complete before user stories
    ↓
    ├─→ Phase 3: US1 - Task Creation (T013-T024) 🎯 MVP - can run in parallel
    ├─→ Phase 4: US2 - Task Listing (T025-T035) - can run in parallel with US1
    └─→ Phase 5: US6 - Conversation History (T036-T051) - REQUIRED before US3-US5
            ↓
            ├─→ Phase 6: US3 - Task Completion (T052-T061) - can run in parallel
            ├─→ Phase 7: US4 - Task Updates (T062-T072) - can run in parallel
            └─→ Phase 8: US5 - Task Deletion (T073-T082) - can run in parallel
                    ↓
                Phase 9: Frontend UI (T083-T095) - requires chat endpoint from US6
                    ↓
                Phase 10: Integration Testing (T096-T106)
                    ↓
                Phase 11: Polish (T107-T115)
```

### Parallel Execution Opportunities

**After Phase 2 completes, these can run in parallel**:
- US1 (T013-T024) + US2 (T025-T035) - independent MCP tools

**After US6 completes, these can run in parallel**:
- US3 (T052-T061) + US4 (T062-T072) + US5 (T073-T082) - independent MCP tools

**Within each phase**:
- All [P] marked tasks can run in parallel (different files)
- Test writing tasks (T013-T016, T025-T029, etc.) can all run in parallel

### MVP Scope Recommendation

**Minimum Viable Product** (ready to demo):
- Phase 1: Setup (T001-T005)
- Phase 2: Foundational (T006-T012)
- Phase 3: US1 - Task Creation (T013-T024)
- Phase 5: US6 - Conversation History (T036-T051, skipping T036-T040 tests if time-constrained)
- Phase 9: Frontend UI (T087-T095, minimal implementation)

This MVP delivers:
✅ Chat interface
✅ Natural language task creation
✅ Conversation persistence
✅ Integration with Phase 2 task list

**Total**: ~40 tasks for MVP, ~115 tasks for complete feature

---

## Implementation Strategy

1. **Sequential Phases**: Complete Setup → Foundational before ANY user story work
2. **TDD Discipline**: ALWAYS write tests first (Red), implement (Green), refactor
3. **Independent Stories**: Each user story (US1-US6) can be delivered as an increment
4. **Parallel Execution**: Use [P] markers to identify parallelizable tasks
5. **Checkpoints**: Verify each phase checkpoint before moving to next phase
6. **Phase 2 Compatibility**: Run Phase 2 tests after each phase to catch regressions early

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] All 6 user stories have passing acceptance scenarios (spec.md lines 29-112)
- [ ] All 10 success criteria met (spec.md lines 218-227)
- [ ] All 45 functional requirements satisfied (spec.md lines 135-204)
- [ ] Phase 2 compatibility verified (FR-036 through FR-040)
- [ ] All TDD tests written first and passing (Constitution Principle V)
- [ ] Test coverage >90% for MCP tools and agent service
- [ ] Performance goals met (chat endpoint <3s p95, 50 concurrent users)
- [ ] Security verified (user isolation, JWT auth, ownership checks)
- [ ] Documentation complete (inline docs, .env.example updated)

---

**Total Tasks**: 115 tasks
**MVP Tasks**: ~40 tasks (Phases 1, 2, 3, 5 minimal, 9 minimal)
**Estimated Parallel Opportunities**: ~60 tasks marked [P]
**User Stories**: 6 stories (US1-US6) organized as independent, testable increments
