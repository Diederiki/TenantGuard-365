"""Register all tasks so the broker discovers them on import."""

from app.tasks import heartbeat, reports, security  # noqa: F401
