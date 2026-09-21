# Build context is the monorepo ROOT (not apps/studio), so this stage can
# see pnpm-workspace.yaml, the root lockfile, and fixtures/ — same layout
# Studio expects locally (apps/studio/../../fixtures).
FROM node:24-slim AS base
RUN corepack enable
WORKDIR /app

FROM base AS deps
# The @pergolando/shared git dependency's "prepare" script needs git.
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/studio/package.json apps/studio/package.json
RUN pnpm install --frozen-lockfile

FROM deps AS build
COPY . .
# Served at pergolando.rdsign-app.it/studio behind Cloudflare path routing —
# empty/unset for any other build (matches local dev, mounted at "/").
ARG STUDIO_BASE_PATH=""
ENV STUDIO_BASE_PATH=${STUDIO_BASE_PATH}
RUN pnpm --filter @pergolando/studio run build

FROM node:24-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production
# Recreates apps/studio/, node_modules/ and fixtures/ together, exactly as
# Next.js's file tracer laid them out under .next/standalone.
COPY --from=build /app/apps/studio/.next/standalone ./
COPY --from=build /app/apps/studio/.next/static ./apps/studio/.next/static
WORKDIR /app/apps/studio
EXPOSE 3000
CMD ["node", "server.js"]
