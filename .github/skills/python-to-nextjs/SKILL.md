---
name: python-to-nextjs
description: 'Migrate Python Streamlit logic to Next.js TypeScript. Use when converting Python functions from db.py, analytics.py, auth.py, or page files to TypeScript equivalents in the frontend. Maps pandas operations to JS, SQLite queries to API calls, Streamlit UI to React components.'
argument-hint: 'Python file or function to migrate (e.g. "analytics.py get_monthly_summary")'
---

# Python → Next.js Migration Skill

## When to Use
- Porting a specific Python function to TypeScript
- Creating a new API hook that replaces a `db.py` query
- Converting a Streamlit page (`pages/`) to a Next.js page
- Mapping `analytics.py` calculations to frontend hooks

## When NOT to Use
- Writing new features with no Python equivalent
- Pure UI/design work (use `stitch-component` skill)

## File Mapping

| Python Source | TypeScript Target | Purpose |
|---|---|---|
| `db.py` | `src/lib/api.ts` | Database operations → REST API calls |
| `analytics.py` | `src/hooks/useAnalytics.ts` | Analytics logic → React Query hook |
| `auth.py` | `src/stores/auth.ts` + `src/lib/api.ts` | Auth → Zustand store + API |
| `ui_components.py` | `src/components/*.tsx` | Reusable UI → React components |
| `pages/0_🏠_대시보드.py` | `src/app/(protected)/dashboard/page.tsx` | Dashboard |
| `pages/1_📝_입력.py` | `src/app/(protected)/transactions/new/page.tsx` | Transaction input |
| `pages/2_📋_내역.py` | `src/app/(protected)/transactions/page.tsx` | Transaction history |
| `pages/3_📊_분석.py` | `src/app/(protected)/analytics/page.tsx` | Analytics |
| `pages/4_⚙️_설정.py` | `src/app/(protected)/settings/page.tsx` | Settings |

## Migration Procedure

### 1. Read the Python Source
Read the target Python file to understand:
- Data structures (what SQLite columns / pandas DataFrames)
- Business logic (calculations, filtering, aggregation)
- UI flow (what the user sees and interacts with)

### 2. Map Data Patterns

| Python Pattern | TypeScript Equivalent |
|---|---|
| `pd.DataFrame` | `Transaction[]` (typed array) |
| `df.groupby()` | `array.reduce()` or lodash `groupBy` |
| `df['amount'].sum()` | `array.reduce((s, t) => s + t.amount, 0)` |
| `sqlite3.connect()` | `request<T>('/endpoint')` via api.ts |
| `st.session_state` | Zustand store |
| `st.cache_data` | React Query `staleTime` |
| `datetime.now()` | `new Date()` / `date-fns` |
| `f"{amount:,.0f}원"` | `formatCurrency(amount)` |

### 3. Apply Architecture Rules
- **NEVER** port SQLite queries to client side — they become API calls
- **NEVER** do line-by-line translation — restructure for React patterns
- Business logic that should remain server-side → API endpoint design only
- Client-side calculations → TanStack Query `select` or custom hook
- All data fetching through `src/lib/api.ts` wrappers

### 4. Checklist
- [ ] Read the original Python file first
- [ ] Identify which TypeScript file(s) are targets
- [ ] Map Python data structures to TypeScript types (`src/types/index.ts`)
- [ ] Use existing API wrappers (never direct fetch)
- [ ] Wrap data fetching in React Query hooks
- [ ] Use Zustand for client state that was in `st.session_state`
- [ ] Korean UI strings preserved
- [ ] Format functions from `src/lib/utils.ts` used (not inline formatting)
