---
description: "Use when referencing or converting Python Streamlit logic to TypeScript. Covers the legacy codebase mapping and migration strategy."
---
# Legacy Python Reference

This project is a Streamlit → Next.js migration. The Python source is reference-only.

## File Map (Python → TypeScript)
| Python | TypeScript Equivalent |
|--------|----------------------|
| `db.py` CRUD functions | `src/lib/api.ts` (REST calls to backend) |
| `analytics.py` pandas aggregation | `src/hooks/useAnalytics.ts` (API-backed) |
| `auth.py` session state | `src/stores/auth.ts` (Zustand + JWT) |
| `ui_components.py` Plotly charts | `src/app/**/page.tsx` (Recharts inline) |
| `pages/*.py` | `src/app/(protected)/**/page.tsx` |

## Migration Rules
- Do NOT port Python code line-by-line. Re-implement in idiomatic TypeScript.
- Business logic (aggregation, insights) moves to the **backend API**, not the frontend.
- Streamlit `st.session_state` → Zustand store or TanStack Query cache.
- Streamlit `st.sidebar` filters → `useFilterStore` + inline filter bars or bottom sheets.
- Plotly charts → Recharts with Stitch color tokens.

## Key Documents
- `MIGRATION_TECH_SPEC.md` — API endpoints, type definitions, architecture
- `MIGRATION_DESIGN_SPEC.md` — component specs, interaction flows, UI state maps
