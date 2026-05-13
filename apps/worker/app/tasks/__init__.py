"""Register all tasks so the broker discovers them on import."""

from app.tasks import heartbeat, security  # noqa: F401
