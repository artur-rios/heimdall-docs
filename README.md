# heimdall-docs

The home page and documentation portal for
[Heimdall](https://github.com/artur-rios/heimdall-api), a centralized identity
management system with scope-based multi-tenancy: an ASP.NET Core API and the
Flutter application that drives it. This site explains what Heimdall is, how it
is put together, how to run it, and how to use it, and it holds the detailed
documentation of the API and of the application, with the specification
documents of both. It is the single documentation site for Heimdall.

**[docs.artur-rios.tech/heimdall-docs](https://docs.artur-rios.tech/heimdall-docs/)**

This repository contains documentation only. It builds no software and ships no
package.

## The project

| Repository | What it holds |
|---|---|
| [heimdall-api](https://github.com/artur-rios/heimdall-api) | The ASP.NET Core identity API. |
| [heimdall-ui](https://github.com/artur-rios/heimdall-ui) | The Flutter application for web, Windows, Linux and Android. |
| [heimdall-docs](https://github.com/artur-rios/heimdall-docs) | This site. |

## Content the site does not own

Four paths hold files copied from the code repositories. The yggdrasil `sync`
feature rewrites each of them wholesale, with a commit straight to this
repository's `main`, whenever the repository it comes from is released (a push to
its `main` whose checks passed). A change made to them here is lost at the next
release, so **they must not be edited by hand**. To change one, change its
source in the code repository.

| Path in this repository | Copied from | Shown on the site as |
|---|---|---|
| `content/en/docs/api/requirements/documents/` | `docs/requirements/` in heimdall-api | The API requirements |
| `content/en/docs/application/requirements/documents/` | `docs/requirements/` in heimdall-ui | The application requirements |
| `static/api/openapi/heimdall.json` | `docs/openapi/heimdall.json` in heimdall-api | The API explorer and the OpenAPI document |
| `static/api/coverage-report/` | The coverage report that heimdall-api's `test` check archives (`docs/coverage-report/`) | The test coverage page |

Every other page is written here by hand. The CHANGELOG and CONTRIBUTING files of
the code repositories are not rendered on the site; its pages link to them on
GitHub.

## Running it locally

**Requirements:** [Hugo extended](https://gohugo.io/installation/) 0.160.1 or
newer — the minimum of Docsy v0.18.1; the site image builds with 0.165.0 — the [Go toolchain](https://go.dev/dl/)
— Docsy is consumed as a Hugo Module — and Node with npm, for the theme's Bootstrap
and Font Awesome and for Dart Sass. Python 3.11 or newer is needed only for the checks below (the checker
imports `tomllib`).

```bash
git clone https://git.techcraftsmen.net/artur-rios/heimdall-docs.git
cd heimdall-docs
npm ci
export PATH="$PWD/node_modules/.bin:$PATH"
hugo server
```

Hugo runs Dart Sass, which Docsy compiles its SCSS with, as `sass` from the
`PATH`; `npm ci` installs it as the `sass-embedded` package, hence the `export`.
On Windows, npm also installs the pure-JavaScript `sass` package, whose `sass`
command shadows the embedded one and cannot serve Hugo: put
`node_modules/sass-embedded-win32-x64/dart-sass` on the `PATH` instead, or
[install Dart Sass](https://gohugo.io/functions/css/sass/#dart-sass).

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
├── package.json              # Dart Sass (sass-embedded), autoprefixer, postcss-cli
├── package-lock.json
├── packages/hugoautogen/      # the theme's npm packages (`hugo mod npm pack`)
├── assets/scss/
│   └── _styles_project.scss  # light/dark code-block styles, diagrams, tables
├── content/en/
│   ├── _index.md             # landing page
│   ├── about/                # the about page
│   └── docs/                 # the documentation
│       ├── overview/ architecture/ installation/ user-guide/ integrating/ repositories/
│       ├── api/              # the API: reference, explorer, flows, operations, coverage, status
│       │   └── requirements/documents/   # copied from heimdall-api (sync-owned)
│       └── application/      # the UI: scope, environments, signing, status
│           └── requirements/documents/   # copied from heimdall-ui (sync-owned)
├── layouts/
│   ├── _markup/              # the link render hook for the copied documents
│   └── _shortcodes/          # swagger-ui, for the API explorer
├── static/api/
│   ├── openapi/heimdall.json # the OpenAPI document (sync-owned)
│   └── coverage-report/      # the coverage report (sync-owned)
├── docs/
│   ├── fact-sheet.md         # the cited facts the pages are written from
│   └── superpowers/          # the design specs, the plans, and the contradictions found
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

Docsy is the Hugo Module `github.com/docsy/docsy/theme`, at the version in
`go.mod`. Since v0.16.0 the theme declares Bootstrap and Font Awesome as npm
packages, which `hugo mod npm pack` writes into the `packages/hugoautogen`
workspace of `package.json`. Moving the theme is therefore four commands, not
one, or the stylesheets are built against the previous theme's Bootstrap:

```bash
hugo mod get github.com/docsy/docsy/theme@<version>
hugo mod npm pack
npm install
hugo --minify
```

Commit `go.mod`, `go.sum`, `package.json`, `package-lock.json` and
`packages/` once that build has produced `public/index.html` without a
warning. Run `hugo mod npm pack` again after any change to `package.json`
too: Hugo warns that the npm dependencies are out of sync until it has.

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
