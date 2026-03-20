---
description: "Use when creating or modifying React hooks, API calls, Zustand stores, or TanStack Query logic. Covers data fetching patterns and state management conventions."
applyTo: ["frontend/src/hooks/**", "frontend/src/stores/**", "frontend/src/lib/api.ts"]
---
# State & Data Rules

## API Client (`src/lib/api.ts`)
- All API calls go through the `request<T>()` wrapper — never use raw `fetch`.
- API base URL from `NEXT_PUBLIC_API_URL` env var.
- Errors are thrown as `ApiError(status, message)`.

## TanStack Query Hooks (`src/hooks/`)
- Every server-state read uses `useQuery` with structured `queryKey`.
- Mutations use `useMutation` and `invalidateQueries` on success.
- Query key convention: `["resource", ...params]` — e.g. `["transactions", filter]`.
- Cross-invalidate related keys: transaction mutations invalidate `["analytics"]` too.

## Zustand Stores (`src/stores/`)
- `useAuthStore`: user, token, setAuth, clearAuth (persisted to localStorage).
- `useFilterStore`: filter object, selectedMonth (not persisted).
- Access store state with selector: `useAuthStore((s) => s.user)`.

## Patterns to Avoid
- Do NOT call API directly from components — always use a hook.
- Do NOT put server-state in Zustand — that's TanStack Query's job.
- Do NOT create new stores without clear justification.
