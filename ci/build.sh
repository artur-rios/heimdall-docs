#!/bin/sh
# The `build` check: the site's image (the Dockerfile) can still be produced, which is Hugo building the whole site with its Docsy module and, for the stages that follow, the site checker
# (required pages, links, anchors, placeholder text) passing.
# The old Deploy workflow built the site on every pull request, so a required status check had something to require; this
# is that. Build only, no push and no run: how the image answers is the deploy's. yggdrasil.yml runs it in the pinned docker
# CLI image (an Alpine one: no bash, hence sh) with the CI engine's socket (`docker: true`), from the repository's root. The
# image has a tag of its own for each run and is removed when the script ends, so builds in parallel never share one and
# none is left behind.
set -eu

# The repository's root, wherever this is run from.
cd "$(dirname "$0")/.."

# A tag of its own for each run: the shell is PID 1 in its container, so the process id alone would not be one.
image="heimdall-docs-site-check:$(date +%s)-$(tr -dc a-z0-9 </dev/urandom | head -c 8)"
trap 'docker rmi --force "$image" >/dev/null 2>&1 || true' EXIT

# The address the deploy builds for (the stack's PUBLIC_HOST and PUBLIC_PATH), so the checker sees the same links.
docker build --file Dockerfile --tag "$image" \
    --build-arg PUBLIC_HOST=docs.artur-rios.tech --build-arg PUBLIC_PATH=/heimdall-docs .
