# Heimdall documentation portal — design

- **Date:** 2026-10-13
- **Repository:** `heimdall-docs`
- **Published at:** GitHub Pages — <https://artur-rios.github.io/heimdall-docs/>
- **Status:** approved

## 1. Problem

Heimdall is spread across two code repositories. `heimdall-api` holds the
ASP.NET Core identity API; `heimdall-ui` holds the Flutter front-end for the
web, Windows, Linux and Android. The API already publishes a deep developer
site at <https://artur-rios.github.io/heimdall-api/> — architecture, domain
model, API reference, Swagger explorer, flows, operations, environments,
requirements and coverage — but it documents the API alone. Nothing introduces
Heimdall as a whole, documents the UI beyond its Markdown specifications,
explains how the pieces and the client systems that rely on Heimdall fit
together, or tells a person how to use it.

`heimdall-docs` becomes that home page and documentation source.

## 2. Scope

A Hugo site using the Docsy theme, **published on GitHub Pages** at
`https://artur-rios.github.io/heimdall-docs/`, covering the whole project:

- a landing page that serves as Heimdall's home page,
- an overview of the project and its concepts,
- the system architecture across API, UI, database, integrations and client
  systems, and the UI's own architecture, with Mermaid diagrams,
- installation: running the API, running and building the UI for each target,
  and where released artifacts come from,
- a user guide to the UI, organised by role,
- a guide to integrating a client system with Heimdall,
- a map into the API site's sections,
- the project's repositories and their canonical documents.

### 2.1 Relationship to the heimdall-api site

The portal **links into** the heimdall-api site for API internals and never
copies them: the API reference, the Swagger explorer, the sequence-diagram
flows, operations, environments and deployment, the requirements rendering,
the changelog, contributing and the coverage report. Two copies would drift;
the API site is generated from the API repository and stays authoritative for
it. The portal adds what that site cannot hold: the project-wide view, the UI,
and the user's perspective.

### 2.2 Explicitly out of scope

- The site builds no software and publishes no artifact. It documents the
  artifacts the code repositories' own workflows produce.
- No change to `heimdall-api`'s site, workflows or content.

## 3. Site structure

```txt
heimdall-docs/
├── go.mod, go.sum              # Docsy, as a Hugo Module
├── hugo.toml                   # baseURL, Mermaid, menus, repository links
├── package.json                # autoprefixer + postcss-cli for Docsy's SCSS
├── assets/scss/                # code-block and project styles
├── i18n/en.toml                # footer override
├── content/en/
│   ├── _index.md               # landing page
│   ├── about/_index.md
│   └── docs/
│       ├── _index.md
│       ├── overview/
│       ├── architecture/
│       ├── installation/
│       ├── user-guide/
│       ├── integrating/
│       ├── api/
│       └── repositories/
└── .github/workflows/deploy.yml
```

Content lives under `content/en/` so a `pt-BR` tree can be added later without
restructuring. The site ships English only.

## 4. Content plan

### 4.1 Landing page

A Docsy cover with the one-line pitch, "Get started" (docs) and "Source"
(GitHub) buttons, a lead paragraph, and feature blocks: scope-based
multi-tenancy, roles, persons and applications, authentication options
(password, Google, two-factor), one UI on four targets, and the open-source
licence.

### 4.2 Overview

What Heimdall is — a centralized identity-management API with scope-based
multi-tenancy, and its UI — and what it is not. The concepts in brief: scopes,
the three roles, persons, applications, scope permissions and JWT claims,
Google users, two-factor authentication, deletion strategies. Each concept
links to the API site's Overview or Domain model for the full rules.

### 4.3 Architecture

Mermaid diagrams:

1. **System context** — client systems, the UI, the API, PostgreSQL, and the
   external integrations the API uses.
2. **API layers** — Domain, Application (Command, Query, Shared),
   Infrastructure, Presentation; summarised, linking to the API site's
   Architecture page for the class diagrams.
3. **UI architecture** — its structure, state, the generated API client, and
   how it reaches the API; documented here because no other site does.
4. **Role-based UI** — what System Admin, Scope Admin and User each see, noting
   that the API remains the sole authority.

### 4.4 Installation

Running the API locally (prerequisites, configuration, migrations, Docker
Compose), running and building the UI for web, Windows, Linux and Android with
each target's prerequisites, and where released builds come from — exactly as
the repositories' workflows and releases state.

### 4.5 User guide

The UI's use cases UI-01 … UI-30, grouped into task-oriented pages: signing in
(password, Google, second factor), recovering a password and verifying an
address, managing your own profile, and the administration pages for scopes,
persons, applications, scope permissions and Google users — each marked with
the roles that can reach it.

### 4.6 Integrating a client system

How a system such as Fortuna relies on Heimdall: getting a scope, persons and
applications authenticating within it, the JWT and the permission claims
folded into it, and the caller key. Sourced from the API's requirements and
from Fortuna's integration; links to the Fortuna site as a worked example.

### 4.7 API documentation

A table mapping each heimdall-api site section to what it covers, with deep
links: Overview, Getting started, Architecture, Domain model, API reference,
API explorer, Flows, Operations, Environments and deployment, Requirements
(including the data-protection documents), Changelog, Contributing, coverage.

### 4.8 Repositories

The three repositories, what each holds, its default branch, its released
versions, and deep links to every document under each code repository's
`docs/requirements/`.

### 4.9 About

Why Heimdall exists, the stack in one line per repository, and the licence.

## 5. Build and deployment

- Docsy v0.15.0 as a Hugo Module, pinned for the same reason as
  `alexandria-docs`: v0.16.0 resolves but builds no output. Requires the Go
  toolchain locally and in CI.
- Hugo extended, minimum 0.158.0; CI builds with 0.165.0.
- `.github/workflows/deploy.yml`: on pull request, build only; on push to
  `main` and on manual dispatch, build with the Pages base URL and deploy
  through `actions/upload-pages-artifact` and `actions/deploy-pages`. Every
  build asserts that `public/index.html` was produced.
- **GitHub Pages**, with Settings → Pages → Source set to **GitHub Actions**.
  `baseURL` is `https://artur-rios.github.io/heimdall-docs/`.

## 6. Correctness rule

Every factual claim on the site is sourced from the two code repositories'
READMEs, changelogs, requirements documents, workflows and published releases,
and from the heimdall-api site. No feature, version, endpoint, environment
variable or command is invented. Where a detail cannot be verified from those
sources, the page links to them instead of asserting it.

## 7. Verification

- `hugo --minify` builds with no errors and no warnings, and writes
  `public/index.html`.
- No broken internal links in the built output; external links to the
  repositories and the heimdall-api site resolve.
- Every page renders legibly in light and dark mode at desktop and phone
  widths, and every Mermaid diagram renders.
- After the first push to `main`, the Deploy workflow succeeds and
  `https://artur-rios.github.io/heimdall-docs/` serves the site.

## 8. Assumptions

1. The GitHub repository is `artur-rios/heimdall-docs`, public, default branch
   `main`, created as part of this work.
2. The initial site is pushed directly to `main`; the repository is new and
   nothing protects it yet.
3. The site is English-only at launch.
