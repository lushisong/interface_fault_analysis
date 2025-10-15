# Repository Guidelines

## Project Structure & Module Organization
- Source lives in `src/` (`core/`, `models/`, `ui/`, `analysis/`, `utils/`, `templates/`). Entry point is `main.py` (PyQt5 GUI).
- Tests are under `tests/` (plus `tests/ui/`). Demos: `simple_demo.py` (quick run) and `create_drone_demo.py` (writes samples to `demo_projects/`).
- Assets and docs: `templates/`, `data/`, `doc/`. Keep generated logs (`app.log`, etc.) out of commits.

## Build, Test, and Development Commands
- Environment: `python -m venv .venv && .venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Unix).
- Install: `pip install -r requirements.txt`.
- Run GUI: `python main.py`. Run demo: `python simple_demo.py`. Generate sample project: `python create_drone_demo.py`.
- Tests: `pytest -q`; subset `pytest -k "module_panel" -q`; marker `pytest -m diamante -q` (see `pytest.ini`). For headless runs set `QT_QPA_PLATFORM=offscreen`.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation. Prefer type hints and module-level docstrings.
- Naming: classes `PascalCase`, functions/variables/modules `snake_case`, tests `tests/test_*.py`.
- Keep UI logic in `src/ui/`; business/data models in `src/models/`; algorithms and orchestration in `src/core/`. Preserve `to_dict`/`from_dict` patterns for models and avoid GUI imports outside `ui/`.

## Testing Guidelines
- Framework: pytest. Place new tests in `tests/` (UI-related in `tests/ui/`). Use markers where appropriate (e.g., `diamante`).
- Aim for deterministic tests (no arbitrary sleeps); prefer pure model tests over GUI when possible. No strict coverage threshold, but include tests for new or changed behavior.

## Commit & Pull Request Guidelines
- Commits follow concise, imperative subjects (e.g., "Add connection line style options"). Keep messages under ~72 chars; include a descriptive body when needed.
- PRs should: describe the change and rationale, link issues, include before/after screenshots or GIFs for UI changes, update docs under `doc/` when behavior changes, and pass `pytest -q` locally. Keep PRs focused and avoid committing large binaries or generated content under `demo_projects/`.

## Security & Configuration Tips
- Some models execute user-provided `python_code` via `exec`; never load or commit untrusted snippets. Validate inputs and prefer pure functions in core/models.

