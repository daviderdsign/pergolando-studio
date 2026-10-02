# UNTESTED: Docker isn't available in the environment this was written in
# (same caveat as ../docker-compose.dev.yml). Verify the actual build/run on
# the NAS before relying on it — in particular the exact shared-library list
# below is the commonly-documented minimum for headless Blender on Debian,
# not something confirmed against this specific image.
#
# Isolated on purpose: this is the ONLY container that needs Blender (~300MB
# download) — pergolando-backend calls it over HTTP instead of shelling out
# to Blender itself, so the ~300MB never touches the backend's own image.
FROM node:24-slim AS runtime

# Headless Blender still dynamically links against these even with no
# display attached (--background) — without them it fails to start with a
# shared-library error, not a clean "no display" message.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl xz-utils \
    libxi6 libxrender1 libxfixes3 libxkbcommon0 libgl1 libsm6 \
    && rm -rf /var/lib/apt/lists/*

# Pin the exact version rather than "latest" — matches the Blender version
# this repo's 3d/flag.blend and 3d/generate_flag.py were built/tested
# against (5.2.2 LTS). Bumping this needs re-verifying the whole 3d/ pipeline.
ARG BLENDER_VERSION=5.2.2
RUN curl -fsSL \
    "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
    -o /tmp/blender.tar.xz \
    && mkdir -p /opt/blender \
    && tar -xJf /tmp/blender.tar.xz -C /opt/blender --strip-components=1 \
    && rm /tmp/blender.tar.xz

WORKDIR /app
COPY package.json server.js ./

ENV PORT=8080
ENV BLENDER_EXECUTABLE_PATH=/opt/blender/blender
# 3d/flag.blend + 3d/generate_flag.py are expected mounted here at runtime
# (see docker-compose.dev.yml) — kept out of the image so a script/model
# tweak doesn't need a rebuild, same pattern as the bundle mount on
# pergolando-backend.
ENV THREED_ASSETS_PATH=/app/3d

EXPOSE 8080
CMD ["node", "server.js"]
