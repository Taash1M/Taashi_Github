# Coding Standards

These principles apply across Python-based data engineering codebases.

## General

- Prefer **small, composable functions** over large monoliths.
- Use **type hints** for all public functions.
- Write **docstrings** for modules, classes, and functions describing intent, not just mechanics.
- Avoid magic numbers and hard-coded paths; use **configuration**.

## Python Style

- Follow PEP8 for formatting.
- Use `logging` instead of `print` in production code.
- Structure projects with clear separation of concerns:
  - `src/` for application logic
  - `tests/` for tests
  - `config/` for configurations
  - `scripts/` for one-off utilities

## SQL Style

- Uppercase SQL keywords (SELECT, FROM, JOIN, WHERE).
- Use **CTEs** to improve readability of complex queries.
- Name columns and tables consistently: use `snake_case`.
- Avoid `SELECT *` in production code; list columns explicitly.
