<!--
Sync Impact Report:
- Version change: 1.0.1 → 2.0.0
- Modified principles:
  * Principle I: "Backwards Compatibility" → REMOVED (Phase 3 is standalone, not extending Phase 2)
  * Principle II: "Stateless Server Design" → UPDATED (expanded to cover MCP tools)
  * Principle IV: "Single Source of Truth" → UPDATED (removed UI references, chat-centric)
- Added sections:
  * New Components expanded with Official MCP SDK details
  * Conversational Interface principle
  * MCP Tools Statefulness requirement
- Removed sections:
  * All references to "Phase 2 REST API endpoints"
  * All references to "React UI components"
  * All references to "extending Phase 2"
  * "Frontend logic that handles task CRUD outside of the conversational agent"
- Templates requiring updates:
  ✅ plan-template.md: No update required (generic template)
  ✅ spec-template.md: No update required (generic template)
  ✅ tasks-template.md: No update required (generic template)
- Ratification date: 2025-12-10 (unchanged)
- Last amended: 2025-12-15 (Phase 3 architecture redefinition)
- Breaking changes: MAJOR version bump due to removal of backwards compatibility principle
-->

# Evolution of Todo - Phase 3: AI-Powered Chatbot Constitution

## Core Principles

### I. Conversational Interface Primary (NON-NEGOTIABLE)

**Rule**: All task management operations MUST be accessible through conversational interface.

- Users interact with tasks via natural language chat
- AI agent interprets user intent and executes operations
- No traditional UI forms or buttons for task CRUD
- Conversational interface is the primary interaction model

**Rationale**: Phase 3 shifts from traditional UI to conversational AI interface. This enables natural language task management and prepares the foundation for advanced AI-driven workflows.

### II. Stateless Server Design (NON-NEGOTIABLE)

**Rule**: All chat endpoints and MCP tools MUST be fully stateless.

- No in-memory session storage allowed
- Chat endpoint MUST reconstruct context from the database on every request
- MCP tools MUST be stateless and store all state in the database
- Each request MUST be independently processable with JWT and conversation ID

**Rationale**: Stateless design enables horizontal scaling, simplifies debugging, and prepares the system for Phase 4 (Kubernetes) and Phase 5 (Cloud-native scaling).

### III. Security First

**Rule**: User isolation and authentication MUST be enforced at every boundary.

- All chat requests MUST include JWT: `Authorization: Bearer <token>`
- User isolation MUST be enforced for:
  - Tasks
  - Conversations
  - Messages
- MCP tools MUST verify task ownership using `user_id` before any operation
- No hard-coded secrets or tokens allowed; use environment variables

**Rationale**: Multi-user systems require strict isolation to prevent data leaks. JWT provides standardized, stateless authentication that scales.

### IV. Single Source of Truth

**Rule**: All task data MUST reside in a single database with consistent access patterns.

- Tasks are stored in the `tasks` table
- Chat interface operates directly on the database via MCP tools
- No data duplication or synchronization logic allowed
- All operations (chat, API) query the same database

**Rationale**: Multiple data sources create inconsistency, confusion, and maintenance burden. A single source of truth ensures reliability.

### V. Test-Driven Development

**Rule**: Tests MUST be written before implementation for new functionality.

- Write tests for MCP tools before implementing them
- Write integration tests for chat endpoint before implementing it
- Tests MUST fail initially (Red phase)
- Implementation MUST make tests pass (Green phase)
- Refactor only after tests pass

**Rationale**: TDD ensures requirements are clear, code is testable, and regressions are caught early. It enforces discipline and quality.

### VI. Extensibility and Modularity

**Rule**: Architecture MUST support future phases without breaking changes.

- Components MUST be modular and independently deployable
- Frontend and backend boundaries MUST remain clean with well-defined APIs
- No architectural decisions that block Phase 4 (Kubernetes) or Phase 5 (Microservices)
- Configuration MUST be externalized (no hard-coded hostnames, ports, or secrets)

**Rationale**: The Evolution of Todo project is multi-phase. Each phase must build a solid foundation for the next without requiring rewrites.

## Architecture Strategy

### Technology Stack

- **Frontend**: Next.js App Router, TailwindCSS, React
- **Backend**: FastAPI, Python 3.13
- **Database**: SQLModel + Neon PostgreSQL
- **Authentication**: Better Auth with JWT

