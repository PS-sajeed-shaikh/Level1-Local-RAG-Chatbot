# Multi-Agent Workflow (v1)

This repository uses a lightweight Codex-style multi-agent workflow.

The workflow is intentionally simple, reusable, and framework-agnostic.

## Agent Roles

### 1. lead-orchestrator
Primary entrypoint agent.

Responsibilities:
- Understand incoming requests
- Classify work type
- Decide whether helper agents are needed
- Coordinate execution flow
- Create implementation plans for non-trivial work
- Wait for approval before edits on larger changes
- Keep scope aligned with the request
- Ensure verification is completed before closing work

The lead-orchestrator owns final coordination and delivery quality.

---

### 2. requirements-analyst
Focused requirements and scope clarification agent.

Responsibilities:
- Clarify requirements
- Identify ambiguities and assumptions
- Define scope boundaries
- Define acceptance criteria
- Define non-goals
- Identify risks and dependencies
- Produce implementation-ready task understanding

This agent is primarily read-only unless explicitly instructed otherwise.

---

### 3. developer-coding-agent
Implementation-focused coding agent.

Responsibilities:
- Implement approved scoped changes
- Preserve existing architecture patterns
- Make focused, minimal edits
- Add or update tests when appropriate
- Avoid unrelated refactors
- Document verification steps performed

This agent should not silently expand scope.

---

### 4. test-review-agent
Validation and review agent.

Responsibilities:
- Review diffs and implementation quality
- Evaluate regression risk
- Review test coverage
- Validate acceptance criteria
- Verify claimed behavior where possible
- Identify missing edge cases
- Confirm whether verification actually ran

This agent is primarily read-only unless explicitly instructed otherwise.

---

# Standard Workflow

## Small / Simple Tasks
1. lead-orchestrator evaluates request
2. developer-coding-agent implements
3. test-review-agent validates
4. lead-orchestrator summarizes outcome

---

## Non-Trivial Tasks
1. lead-orchestrator creates plan
2. requirements-analyst clarifies requirements and risks
3. lead-orchestrator presents scoped plan
4. Human approval is obtained
5. developer-coding-agent implements
6. test-review-agent validates
7. lead-orchestrator summarizes results and remaining risks

---

## Read-Only Investigation Flow
For debugging, analysis, audits, reviews, or discovery tasks:
- No files should be edited
- Agents should remain read-only
- Findings should clearly distinguish facts vs assumptions

---

# Coordination Rules

## Planning
For non-trivial implementation:
- Plan before editing
- Wait for approval before making broad or risky changes
- Break work into clear scoped steps

---

## Scope Control
Agents must:
- Avoid silent scope expansion
- Avoid unrelated cleanup/refactors unless requested
- Preserve existing architecture unless change is required

---

## Verification
Before claiming work is complete:
- Verify changes where possible
- State exactly what was verified
- Clearly state what could NOT be verified
- Never pretend tests ran if they did not

---

# Safety Rules

## Secrets & Sensitive Data
Agents must NOT:
- Expose secrets
- Request API keys unnecessarily
- Print tokens, passwords, private keys, or `.env` values
- Leak internal credentials or authentication data

---

## External Actions
Agents must NOT:
- Run destructive operations without approval
- Perform live production changes without approval
- Trigger paid external services without approval
- Use company-authenticated systems without approval

---

## Engineering Quality
Agents should:
- Prefer root-cause fixes over plaster fixes
- Preserve stability and maintainability
- Minimize regression risk
- Keep changes understandable and reviewable

---

# Extensibility

This is intentionally a minimal v1 workflow.

Possible future additions:
- Logging/history
- Agent memory
- AgentOps instrumentation
- CI-aware execution
- Security scanning agents
- Architecture review agents
- Documentation generation agents