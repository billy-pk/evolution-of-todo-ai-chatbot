<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.1
- Modified sections: Architecture Strategy > Technology Stack (Python 3.11+ → Python 3.13)
- Principles: No changes
- Templates status:
  ✅ plan-template.md: No update required
  ✅ spec-template.md: No update required
  ✅ tasks-template.md: No update required
  ⚠ commands/*.md: No command files found to update
- Ratification date: 2025-12-10 (unchanged)
- Last amended: 2025-12-10 (Python version clarification)
-->

# Evolution of Todo - Phase 3: AI-Powered Chatbot Constitution

## Core Principles

### I. Backwards Compatibility (NON-NEGOTIABLE)

**Rule**: Phase 3 MUST NOT break any functionality from Phase 2.

- All REST API endpoints from Phase 2 MUST remain unchanged and functional
- The tasks table schema MUST remain intact with no breaking migrations
- Better Auth with JWT MUST remain the authentication system
- Task CRUD UI MUST NOT be modified or removed
- All Phase 2 code MUST continue running without regression

**Rationale**: Phase 3 is an extension layer, not a replacement. Users rely on existing functionality, and breaking changes would violate trust and deployment stability.

### II. Stateless Server Design (NON-NEGOTIABLE)

**Rule**: All chat endpoints MUST be fully stateless.

- No in-memory session storage allowed
- Context MUST be reconstructed from the database on every request
- Each request MUST be independently processable with JWT and conversation ID

**Rationale**: Stateless design enables horizontal scaling, simplifies debugging, and prepares the system for Phase 4 (Kubernetes) and Phase 5 (Cloud-native scaling).

### III. Security First

**Rule**: User isolation and authentication MUST be enforced at every boundary.

- All chat requests MUST include JWT: `Authorization: Bearer <token>`
- User isolation MUST be enforced for:
  - Tasks (inherited from Phase 2)
  - Conversations (new in Phase 3)
  - Messages (new in Phase 3)
- MCP tools MUST verify task ownership using `user_id` before any operation
- No hard-coded secrets or tokens allowed; use environment variables

**Rationale**: Multi-user systems require strict isolation to prevent data leaks. JWT provides standardized, stateless authentication that scales.

### IV. Single Source of Truth

**Rule**: Both UI and Chat interfaces MUST operate on the same data.

- Tasks created via Chat MUST appear in Phase 2 UI
- Tasks created via UI MUST appear in Chat
- Both systems MUST use the same `tasks` table in the database
- No data duplication or synchronization logic allowed

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

### Technology Stack (Inherited from Phase 2)

- **Frontend**: Next.js App Router, TailwindCSS, React
- **Backend**: FastAPI, Python 3.13
- **Database**: SQLModel + Neon PostgreSQL
- **Authentication**: Better Auth with JWT

### New Components (Phase 3)

- **Chat UI**: OpenAI ChatKit
- **AI Agent**: OpenAI Agents SDK
- **Tool Layer**: MCP (Model Context Protocol) tools
- **Persistence**: SQLModel tables for conversations and messages

### System Boundaries

- Frontend communicates with Backend via REST API
- Backend enforces authentication via JWT validation
- MCP tools operate on database with user_id isolation
- AI Agent calls MCP tools via standardized protocol

## Development Workflow

### Feature Development Process

1. **Specification**: Create or update feature spec in `specs/<feature>/spec.md`
2. **Planning**: Generate implementation plan in `specs/<feature>/plan.md`
3. **Tasks**: Generate task list in `specs/<feature>/tasks.md`
4. **Implementation**: Follow Red-Green-Refactor cycle
5. **Validation**: Run tests, verify acceptance criteria
6. **Integration**: Ensure Phase 2 functionality remains intact

### Quality Gates

- All PRs MUST pass linting and type checking
- All tests MUST pass before merge
- No decrease in test coverage
- Manual verification that Phase 2 UI still works

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

**Version**: 1.0.1 | **Ratified**: 2025-12-10 | **Last Amended**: 2025-12-10

**Change Log**:
- **1.0.1** (2025-12-10): Clarified Python version requirement (3.11+ → 3.13)
- **1.0.0** (2025-12-10): Initial constitution for Phase 3 based on CONSTITUTION.md requirements
