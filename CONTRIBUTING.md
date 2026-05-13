# Contributing

This is an internal enterprise project. Contributions follow the phased build plan in [ROADMAP.md](ROADMAP.md).

## Working principles

1. **Phase discipline.** Work the current phase. Do not skip ahead.
2. **Inspect first.** Read existing files before changing them. Update cleanly. No drive-by refactors.
3. **Complete files.** Land commit-ready code, not snippets.
4. **Document every decision.** Architecture / security choices land in `docs/`.
5. **Secure defaults.** No remediation, no destructive actions, no raw content storage unless explicitly opted in.
6. **No secrets in git.** Ever.
7. **Audit everything privileged.** Use `AuditLogger`, never raw inserts.
8. **Tests required.** Unit + integration coverage at phase exit.
9. **Track TODOs in ROADMAP.** No orphan TODO comments.
10. **One feature, one PR.** Small, reviewable, reversible.

## Branching

- `main` is always deployable to the dev environment.
- Feature branches: `feat/phase-<N>-<short-name>`.
- Bugfix branches: `fix/<short-name>`.
- Docs-only changes can land directly on `main` after review.

## Commit messages

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `security`, `perf`, `build`, `ci`.

## Reviews

- All PRs need at least one review.
- Security-sensitive changes (auth, RBAC, audit, remediation, Graph permissions) need a security-focused review and a note in the PR body referencing the relevant docs in `docs/security/`.

## Code style

- **Python**: ruff for lint+format, mypy strict, pytest. Line length 100.
- **TypeScript**: eslint, prettier, strict TS config.
- **SQL migrations**: Alembic; explicit `up` and `down`; no destructive ops without a release-note flag.

## Definition of done (per phase)

- [ ] Code merged
- [ ] Tests pass in CI
- [ ] Docs updated (`README`, `ROADMAP`, plus relevant `docs/` sections)
- [ ] Migrations applied and reversible
- [ ] Security implications documented
- [ ] Smoke check on a fresh `docker compose up`
