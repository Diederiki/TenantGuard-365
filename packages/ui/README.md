# packages/ui

> Shared React component library for the web app.
>
> **Phase 0**: empty. **Phase 1**: shadcn/ui generated components + project-specific compositions live here.

## What goes here

- Wrappers around shadcn/ui primitives with project styling baked in.
- Shared `DataTable` built on TanStack Table.
- Shared `Chart` wrappers around Recharts.
- Severity badges, status pills, audit-event line items.
- Empty / loading / error state components.

## What does not go here

- Page-specific layouts — those live under `apps/web/app/<route>/`.
- Module-specific tables — those live in each module's web folder.

## Style

- Tailwind. No CSS-in-JS.
- Components must support dark mode by default.
- Components must be accessible (keyboard navigation, ARIA labels, contrast).
