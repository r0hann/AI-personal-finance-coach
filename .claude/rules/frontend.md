---
paths:
  - "frontend/src/**/*.tsx"
  - "frontend/src/**/*.ts"
---

# Frontend Rules (React / TypeScript / Tailwind)

## Stack
- React + TypeScript + Tailwind CSS + Recharts
- Vite for bundling, served on port 5173 (dev) / 3000 (Docker)
- API base URL from `import.meta.env.VITE_API_BASE_URL` — never hardcode localhost

## API calls
- All fetch calls go to `$VITE_API_BASE_URL/<endpoint>`
- Streaming chat uses `fetch` with `response.body.getReader()` — not axios
- Always handle loading, error, and empty states in components

## Tailwind conventions
- Use Tailwind utility classes only — no inline styles, no custom CSS unless unavoidable
- Color palette follows the category colors defined in `supabase/schema.sql`
- Dark mode not required — design for light mode only

## Recharts
- Charts must be wrapped in `<ResponsiveContainer width="100%" height={300}>`
- Always provide a fallback when data is empty (skeleton or "No data" message)

## TypeScript
- Strict mode is on — no `any` types
- API response types must be explicitly typed, not inferred from `fetch`
- Use `Optional chaining (?.)` for nested API data access

## Component structure
- One component per file
- Props interfaces defined at top of file, named `<ComponentName>Props`
- No default exports for shared components — use named exports
