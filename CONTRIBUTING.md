# Contributing

Thanks for improving the API & System Health Monitor.

## Development Workflow

1. Create a focused branch for your change.
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Run `python -m pytest -v` before opening a pull request.
4. If you touch runtime behavior, also run `python monitor.py --config config.yaml run --cycles 1 --report`.
5. Document any architecture or operational changes in `docs/`.

## Code Review Checklist

- Keep monitor output deterministic and easy to debug.
- Prefer configuration over hardcoded endpoints or thresholds.
- Add or update tests for every behavioral change.
- Preserve cross-platform support for Windows, Linux, and macOS.
- Note any tradeoffs in the pull request description.
