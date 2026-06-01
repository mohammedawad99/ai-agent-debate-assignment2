"""Prompts layer (Phase 6.4).

Project-local prompt templates live under the repository `prompts/` directory and are
loaded via `loader.load_prompt` and filled via `templates.render`. No global Claude
skills are used; no code execution / eval / network. See docs/PROMPTS.md.
"""
