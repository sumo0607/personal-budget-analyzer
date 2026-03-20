# Design System Strategy: The Financial Architect

This design system is engineered to transform the mundane task of expense tracking into a high-end, editorial experience. We are moving away from the "utility spreadsheet" aesthetic toward a "Digital Curator" model—where data feels like a premium insight rather than a chore.

---

## 1. Creative North Star: "The Digital Curator"
The objective is **Informed Serenity**. Financial apps often trigger anxiety through cluttered grids and harsh red/green contrasts. Our direction uses **Organic Precision**: a layout that feels as organized as a boutique gallery. We break the "template" look by using intentional white space (asymmetry), high-contrast typography scales (editorial feel), and deep tonal layering instead of traditional borders.

---

## 2. Color & Surface Philosophy
We treat the screen as a physical workspace composed of stacked, semi-transparent layers.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to section off content.
Boundaries must be defined solely through background color shifts or tonal transitions. Use `surface-container-low` for secondary sections and `surface-container-highest` for emphasized interactive zones.

### Surface Hierarchy & Nesting
*   **Base:** `surface` (#f8f9fa)
*   **De-emphasized Areas:** `surface-container-low` (#f3f4f5)
*   **Primary Cards:** `surface-container-lowest` (#ffffff)
*   **Elevated Actions:** `surface-container-high` (#e7e8e9)

### The Glass & Gradient Rule
To achieve a "Signature" feel, use **Glassmorphism** for floating action buttons or navigation bars. Apply a 20px backdrop-blur to `surface` colors at 80% opacity. 
*   **Signature Texture:** For hero headers (e.g., Monthly Summary), use a subtle linear gradient from `primary` (#00475e) to `primary-container` (#1a5f7a). This adds a "soul" to the data that flat Indigo cannot provide.

---

## 3. Typography: Editorial Authority
We utilize a dual-font strategy to balance technical precision with human readability.

*   **Display & Headlines (Manrope):** Use for large financial figures and section headers. The geometric nature of Manrope provides a modern, architectural feel.
    *   *Scale Example:* `display-lg` (3.5rem) for the main account balance to create an unmistakable focal point.
*   **Body & Labels (Plus Jakarta Sans):** Used for transactional data and micro-copy. Its slightly wider apertures ensure readability at small sizes (`body-sm` 0.75rem).

**Typographic Hierarchy:** Always pair a `headline-sm` title with a `label-md` in `on-surface-variant` (#40484d) for a sophisticated, meta-data appearance.

---

## 4. Elevation & Depth: Tonal Layering
Traditional shadows are often "dirty." We use **Ambient Shadows** and **Tonal Stacking**.

*   **The Layering Principle:** Place a `surface-container-lowest` card on top of a `surface-container-low` background. The subtle 2-bit color shift creates a natural "lift" without visual noise.
*   **Ambient Shadows:** If a card must float, use a shadow with a 24px blur, 0px spread, and 6% opacity using a tint of `primary` (#00475e) rather than pure black.
*   **The Ghost Border Fallback:** For accessibility in input fields, use `outline-variant` (#c0c8cd) at **20% opacity**. Never use 100% opaque outlines.

---

## 5. Component Guidelines

### Buttons (High-End Utility)
*   **Primary:** Solid `primary` (#00475e) with `on-primary` (#ffffff) text. Use `lg` (1rem) rounded corners.
*   **Secondary:** `secondary-container` (#8df5e4) background with `on-secondary-container` (#007165) text. 
*   **Glass Action:** For floating buttons, use `surface-bright` with a 15% opacity and a heavy backdrop blur.

### Data Cards & Lists
*   **Forbid Dividers:** Do not use horizontal lines between transactions. Instead, use `3.5` (1.2rem) vertical spacing from the scale to group items. 
*   **Visual Rhythm:** Use `surface-container-lowest` for the card body and a small `primary-fixed` (#c0e8ff) accent bar (4px width) on the left side to denote "Active" or "Uncategorized" states.

### Input Fields
*   **Soft Focus:** Default state has no border, only a `surface-container-high` background. On focus, transition to a `ghost border` (outline-variant at 20%) and a subtle glow using `primary-fixed-dim`.

### Metrics & Chips
*   **Success (Income):** Use `secondary` (#006b5f) for text, never a harsh neon green.
*   **Destructive (Expense):** Use `error` (#ba1a1a) but only for the numerical value, keeping the surrounding UI neutral to reduce "spend-stress."

---

## 6. Do’s and Don’ts

### Do
*   **DO** use asymmetric margins (e.g., wider left padding than right) in hero sections to create a premium magazine feel.
*   **DO** use `display-sm` for large numbers but pair them with `label-sm` (all caps) to ground the data.
*   **DO** leverage the `spacing-10` (3.5rem) for top-of-page breathing room.

### Don’t
*   **DON'T** use 1px dividers. If you feel you need one, increase the background contrast between sections instead.
*   **DON'T** use pure black (#000000) for text. Use `on-background` (#191c1d) to maintain a soft, professional look.
*   **DON'T** crowd the screen. If more than 5 transactions are visible without scrolling, increase your vertical spacing.

---

## 7. Token Summary Reference

| Category | Token | Value | Application |
| :--- | :--- | :--- | :--- |
| **Color** | `primary` | #00475e | Main brand, CTAs, Active States |
| **Color** | `secondary` | #006b5f | Income figures, Growth metrics |
| **Color** | `surface` | #f8f9fa | Main App Background |
| **Shape** | `md` | 0.75rem | Standard Cards / Buttons |
| **Shape** | `xl` | 1.5rem | Bottom Sheets / Feature Cards |
| **Type** | `display-md` | 2.75rem | Total Balance / Hero Numbers |
| **Type** | `title-sm` | 1rem | Transaction Names |