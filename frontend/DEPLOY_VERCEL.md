# Deploy SentinelIQ frontend on Vercel

The app is a **TanStack Start** SSR app. Production builds use **Nitro** with the **Vercel** preset and emit the [Build Output API](https://vercel.com/docs/build-output-api/v3) layout under `.vercel/output/`.

## Prerequisites

- Node.js **20+** (see `package.json` `engines`)
- A deployed **FastAPI backend** with CORS enabled (see repo `backend/`)
- npm (use `package-lock.json`; do not rely on Bun for Vercel unless you configure it explicitly)

## Import the project

1. Push this repo to GitHub (or connect your Git provider in Vercel).
2. In Vercel: **Add New Project** → import the repository.
3. Set **Root Directory** to `frontend` (monorepo).
4. Vercel reads `frontend/vercel.json`:
   - **Install Command:** `npm ci`
   - **Build Command:** `npm run build`
   - **Framework Preset:** Other (Nitro supplies `.vercel/output`; do not set a separate Output Directory in the dashboard).

## Environment variables

In Vercel → Project → **Settings** → **Environment Variables**, add:

| Name | Example | Required |
|------|---------|----------|
| `VITE_API_BASE_URL` | `https://your-api.example.com` | **Yes** (production) |

- No trailing slash.
- The client calls paths such as `/health`, `/alerts`, `/dashboard/summary` (see `src/lib/api/client.ts`).
- If `VITE_API_BASE_URL` is empty, the browser requests your **Vercel domain**, which does not serve the FastAPI API unless you add separate rewrites.

Copy `frontend/.env.example` for local development.

## Verify locally

```bash
cd frontend
npm ci
npm run build
```

You should see Nitro log `preset: vercel` and output under `.vercel/output/`. Optional preview:

```bash
npx vite preview
```

## Smoke test after deploy

1. Open the production URL — executive dashboard (`/`).
2. In DevTools → Network, confirm API calls go to `VITE_API_BASE_URL` and return 200.
3. Visit `/alerts`, `/incidents`, and `/analytics`.

## Troubleshooting

- **Build skips Nitro / no `.vercel/output`:** Ensure `vite.config.ts` includes `nitro: { preset: "vercel" }`.
- **Empty dashboard / API errors:** Set `VITE_API_BASE_URL` and redeploy (Vite inlines `VITE_*` at build time).
- **Large upload:** `sentinel-hub-main.zip` is listed in `.vercelignore`.
