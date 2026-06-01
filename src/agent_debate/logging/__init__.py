"""Logging layer.

Future home of LoggerFactory and structured/rotating handlers. Logs must never
contain secrets (ARCHITECTURE SR-2). No implementation yet (Phase 4 skeleton).

Note: this package is named `agent_debate.logging`; it does not shadow the stdlib
`logging` module (absolute imports resolve `import logging` to the stdlib).
"""
