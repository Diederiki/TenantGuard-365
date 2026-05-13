"""Application configuration. Pulled from environment via Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production"]
AuthMode = Literal["mock", "entra"]
LogFormat = Literal["json", "console"]
LogLevel = Literal["debug", "info", "warning", "error", "critical"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,  # supplied by docker; nothing to read from disk
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core
    environment: Environment = "development"
    app_name: str = "M365 Enterprise Control Center"
    app_public_url: str = "http://localhost:3000"
    api_public_url: str = "http://localhost:8000"
    log_level: LogLevel = "info"
    log_format: LogFormat = "json"

    # Auth
    auth_mode: AuthMode = "mock"
    dev_session_secret: str = Field(
        default="dev-insecure-do-not-use-in-prod-change-me-now",
        min_length=16,
    )
    session_cookie_name: str = "tg365_session"
    session_idle_timeout_minutes: int = 60
    session_absolute_timeout_hours: int = 12
    csrf_cookie_name: str = "tg365_csrf"

    # Entra (filled in Phase 2)
    entra_tenant_id: str | None = None
    entra_client_id: str | None = None
    entra_client_secret: str | None = None
    entra_redirect_uri: str = "http://localhost:8000/auth/callback"
    entra_authority: str = "https://login.microsoftonline.com"

    # Graph (used Phase 3+)
    graph_base_url: str = "https://graph.microsoft.com/v1.0"
    graph_beta_base_url: str = "https://graph.microsoft.com/beta"
    graph_default_page_size: int = 100
    graph_max_retries: int = 8
    graph_backoff_base_seconds: float = 1.0
    graph_backoff_cap_seconds: float = 60.0
    graph_per_tenant_concurrency: int = 4
    token_cache_master_key: str | None = None

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql+psycopg://tg365:change-me@postgres:5432/tg365",
    )

    # Redis
    redis_url: RedisDsn = Field(default="redis://redis:6379/0")

    # OpenSearch
    opensearch_url: str = "http://opensearch:9200"
    opensearch_username: str | None = None
    opensearch_password: str | None = None
    opensearch_verify_certs: bool = False
    opensearch_index_prefix: str = "tg365"

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_region: str = "us-east-1"
    minio_root_user: str = "tg365admin"
    minio_root_password: str = "change-me-minio"  # noqa: S105  dev default, overridden by env
    minio_bucket_exports: str = "tg365-exports"
    minio_bucket_evidence: str = "tg365-evidence"
    minio_use_ssl: bool = False

    # Mail
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = False
    mail_from_address: str = "M365 Control Center <noreply@tg365.local>"

    # Feature flags (destructive features off by default)
    feature_remediation_enabled: bool = False
    feature_content_search_enabled: bool = False
    feature_defender_hunting_enabled: bool = False
    feature_purview_audit_enabled: bool = False

    # Telemetry
    otel_exporter_otlp_endpoint: str | None = None
    otel_service_name: str = "tg365-api"

    def assert_safe_for_environment(self) -> None:
        """Run startup checks that depend on multiple fields."""
        if self.environment == "production":
            if self.auth_mode == "mock":
                raise RuntimeError(
                    "AUTH_MODE=mock is forbidden when ENVIRONMENT=production"
                )
            if self.dev_session_secret.startswith("dev-insecure"):
                raise RuntimeError(
                    "DEV_SESSION_SECRET must be set to a strong random value in production"
                )
            if self.token_cache_master_key is None:
                raise RuntimeError(
                    "TOKEN_CACHE_MASTER_KEY must be set in production"
                )
            if self.feature_remediation_enabled:
                # Allowed but warn explicitly at startup.
                # The remediation framework still requires per-policy enable + approval.
                pass


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
