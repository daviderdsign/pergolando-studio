# Pergolando

White-label system for pergola/awning manufacturers. Two components that share no database or code — only a versioned data package, the **bundle**, and one shared library for the schema/pricing logic:

- **Studio** (`apps/studio`, this repo) — internal tool: turns a manufacturer's PDF price list into a validated, versioned bundle.
- **App Venditore** — one deployment per client (own branding, own SQLite file, own container), built in [pergolando-backend](https://github.com/daviderdsign/pergolando-backend) and [pergolando-frontend](https://github.com/daviderdsign/pergolando-frontend).
- **[pergolando-shared](https://github.com/daviderdsign/pergolando-shared)** — the bundle Zod schema and the TypeScript pricing engine, consumed by both Studio and pergolando-backend as a tagged git dependency (`@pergolando/shared`). This is the single source of truth for pricing logic; it does **not** live in this repo.

## Workspace layout

```
apps/
  studio/          Fase 1 MVP: PDF ingest -> mapping editor -> validation -> bundle export
fixtures/
  vision/, brera/  The two already-validated reference catalogs, used as Studio's starting templates
prototype/
  vision_*.json, brera_*.json   The originally-provided catalog data (provenance, unmodified)
```

`pergolando-shared`, `pergolando-backend` and `pergolando-frontend` are separate GitHub repos, each with
its own history and tooling — not part of this pnpm workspace. If you clone them as sibling directories
here for convenience they're gitignored from this repo.

## Bundle schema and pricing engine

Both live in [pergolando-shared](https://github.com/daviderdsign/pergolando-shared), not here — see that
repo's README for why (git dependency instead of npm publish, the Python-to-TypeScript golden-output
regression tests, etc). Studio depends on it via:

```json
"@pergolando/shared": "github:daviderdsign/pergolando-shared#v0.1.0"
```

Bumping that ref is how Studio picks up schema/engine changes; there is no local copy to keep in sync.

## Development

Requires Node 24 (see `.nvmrc`) and pnpm.

```bash
pnpm install
pnpm build       # builds apps/*
pnpm typecheck
pnpm lint
```

Studio itself: `pnpm --filter @pergolando/studio dev`.

## Running App Venditore locally (one tenant)

`docker-compose.dev.yml` runs one backend+frontend pair against a bundle Studio has already exported —
see the file itself for prerequisites. It demonstrates the "one deployment per tenant" model: a second
tenant is a second backend+frontend pair with a different bundle/database/port, not a flag on this one.

```bash
docker compose -f docker-compose.dev.yml up --build
```

(Untested in this environment — Docker wasn't available. Verify before relying on it.)
