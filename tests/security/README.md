# tests/security

Security regression tests at the platform level. The Python-side defaults
guard lives in [apps/api/tests/security/test_security_posture.py](../../apps/api/tests/security/test_security_posture.py).

Planned additions:
- CSP header presence + violation reports
- CSRF rejection on POST/PATCH without header
- 401 / 403 enforcement on every authenticated route
- Token cache decrypt-cross-tenant failure
- Rate-limit middleware actually rate-limits
- Audit log append-only DB trigger enforcement
