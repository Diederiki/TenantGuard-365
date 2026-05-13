"""Smoke test: package imports cleanly with no broker connection required at import."""

from __future__ import annotations


def test_config_loads() -> None:
    from app.config import get_settings

    s = get_settings()
    assert s.environment in {"development", "staging", "production"}


def test_tasks_module_imports() -> None:
    import app.tasks  # noqa: F401
