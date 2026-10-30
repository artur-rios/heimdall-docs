# heimdall-docs

The home page and documentation portal for
[Heimdall](https://github.com/artur-rios/heimdall-api), a centralized identity
management system with scope-based multi-tenancy: an ASP.NET Core API and the
Flutter application that drives it. This site explains what Heimdall is, how it
is put together, how to run it, and how to use it. The API's internals live on
the [heimdall-api site](https://docs.artur-rios.tech/heimdall-api/).

**[docs.artur-rios.tech/heimdall-docs](https://docs.artur-rios.tech/heimdall-docs/)**

This repository contains documentation only. It builds no software and ships no
package.

## The project

| Repository | What it holds |
|---|---|
| [heimdall-api](https://github.com/artur-rios/heimdall-api) | The ASP.NET Core identity API. |
| [heimdall-ui](https://github.com/artur-rios/heimdall-ui) | The Flutter application for web, Windows, Linux and Android. |
| [heimdall-docs](https://github.com/artur-rios/heimdall-docs) | This site. |

## Running it locally

**Requirements:** [Hugo extended](https://gohugo.io/installation/) 0.158 or
newer — the configuration uses `locale` and `languages.*.label`, which arrived
in that release; the site image builds with 0.165.0 — the [Go toolchain](https://go.dev/dl/)
— Docsy is consumed as a Hugo Module — and Node with npm, for Docsy's PostCSS
pipeline. Python 3.11 or newer is needed only for the checks below (the checker
imports `tomllib`).

```bash
git clone https://git.techcraftsmen.net/artur-rios/heimdall-docs.git
cd heimdall-docs
npm ci
hugo server
```

The site is then at <http://localhost:1313/heimdall-docs/>.

To reproduce what the image builds:

```bash
hugo --minify
```

## Checking it

Jenkins' `build` check builds the site image on every pull request, and the
image builds the site and then checks it, so a site that fails the check fails
the pull request and is never deployed. The check is that required pages exist, internal links
and anchors resolve, Hugo printed no unexpected warnings, and no placeholder
text is left. To run the same check locally:

```bash
hugo --minify 2>&1 | tee hugo.log && python scripts/check_site.py --public public --build-log hugo.log
```

The pages that must exist are listed in `scripts/required_pages.txt`. The
checker has its own tests:

```bash
python -m unittest discover -s scripts -p "test_*.py"
```

## Layout

```txt
heimdall-docs/
├── hugo.toml                 # site configuration
├── go.mod                    # the Docsy theme, as a Hugo Module
├── package.json              # autoprefixer + postcss-cli
├── assets/scss/
│   └── _styles_project.scss  # light/dark code-block styles, diagrams, tables
├── content/en/
│   ├── _index.md             # landing page
│   ├── about/                # the about page
│   └── docs/                 # the documentation
├── docs/
│   ├── fact-sheet.md         # the cited facts the pages are written from
│   └── superpowers/          # the design spec and the plan the site was built from
├── i18n/en.toml              # footer text
├── scripts/
│   ├── check_site.py         # post-build site checker
│   ├── test_check_site.py    # tests for the checker
│   └── required_pages.txt    # pages that must be built
├── LICENSE
├── ci/build.sh               # the pull request check: builds the image
├── yggdrasil.yml             # what Jenkins checks
├── Dockerfile                # builds, checks and serves the site
├── .dockerignore
├── renovate.json             # dependency updates
└── .gitattributes
```

Content lives under `content/en/` so a `pt-BR` translation can be added
alongside it without restructuring.

## Updating the theme

`go.mod` currently pins Docsy to v0.15.0 on purpose. v0.16.0 moved the actual
theme (`layouts/`, `assets/`) into a git submodule that Go's module zip does
not include, so it resolves as a Hugo Module but builds no output.

**v0.16.0 was checked on 2026-08-24, in the sibling alexandria-docs site, and the
fault was unchanged.** It resolves, then fails at build with `template for
shortcode "blocks/cover" not found` and writes no `public/`. Later releases
(v0.18.0 at the time of writing) have not been verified here. The pin stays
until one is.

Bumping the version therefore needs a real check, not just a green `go get`:

```bash
hugo mod get -u github.com/google/docsy
hugo --minify
```

Only commit the resulting `go.mod` and `go.sum` once that build has actually
produced `public/index.html` — an empty or missing `public/` means the new
version is broken the same way v0.16.0 was, and the pin should stay.

## Deployment

The site is deployed by Jenkins, from the yggdrasil pipeline: every push to
`main` builds the `Dockerfile` and deploys the image to production, where it
is served at <https://docs.artur-rios.tech/heimdall-docs/>. The image answers
`/healthz` for the status check. The address comes from the build arguments
`PUBLIC_HOST` and `PUBLIC_PATH`, which the deploy passes, so the `baseURL` in
`hugo.toml` only matters for `hugo server`.

Every pull request is checked by Jenkins' `build` check (`yggdrasil.yml`, run by
`ci/build.sh`), which builds the same image without pushing or running it, and the site
check above runs inside that build.

To build the image locally:

```bash
docker build -t heimdall-docs \
  --build-arg PUBLIC_HOST=docs.artur-rios.tech --build-arg PUBLIC_PATH=/heimdall-docs .
docker run --rm -p 8080:8080 heimdall-docs
```

The site is then at <http://localhost:8080/heimdall-docs/>.

## Contributing

The GitHub repository is a read-only mirror for the real, open-source code of heimdall-docs. Its home is Forgejo, at
https://git.techcraftsmen.net/artur-rios/heimdall-docs. If you want to contribute, e-mail me at arturdev@duck.com.
