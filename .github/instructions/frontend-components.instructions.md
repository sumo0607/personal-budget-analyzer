---
description: "Use when writing React components, pages, or layouts in the Next.js frontend. Covers Stitch design system tokens, Tailwind patterns, and component conventions."
applyTo: "frontend/src/**/*.tsx"
---
# Frontend Component Rules

## Stitch Design System
- **No 1px borders.** Use tonal layering: `bg-surface-container-lowest` on `bg-surface-container-low` background.
- Ambient shadows: `shadow-[0_4px_20px_rgba(0,71,94,0.04)]` (primary-tinted, not pure black).
- Glassmorphism for floating elements: `bg-[#f8f9fa]/80 backdrop-blur-xl`.
- Refer to `stitch/vault_vista/DESIGN.md` for full token reference.

## Typography
- Headlines: `font-headline font-extrabold tracking-tight` (Manrope)
- Body: `font-body` or `font-label` (Plus Jakarta Sans)
- Labels: `text-[10px] font-bold uppercase tracking-wider text-on-surface-variant`

## Icons
- Always use Material Symbols: `<span className="material-symbols-outlined">icon_name</span>`
- Fill for active state: `style={{ fontVariationSettings: "'FILL' 1" }}`

## Component Patterns
- Mark client components with `"use client"` at top
- Use `cn()` from `@/lib/utils` for conditional classes
- Format currency via `formatCurrency()` / `formatCurrencyShort()` from `@/lib/utils`
- Category icons via `CATEGORY_ICONS` map from `@/types`
