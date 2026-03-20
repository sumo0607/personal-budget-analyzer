---
description: "Use when working with Tailwind config, global CSS, color tokens, or theming. Covers the Vault Vista design system color palette and spacing rules."
applyTo: ["frontend/tailwind.config.ts", "frontend/src/app/globals.css"]
---
# Tailwind & Theming Rules

## Color Tokens (Material Design 3)
All colors are defined in `tailwind.config.ts`. Key tokens:
- `primary` (#00475e) — CTAs, active states, main brand
- `secondary` (#006b5f) — income figures, growth metrics
- `error` (#ba1a1a) — expense figures, destructive actions
- `surface` (#f8f9fa) — app background
- `on-surface` (#191c1d) — primary text (never use pure #000)
- `on-surface-variant` (#40484d) — secondary text, labels

## Surface Hierarchy
- Base: `surface` → `surface-container-low` → `surface-container` → `surface-container-high` → `surface-container-highest`
- Cards: `surface-container-lowest` (#fff) — primary card background
- Active card accent: `border-l-4 border-primary` (left accent bar, not full border)

## Spacing
- `spacing-10` (2.5rem / 40px) for top-of-page breathing room
- `gap-4` between cards in grid
- No more than 5 transaction items visible without scrolling (generous vertical spacing)

## Do NOT
- Add 1px solid borders — use tonal layering or ghost borders (outline-variant at 20% opacity)
- Use pure black (#000000) for anything
- Add new color tokens without updating `tailwind.config.ts`
