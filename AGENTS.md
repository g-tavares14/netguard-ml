# AGENTS.md

Python 3.12+ project managed with uv.
Layout: src/ for code, tests/ for tests.
Zed is the editor: basedpyright + Ruff. Their diagnostics are the quality bar.

## Tooling — do not replace

| Job | Tool | Forbidden substitutes |
|---|---|---|
| Deps / venv / run | uv | pip, poetry, pipenv, conda, manual .venv activation |
| Lint + format | Ruff | black, isort, flake8, autopep8 |
| Types | basedpyright | mypy, unless this repo already has mypy |
| Tests | pytest | unittest as the default runner |

Never invent a requirements.txt if pyproject.toml + uv.lock exist.

## Commands

```bash
uv sync
uv add <package>
uv add --dev <package>
uv lock
uv run python -m <package>
uv run ruff check --fix <path>
uv run ruff format <path>
uv run basedpyright
uv run pytest tests/ -q
uv run pytest tests/<file>.py::<test_name> -q --tb=short