### New Components (Phase 3)

- **Chat UI**: OpenAI ChatKit (official React component)
- **AI Agent**: OpenAI Agents SDK (official SDK for agent logic)
- **Tool Layer**: MCP (Model Context Protocol) tools built with Official MCP SDK
- **MCP Server**: Stateless HTTP MCP server exposing task operations as tools
- **Persistence**: SQLModel tables for conversations and messages

### System Boundaries

- Frontend loads ChatKit component for conversational interface
- Frontend calls chat endpoint with user message and conversation ID
- Backend validates JWT and reconstructs conversation context from database
- Backend initializes OpenAI Agent with MCP tools
- Agent processes user message and calls MCP tools as needed
- MCP tools execute database operations with user isolation
- Chat endpoint persists conversation state to database
- Response streams back to frontend via ChatKit

### MCP Tools Architecture

**Stateless MCP Server** (built with Official MCP SDK):
- Exposes task operations as MCP tools (add_task, list_tasks, update_task, complete_task, delete_task)
- Each tool receives `user_id` parameter for user isolation
- Tools connect to PostgreSQL database via SQLModel
- No in-memory state; all state stored in database
- HTTP transport for stateless request/response

**Chat Endpoint** (stateless):
- Receives user message + conversation_id
- Loads conversation history from database
- Initializes OpenAI Agent with MCP server connection
- Agent uses MCP tools to manage tasks
- Saves new messages to database
- Returns assistant response

## Development Workflow

### Feature Development Process

1. **Specification**: Create or update feature spec in `specs/<feature>/spec.md`
2. **Planning**: Generate implementation plan in `specs/<feature>/plan.md`
3. **Tasks**: Generate task list in `specs/<feature>/tasks.md`
4. **Implementation**: Follow Red-Green-Refactor cycle
5. **Validation**: Run tests, verify acceptance criteria
6. **Integration**: Verify multi-server coordination (Frontend + Backend + MCP Server)

### Quality Gates

- All PRs MUST pass linting and type checking
- All tests MUST pass before merge
- No decrease in test coverage
- Manual verification that chat functionality works end-to-end
- Verify statelessness: restart servers and ensure functionality persists

### Documentation Requirements

- ADRs (Architecture Decision Records) MUST be created for significant decisions
- PHRs (Prompt History Records) MUST be created for AI-assisted development sessions
- API contracts MUST be documented in `specs/<feature>/contracts/`
- Database schema changes MUST be documented with migration scripts

## Governance

### Amendment Process

1. Propose changes via pull request to `.specify/memory/constitution.md`
2. Document rationale and impact in PR description
3. Update `CONSTITUTION_VERSION` following semantic versioning:
   - MAJOR: Backward incompatible governance/principle removals or redefinitions
   - MINOR: New principle/section added or materially expanded guidance
   - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
4. Update dependent templates and documentation
5. Obtain approval from project maintainers
6. Update `LAST_AMENDED_DATE` to date of merge

### Compliance

- All specifications MUST reference this constitution
- All implementations MUST be validated against these principles
- Use `/sp.analyze` to verify cross-artifact consistency
- Constitution supersedes conflicting guidance in other documents

### Version History

**Version**: 2.0.0 | **Ratified**: 2025-12-10 | **Last Amended**: 2025-12-15

**Change Log**:
- **2.0.0** (2025-12-15): MAJOR - Redefined Phase 3 as standalone conversational AI system
  - REMOVED: Backwards Compatibility principle (Phase 3 is not extending Phase 2)
  - REMOVED: All references to "Phase 2 REST API endpoints"
  - REMOVED: All references to "React UI components" and "task CRUD UI"
  - ADDED: Conversational Interface Primary principle
  - UPDATED: Stateless Server Design to cover MCP tools
  - UPDATED: Single Source of Truth to focus on database-centric design
  - UPDATED: Architecture Strategy to detail MCP tools and Official MCP SDK
  - UPDATED: New Components section with MCP Server details
- **1.0.1** (2025-12-10): Clarified Python version requirement (3.11+ → 3.13)
- **1.0.0** (2025-12-10): Initial constitution for Phase 3 based on CONSTITUTION.md requirements
