---
description: "Use when working with form validation, react-hook-form, zod schemas, or transaction/budget input forms."
applyTo: "frontend/src/app/**/new/**"
---
# Form & Validation Rules

## Stack
- `react-hook-form` for form state, `zod` for schema validation, `@hookform/resolvers` to connect them.

## Patterns
- Define zod schema at top of file, infer `FormData` type from it: `type FormData = z.infer<typeof schema>`.
- Use `useForm<FormData>({ resolver: zodResolver(schema), defaultValues })`.
- Register inputs: `{...register("fieldName")}`.
- Show errors inline: `{errors.field && <p className="text-error text-xs">{errors.field.message}</p>}`.

## Mutation Integration
- Call `useMutation` hook on form submit.
- Show loading: `disabled={mutation.isPending}` on submit button.
- Toast on success: `toast.success("...")`, on error: `toast.error(err.message)`.
- Reset form on success: `reset(defaultValues)`.

## UI Conventions
- Input background: `bg-surface-container-high border-none rounded-lg`
- Focus ring: `focus:ring-2 focus:ring-primary/20`
- Labels: `text-[10px] font-bold text-on-surface-variant uppercase tracking-wider`
- Submit button: `bg-primary text-on-primary py-4 rounded-xl font-bold text-lg shadow-lg shadow-primary/20`
