# Pergolando

White-label system for pergola/awning manufacturers. Two components that share no database or code — only a versioned data package, the **bundle**:

- **Studio** (`apps/studio`) — internal tool: turns a manufacturer's PDF price list into a validated, versioned bundle.
- **App Venditore** — multi-tenant seller app (not built in this phase; see `Pergolando — PRD e architettura.md`).

## Workspace layout

```
packages/
  bundle-schema/   Zod schema for the bundle (single source of truth) + generated JSON Schema
  pricing-engine/  TypeScript port of prototype/pergola_engine.py, golden-tested against it
apps/
  studio/          Fase 1 MVP: PDF ingest -> mapping editor -> validation -> bundle export
fixtures/
  vision/, brera/  The two already-validated reference catalogs, used as schema/engine test fixtures
prototype/
  pergola_engine.py  Original Python reference engine — source of truth for the golden regression tests
```

`bundle-schema` and `pricing-engine` are plain packages, not yet published — kept in this monorepo because
Studio is currently their only consumer. When App Venditore work starts (Fase 2), decide then whether to
publish them, use a git submodule, or keep the monorepo and add `apps/venditore` here.

## Why a TypeScript port of `pergola_engine.py`, not a rewrite

`packages/pricing-engine/src/engine.ts` mirrors `prototype/pergola_engine.py`'s `PergolaEngine.configura`
line-for-line, including known quirks (e.g. opzione_tecnica auto-selection comparing against the *total*
requested L rather than the per-module L when growth is on the "L" axis). This is intentional: the Python
engine is already validated against real Vision and Brera catalogs, so the port must reproduce it exactly,
not "fix" it silently.

`packages/pricing-engine/scripts/generate_golden_fixtures.py` runs the Python engine against a representative
set of inputs (both products, both growth orientations, both blade options, coupling detractions, montante
height supplements, and every error path) and writes the results to `fixtures/*/golden_cases.json`.
`packages/pricing-engine/src/engine.test.ts` replays those same inputs through the TypeScript engine and
asserts identical numeric output. Re-run the generator only if `pergola_engine.py`'s logic changes:

```bash
cd packages/pricing-engine
python scripts/generate_golden_fixtures.py
```

## Bundle schema

`packages/bundle-schema/src/*.ts` is the source of truth (Zod). The formal JSON Schema the PRD asks for is
generated from it, not hand-maintained:

```bash
pnpm --filter @pergolando/bundle-schema run generate-json-schema
# writes packages/bundle-schema/schema/bundle.schema.json
```

## Development

Requires Node 24 (see `.nvmrc`) and pnpm.

```bash
pnpm install
pnpm build       # builds packages in dependency order
pnpm test        # vitest — schema validation + pricing-engine golden-output regression tests
pnpm typecheck
pnpm lint
```
