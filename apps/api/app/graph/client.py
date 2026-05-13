"""Async Microsoft Graph client wrapper.

Single point of entry for all Graph calls. Handles:
- 429 ``Retry-After`` honouring
- exponential backoff on 5xx
- pagination via ``@odata.nextLink``
- per-tenant concurrency limiting via an asyncio semaphore

Token acquisition is delegated to a caller-supplied async function so this
module stays free of Entra-specific code (Phase 4 wires it up).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.config import get_settings
from app.graph.backoff import exponential_backoff, parse_retry_after

logger = logging.getLogger("tg365.graph.client")

TokenProvider = Callable[[str], Awaitable[str]]  # tenant_id -> access_token


class GraphPermissionError(PermissionError):
    """Graph responded 403 — almost always a missing scope or consent."""


class GraphFatalError(RuntimeError):
    """4xx other than 401/403/429 — surfaced to the caller."""


@dataclass(slots=True)
class GraphMetrics:
    requests: int = 0
    retries: int = 0
    throttled: int = 0
    fatal: int = 0
    latencies_ms: list[float] = field(default_factory=list)


class GraphClient:
    """Reusable Graph client. Construct one per API process."""

    def __init__(
        self,
        token_provider: TokenProvider,
        *,
        client: httpx.AsyncClient | None = None,
        metrics: GraphMetrics | None = None,
    ) -> None:
        settings = get_settings()
        self._settings = settings
        self._tokens = token_provider
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._semaphores: dict[str, asyncio.Semaphore] = {}
        self.metrics = metrics or GraphMetrics()

    def _semaphore(self, tenant_id: str) -> asyncio.Semaphore:
        sem = self._semaphores.get(tenant_id)
        if sem is None:
            sem = asyncio.Semaphore(self._settings.graph_per_tenant_concurrency)
            self._semaphores[tenant_id] = sem
        return sem

    async def request(
        self,
        tenant_id: str,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        beta: bool = False,
    ) -> httpx.Response:
        base = self._settings.graph_beta_base_url if beta else self._settings.graph_base_url
        url = f"{base}{path}" if path.startswith("/") else path
        max_retries = self._settings.graph_max_retries

        async with self._semaphore(tenant_id):
            for attempt in range(max_retries + 1):
                token = await self._tokens(tenant_id)
                headers = {"Authorization": f"Bearer {token}"}
                self.metrics.requests += 1
                try:
                    r = await self._client.request(
                        method, url, params=params, json=json_body, headers=headers
                    )
                except httpx.HTTPError as exc:
                    if attempt >= max_retries:
                        self.metrics.fatal += 1
                        raise
                    self.metrics.retries += 1
                    sleep_s = exponential_backoff(
                        attempt,
                        base=self._settings.graph_backoff_base_seconds,
                        cap=self._settings.graph_backoff_cap_seconds,
                    )
                    logger.warning(
                        "graph.transport_error",
                        extra={"attempt": attempt, "sleep_s": sleep_s, "err": str(exc)},
                    )
                    await asyncio.sleep(sleep_s)
                    continue

                if r.status_code == 200:
                    return r
                if r.status_code == 429:
                    self.metrics.throttled += 1
                    sleep_s = (
                        parse_retry_after(r.headers.get("Retry-After"))
                        or exponential_backoff(
                            attempt,
                            base=self._settings.graph_backoff_base_seconds,
                            cap=self._settings.graph_backoff_cap_seconds,
                        )
                    )
                    if attempt >= max_retries:
                        self.metrics.fatal += 1
                        raise GraphFatalError(
                            f"throttled after {attempt + 1} attempts: {r.text[:200]}"
                        )
                    logger.warning(
                        "graph.throttled",
                        extra={"attempt": attempt, "sleep_s": sleep_s, "url": url},
                    )
                    self.metrics.retries += 1
                    await asyncio.sleep(sleep_s)
                    continue
                if 500 <= r.status_code < 600:
                    if attempt >= max_retries:
                        self.metrics.fatal += 1
                        raise GraphFatalError(f"server error {r.status_code}: {r.text[:200]}")
                    self.metrics.retries += 1
                    sleep_s = exponential_backoff(
                        attempt,
                        base=self._settings.graph_backoff_base_seconds,
                        cap=self._settings.graph_backoff_cap_seconds,
                    )
                    logger.warning(
                        "graph.5xx",
                        extra={"status": r.status_code, "attempt": attempt, "sleep_s": sleep_s},
                    )
                    await asyncio.sleep(sleep_s)
                    continue
                if r.status_code == 403:
                    self.metrics.fatal += 1
                    raise GraphPermissionError(
                        f"Graph 403: {r.text[:200]}"
                    )
                if 400 <= r.status_code < 500:
                    self.metrics.fatal += 1
                    raise GraphFatalError(f"client error {r.status_code}: {r.text[:200]}")
                return r

        raise GraphFatalError("retry loop exhausted without response")

    async def get_all(
        self,
        tenant_id: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        beta: bool = False,
        page_budget: int = 1000,
    ) -> AsyncIterator[dict[str, Any]]:
        """Iterate every item across paged responses."""
        next_url: str | None = path
        next_params = params
        pages = 0
        while next_url is not None and pages < page_budget:
            r = await self.request(tenant_id, "GET", next_url, params=next_params, beta=beta)
            data = r.json()
            for item in data.get("value", []):
                yield item
            next_url = data.get("@odata.nextLink")
            next_params = None  # nextLink already encodes the params
            pages += 1
