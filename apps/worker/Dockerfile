# =============================================================================
# apps/worker — background workers + scheduler (Dramatiq + APScheduler)
# =============================================================================

FROM python:3.12-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd -g 10001 tg365 \
 && useradd -u 10001 -g tg365 -m -s /usr/sbin/nologin tg365

FROM base AS builder
WORKDIR /build
COPY requirements.txt /build/requirements.txt
RUN pip install --prefix=/install -r requirements.txt

FROM base AS runtime
COPY --from=builder /install /usr/local
WORKDIR /app
COPY --chown=tg365:tg365 . /app
USER tg365

# Default command runs both worker + beat in one process via the entrypoint.
# In production each role gets its own container; see docker-compose.prod.yml.
CMD ["python", "-m", "app.main"]
