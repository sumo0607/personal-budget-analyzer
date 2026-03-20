---
name: stitch-component
description: 'Generate React components following Vault Vista / Stitch design system. Use when creating new UI components, pages, or layouts for the frontend. Covers Material Design 3 tokens, glassmorphism, tonal layering, typography, and icon conventions.'
argument-hint: 'Component name and purpose (e.g. "BudgetCard — shows monthly budget progress")'
---

# Stitch Component Generator

## When to Use
- Creating a new React component (.tsx) in `frontend/src/components/`
- Building a new page in `frontend/src/app/`
- Converting a Stitch HTML mockup (`stitch/`) to React

## When NOT to Use
- Editing existing component logic (use standard edit flow)
- Backend/API work
- Non-UI utility functions

## Procedure

### 1. Check for Stitch Reference
Look for an existing HTML mockup in `stitch/vault_vista/` that matches the requested component.
If found, use it as the structural reference.

### 2. Component Scaffold
```tsx
'use client';

import { cn } from '@/lib/utils';

interface ${Name}Props {
  className?: string;
}

export default function ${Name}({ className }: ${Name}Props) {
  return (
    <div className={cn('...', className)}>
      {/* component body */}
    </div>
  );
}
```

### 3. Apply Design System Rules

**Surface Hierarchy** (light → dark layering):
- `bg-surface` → base canvas
- `bg-surface-container-low` → recessed areas
- `bg-surface-container` → default cards
- `bg-surface-container-high` → elevated cards
- `bg-surface-container-highest` → modals, sheets

**Typography** (Tailwind classes from `globals.css`):
- Headlines: `font-headline` (Manrope)
- Body/Labels: `font-body` (Plus Jakarta Sans)
- Sizes: `text-display-lg`, `text-headline-md`, `text-body-lg`, `text-label-sm`

**FORBIDDEN**:
- `border`, `border-b`, `divide-y` — use tonal surface differences instead
- `text-black`, `bg-black` — use `text-on-surface`, `bg-surface` tokens
- `shadow-md`, `shadow-lg` — use ambient shadows: `shadow-[0_2px_8px_rgba(99,102,241,0.08)]`

**Icons**:
```tsx
<span className="material-symbols-outlined text-[20px]">icon_name</span>
```

**Glassmorphism** (navigation, FAB, bottom sheets only):
```tsx
className="bg-white/70 backdrop-blur-xl"
```

### 4. Import Conventions
- Utilities: `import { cn, formatCurrency, formatDateKorean } from '@/lib/utils'`
- Icons map: `import { CATEGORY_ICONS } from '@/types'`
- Hooks: `import { useTransactions } from '@/hooks/useTransactions'`
- Stores: `import { useFilterStore } from '@/stores/filter'`

### 5. Color Token Quick Reference
See [tailwind.config.ts](./references/color-tokens.md) for full token list.

| Purpose | Token |
|---------|-------|
| Primary action | `bg-primary text-on-primary` |
| Secondary | `bg-secondary-container text-on-secondary-container` |
| Income | `text-tertiary` (green) |
| Expense | `text-error` |
| Outline (subtle) | `text-outline-variant` |

### 6. Checklist
- [ ] Uses `cn()` for className merging
- [ ] No 1px borders (tonal layering only)
- [ ] Korean UI strings
- [ ] Material Symbols for icons (not emoji or SVG)
- [ ] Correct surface hierarchy
- [ ] Responsive (mobile-first breakpoints)
- [ ] `'use client'` directive if using hooks/state
