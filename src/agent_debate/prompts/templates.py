"""Minimal prompt renderer (Phase 6.4).

Replaces simple ``{placeholder}`` tokens (a single word in braces) with provided
values. There is NO external template engine, NO eval, and NO code execution. If the
template contains a ``{placeholder}`` with no provided value, PromptError is raised so
the caller fails clearly. Braces that are not a bare ``{word}`` (e.g. JSON like
``{"k": 1}``) are left untouched.
"""

from __future__ import annotations

import re

from agent_debate.prompts.loader import PromptError

_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def render(template: str, /, **values: str) -> str:
    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise PromptError(f"missing value for placeholder '{key}'")
        return str(values[key])

    return _PLACEHOLDER.sub(_replace, template)
