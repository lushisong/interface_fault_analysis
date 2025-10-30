# Repository Guidelines

## Project Structure & Module Organization
Source code resides in `src/`, grouped into `core/` for orchestration, `models/` for data definitions, `ui/` for PyQt5 components, `analysis/` for computation, `utils/` for helpers, and `templates/` for reusable layouts. The GUI entry point is `main.py`. Tests live in `tests/` with UI-specific suites under `tests/ui/`. Quick demos (`simple_demo.py`, `create_drone_demo.py`) produce sample assets in `demo_projects/`, while documentation and shared assets stay in `doc/`, `data/`, and `templates/`. Keep generated logs (for example `app.log`) out of commits.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows) to create and enter the virtual environment.
- `pip install -r requirements.txt` installs runtime and tooling dependencies.
- `python main.py` launches the PyQt5 interface; `python simple_demo.py` provides a quick functional smoke test.
- `python create_drone_demo.py` populates `demo_projects/` with sample data for manual exploration.
- `pytest -q` runs the full automated suite; narrow focus with `pytest -k "module_panel" -q` or marker runs such as `pytest -m diamante -q`. Set `QT_QPA_PLATFORM=offscreen` for headless execution.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation, meaningful docstrings, and type hints where practical. Restrict UI imports to modules within `src/ui/`. Use `PascalCase` for classes, `snake_case` for modules, functions, and variables, and name tests `tests/test_*.py`. Preserve `to_dict`/`from_dict` patterns in models and keep GUI code separate from business logic.

## Testing Guidelines
The project uses pytest; aim for deterministic, fast tests that favor model and core layers over GUI fixtures. Name fixtures descriptively and avoid brittle timing-based assertions. Place new UI tests under `tests/ui/` and keep shared helpers in `tests/conftest.py`. Run targeted subsets before full sweeps to keep feedback loops short.

## Commit & Pull Request Guidelines
Write commits with short imperative subjects (for example, `Add connection line style options`) and detailed bodies only when needed. Pull requests should explain intent, reference issues, document behavioral changes (update `doc/` if user-facing behavior shifts), and include screenshots or GIFs for UI updates. Ensure `pytest -q` passes locally and exclude generated assets from diffs.

## Security & Configuration Tips
Certain models execute user-provided `python_code` via `exec`; validate or sanitize inputs before execution and never commit unvetted snippets. Keep secrets out of the repository and prefer configuration through environment variables or `.env` files that stay untracked.
