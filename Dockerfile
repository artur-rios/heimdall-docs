# The docs site of Heimdall (the catalog's heimdall-docs, served at docs.artur-rios.tech/heimdall-docs): a Hugo site
# with the Docsy theme, built in a pinned Hugo image, checked, and served by static-web-server. It is the
# templates/site-hugo Dockerfile of yggdrasil, with the differences marked below. The repository has no other image, so
# this is the `Dockerfile` that yggdrasil's stacks/heimdall-docs.yml builds by default.
#
# The build arguments are the stack file's (templates/stacks/site.yml), which scripts/deploy.sh feeds:
#   PUBLIC_HOST, PUBLIC_PATH   the address the site is served at: Hugo's baseURL is https://<host><path>/ (just
#                    <path>/ when there is no host). The proxy does not strip the path, so the files are put under it
#                    too. The baseURL of hugo.toml is only what `hugo server` uses: this overrides it.
#   GIT_COMMIT, YGG_ENVIRONMENT   the commit and the environment this image is built for ({{ getenv
#                    "HUGO_GIT_COMMIT" }} and {{ getenv "HUGO_YGG_ENVIRONMENT" }} in a Hugo template: Hugo's getenv
#                    only allows names that start with HUGO_). The site does not read them today.
#
# Different from the template:
#   1. The theme (Docsy) is a Hugo Module (go.mod, pinned to v0.15.0 on purpose, see the README), so the build needs the
#      Go toolchain. The hugomods images have no variant with both Go and Node, and Docsy's PostCSS pipeline needs Node
#      (package.json), so the Go toolchain is copied from the pinned golang image into the Node variant. go.mod asks for
#      Go 1.26.7 or newer, which is newer than the Go of the hugomods images. The image has no git, so Hugo fetches the
#      module from proxy.golang.org (HUGO_MODULE_PROXY) and go.sum pins its hash. Nothing in the site reads the git
#      history (enableGitInfo is off), so .git is not in the build context.
#   2. The site is checked before it is served, as the Deploy workflow did before it published: the checker's own tests,
#      then scripts/check_site.py (required pages, internal links and anchors, unexpected Hugo warnings, placeholder
#      text), given the build log and the address the site is built for. A site that fails the check is not built into
#      an image, so it is not deployed. Python is the python image's: the checker needs 3.11 or newer.

FROM golang:1.26.10-bookworm@sha256:632dff7351799a5a9954a48dc06670ade72ee44e8c351cdc0e5a57af2fea21af AS go

FROM hugomods/hugo:debian-node-lts-0.165.0@sha256:eef6a12572c8cf3fea72fb034606f3e6a0821368682139378608eabc94e67c87 AS build

COPY --from=go /usr/local/go /usr/local/go
ENV PATH="/usr/local/go/bin:${PATH}"
# Hugo downloads modules with git unless told to use a module proxy (its default is "direct"), and the image has no git.
ENV HUGO_MODULE_PROXY=https://proxy.golang.org

WORKDIR /src

# The PostCSS toolchain on its own, so a change to a page does not install it again.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .

ARG PUBLIC_HOST=
ARG PUBLIC_PATH=
ARG GIT_COMMIT=
ARG YGG_ENVIRONMENT=
ENV HUGO_GIT_COMMIT=${GIT_COMMIT} \
    HUGO_YGG_ENVIRONMENT=${YGG_ENVIRONMENT}

# The build log is kept for the checker. A build that writes no output is the failure mode the Docsy pin exists for, and
# it does not fail the Hugo command (see the README), hence the test of index.html.
RUN set -eu; \
    if [ -n "$PUBLIC_HOST" ]; then base="https://$PUBLIC_HOST$PUBLIC_PATH/"; else base="$PUBLIC_PATH/"; fi; \
    printf '%s' "$base" > /tmp/base-url; \
    if ! hugo --environment production --minify --gc --baseURL "$base" --destination /out > /tmp/hugo.log 2>&1; then \
        cat /tmp/hugo.log; exit 1; \
    fi; \
    cat /tmp/hugo.log; \
    test -s /out/index.html

FROM python:3.14.9-slim-bookworm@sha256:945c2676dc2b18e0c1f16879244122c57c0ffede60006bf3df159c507a31bcae AS verify

WORKDIR /src
COPY scripts/ scripts/
COPY content/ content/
COPY --from=build /out/ public/
COPY --from=build /tmp/hugo.log /tmp/base-url /tmp/

RUN python -m unittest discover -s scripts -p "test_*.py" \
    && python scripts/check_site.py --public public --build-log /tmp/hugo.log --base-url "$(cat /tmp/base-url)"

FROM joseluisq/static-web-server:2.44.1@sha256:94618e3d17802265a21926217e6f9e7832b311b6fbf5933684001739fafed06a

# Declared again: an argument lives in the stage that declares it.
ARG PUBLIC_PATH=
ARG GIT_COMMIT=
ARG YGG_ENVIRONMENT=

# The server has no shell, so nothing is run here: the checked site is copied under its path, and /healthz is a file of
# its own at the root. Port 8080, a numeric non-root user.
COPY --from=verify /src/public/ /public${PUBLIC_PATH}/
COPY <<EOF /public/healthz
ok
EOF

# Hugo writes 404.html at the site's root (under the path): an address the site does not have is a 404.
ENV SERVER_PORT=8080 \
    SERVER_ROOT=/public \
    SERVER_ERROR_PAGE_404=/public${PUBLIC_PATH}/404.html

LABEL org.opencontainers.image.revision="${GIT_COMMIT}" \
      yggdrasil.built-for="${YGG_ENVIRONMENT}"

USER 65532:65532
EXPOSE 8080
