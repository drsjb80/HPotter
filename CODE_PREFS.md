# Coding Preferences

This file records coding preferences, style choices, and project conventions.

## Memory & Context
- Proactively save project context, decisions, and non-obvious findings to memory at the end of significant conversations
- Save when: architectural decisions are made, unusual blockers are encountered, workarounds are discovered, or stakeholder constraints emerge

## Code Style

### Python
- Use `python3` as the default Python interpreter
- Lint with `ruff` (not flake8)
- No type hints

### General
- Keep functions small and focused on a single responsibility
- Use clear, concise logging messages
- Prefer yoda-style comparisons (e.g., `if 0 == x` not `if x == 0`)

### Comments & Documentation
- Write comments to explain **why**, not what. The code itself explains what it does.
- Add a comment only when:
  - The reasoning is non-obvious (hidden constraint, workaround, design decision)
  - Behavior would surprise a reader unfamiliar with the context
  - There's a subtle invariant or assumption
- Focus comments on design decisions, architectural choices, and the problem being solved
- Don't describe what the code does line-by-line—that's what readable code does

### Constructors & Mutation
- Avoid mutators/setters; use custom constructors instead
- Prefer cloning over mutation

### JavaScript
- Always use strict equality: `===` and `!==`

### CSS
- Prefer `rem`, `em`, and percentages for sizing (not pixels)
- Use named colors instead of hex values

## Resource Management & Cleanup

- Use `try/except/finally` for resources that must be cleaned up (sockets, containers, database connections)
- Use context managers (`with`) for files and temporary resources where practical
- Ensure all resources are explicitly closed even on error paths
- Database writes use a lock to prevent concurrency issues

## Error Handling

- Prefer explicit error handling over broad exception swallowing
- Log exceptions at the appropriate level (`debug`, `warning`, `error`)
- Always close resources in `finally` blocks—FD and container leaks are a recurring concern

## Threading

- Avoid busy-waiting; use blocking/event-driven approaches instead
- Use socket timeouts to poll shutdown flags (e.g., 5s timeout in accept loops)
- Use `threading.Event` for cross-thread signaling

## Testing

- Unit test coverage target: 90%
- AI should run unit and system tests, and create new tests when appropriate

## Git

- Create a git hook that prompts for permission on commits over 20K
