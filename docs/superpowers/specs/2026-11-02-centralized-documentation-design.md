# Centralized documentation: design

Date: 2026-11-02. Status: draft, waiting for the owner's approval.

## Intent

Heimdall's documentation is split across three places today:

- **heimdall-docs**, the portal at docs.artur-rios.tech/heimdall-docs: overview, architecture, installation, user
  guide, integrating, repositories, and an "API documentation" page that is only a list of links to the API site;
- **heimdall-api's own site**, at docs.artur-rios.tech/heimdall-api, built from `heimdall-api/docs/` by
  `docs.Dockerfile` and deployed by the `heimdall-api-docs` catalog entry: overview, getting started,
  architecture, domain model, eight flow pages, operations, environments and deployment, API reference, a
  Swagger UI explorer, the fourteen requirements documents, the changelog, contributing, and the coverage report;
- **heimdall-ui**, which has no site: its 400-line README carries everything (prerequisites, configure, run,
  build, container image, use case status), and its seven requirements documents are published nowhere.

The owner wants one place to read about Heimdall: **heimdall-docs**. The code repositories keep only what a
developer working in them needs.

## Goals

1. heimdall-docs is the only Heimdall documentation site. Everything readers find on the API site today, and
   everything the two READMEs teach beyond an overview, is on it.
2. heimdall-api and heimdall-ui each keep: a README with an overview and a link to the docs site,
   `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `docs/requirements/` and `docs/superpowers/`.
3. The artifacts that only heimdall-api can produce reach heimdall-docs by themselves: when the **coverage
   report**, the **OpenAPI document** or the **requirements documents** of heimdall-api change on `main`, and when
   heimdall-ui's **requirements documents** change on `main`, Jenkins copies them into heimdall-docs and pushes
   the commit **directly to heimdall-docs' `main`**, which redeploys the site as any push to `main` does.
4. The API site, its image and its catalog entry are retired.

## Non-goals

- Rewriting the documentation. Pages move and are merged; their substance stays.
- Moving the requirements documents out of the code repositories. They stay where they are, as working files
  (owner's decision): the implement-use-case skill reads them, code comments cite them
  (`LegalBasisRecorder.cs` cites the Privacy Notice's version), and heimdall-ui's `tool/refresh_privacy_notice.dart`
  fetches `Privacy Notice.md` from heimdall-api. The docs site shows copies.
- Moving the superpowers specs and plans. They are each repository's working notes, not reader documentation.
- Changing where the OpenAPI document is generated or checked. heimdall-api's `check` check still compares it with
  the code, and heimdall-ui's `tool/refresh_openapi.dart` still reads it from the heimdall-api checkout.
- Changing how the coverage report is made (`scripts/coverage.py`, the `test` check).
- A pt-BR translation.

## Anti-goals (it fails even if it builds)

- **A write token for heimdall-docs reachable by pull-request code.** A check runs any branch's code
  (yggdrasil's own rule, `docs/catalog.md`, which is why a release's signing key is never a check's credential).
  A token a pull request can read is a token anyone who opens a pull request owns.
- **A copy from anything but `main`.** The site describes the released API and application, never `develop` or a
  pull request.
- **A copy that edits by hand-maintained files in heimdall-docs.** The copied paths belong to the copy; the site's
  own pages never live under them, and a copy never touches anything else.
- **Two sources for the same page.** After the move, a topic is written once, in heimdall-docs. The READMEs do not
  keep a second "Configure" or "Deploy" section that can drift.
- **Broken old links** without a decision: docs.artur-rios.tech/heimdall-api/... is linked from READMEs, the
  CHANGELOG, specs and plans; see "Old addresses".

## Constraints

- **heimdall-docs** is a Hugo site with Docsy as a Hugo Module pinned to v0.15.0 (`go.mod`; the README explains
  why v0.16.0 cannot be used), built, checked (`scripts/check_site.py`: required pages, internal links and anchors,
  Hugo warnings, placeholders) and served by its `Dockerfile`. Its catalog entry deploys production on every push
  to `main` after its `build` check passes. It is a `rules: basic` repository: `main` refuses force pushes and
  deletion and nothing else, so an account with write access can push to it directly.
- **The API site** uses Docsy from npm (`@docsy/theme`, 0.17 or later, Dart Sass), `enableGitInfo`, a
  `render-link` hook that turns the requirements documents' GitHub-style links (sibling `.md` files, `../src/`,
  `../tests/`, `../scripts/`) into site links or GitHub links, a `repo-file` shortcode, Mermaid settings in the
  Docsy 0.18 plugin form, and a Swagger UI page (`api-explorer.md`) that fetches `/openapi/heimdall.json`. What it
  needs must work on heimdall-docs' Docsy v0.15.0, or heimdall-docs moves its Docsy pin as a separate, verified
  step (the README's procedure).
- **yggdrasil** (the CI/CD, `D:\Repositories\yggdrasil`) runs every repository's checks from its `yggdrasil.yml`.
  As of today:
  - a check's container gets no branch name and runs on pull requests as well as pushes;
  - a check may only bind credentials its catalog entry allows, and never a forge token (ids starting with
    `forge-` or `github-` are refused);
  - only the publish agent holds the forge write token;
  - a check's `archive` can be handed to a later step (`deploy.inputs` does this for a deploy).

  **Nothing in yggdrasil can push to another repository today.** Goal 3 needs a yggdrasil change; see "The copy".
- The forge is Forgejo at git.techcraftsmen.net with a read-only GitHub mirror. Links to source on GitHub keep
  working through the mirror.
- heimdall-api reaches `main` only through a release (`release/x.y.z` → `main`, merged by Jenkins after the
  production deploy). heimdall-ui likewise.

## What gets built

### 1. The copy (yggdrasil, heimdall-api, heimdall-ui)

A new, optional section in a repository's `yggdrasil.yml` that says what to copy into which repository. The shape
below shows the intent; the field names and validation follow yggdrasil's conventions and are the builder's:

```yaml
# heimdall-api/yggdrasil.yml
sync:
  repository: heimdall-docs            # a repository of the catalog
  inputs: [test]                       # checks whose archives are copied (the coverage report)
  paths:                               # what is copied, from where to where
    - { from: docs/coverage-report, to: static/api/coverage-report }   # from the `test` archive
    - { from: docs/openapi/heimdall.json, to: static/api/openapi/heimdall.json }
    - { from: docs/requirements, to: content/en/docs/api/requirements/documents }
```

```yaml
# heimdall-ui/yggdrasil.yml
sync:
  repository: heimdall-docs
  paths:
    - { from: docs/requirements, to: content/en/docs/application/requirements/documents }
```

Behaviour:

- It runs **only on a push to `main`** of the source repository, after that build's checks have passed, never on a
  pull request or another branch. The checks named in `inputs` run on that build even if their result could be
  reused (as `deploy.inputs` does today), because their archive is needed.
- The commit and push are done by a yggdrasil script on the **publish agent**, the agent that already holds the
  forge write token. **No repository code ever runs with the token**: the agent clones the target, replaces each
  `to` path wholesale with its `from` (so deletions propagate), commits, and pushes to the target's `main`. Nothing
  outside the listed `to` paths is touched.
- It commits only when something changed. The commit message names the source repository, its version tag (or
  commit) and what changed, as a lowercase Conventional Commits subject, for example
  `docs: sync heimdall-api v4.3.0 artifacts`.
- A rejected push (heimdall-docs' `main` moved meanwhile) is retried on a fresh clone a few times, then fails
  the build loudly. A failed sync fails the build of `main` but never undoes the release that preceded it.
- The push to heimdall-docs' `main` triggers heimdall-docs' usual build: its `build` check, then the production
  deploy. If the copied content breaks the site check, heimdall-docs' build fails and the site stays as it was.
- `scripts/pipeline_config.py` validates the section: the target is a repository of the catalog, every `inputs`
  entry is a check with an `archive`, every `to` is a relative path inside the target with no `..`.

With this in place, the `heimdall-api-docs` catalog entry, `stacks/heimdall-api-docs.yml`, `docs.Dockerfile`,
`docs.Dockerfile.dockerignore` and `deploy.inputs: [test]` are deleted. The `test` check keeps archiving
`docs/coverage-report/**` (now for the sync).

**Rejected alternative:** a check in heimdall-api that clones heimdall-docs and pushes, with a heimdall-docs token
as its credential. It cannot tell `main` from a pull request, and it hands the token to every branch's code (anti-
goal 1). yggdrasil also refuses forge credentials for checks.

### 2. The site (heimdall-docs)

Navigation after the move (my call on the exact layout; the builder may adjust names and weights):

| Section | Content |
|---|---|
| Overview | heimdall-docs' overview, merged with the API site's overview (domain vocabulary and rules) |
| Architecture | heimdall-docs' architecture, merged with the API site's architecture and **domain model** |
| Installation | heimdall-docs' installation, merged with the API README's Configure / Email delivery / Google Sign-In / Migrations / Run / Deploy with Docker (container start-up, metrics, the host's PostgreSQL, naming the login) and the API site's getting started and environments and deployment |
| User guide | unchanged |
| Integrating | unchanged |
| **API** (replaces "API documentation") | API reference; API Explorer (Swagger UI on `static/api/openapi/heimdall.json`); flows (the eight pages); operations; use case status (a link to the API README's tracker); test coverage (link to `static/api/coverage-report/`); requirements (index page + the copied documents) |
| **Application** (new) | what the UI README teaches: prerequisites, install, configure (target scope, environments), run, build, container image (web), use case status (a link to the UI README's tracker); requirements (index page + the copied documents) |
| Repositories | unchanged, plus links to each repository's CHANGELOG and CONTRIBUTING |
| About | unchanged |

- **Changelog and contributing are not shown on the site** (they stay in each repository); the site links to
  them on GitHub. This replaces the API site's `repo-file` shortcode, which is not ported.
- **Requirements pages.** Each `requirements/` section has a hand-written `_index.md` (the API one is the API
  site's existing index, adjusted; the UI one is new) and a `documents/` folder that only the sync writes. The
  copied files are rendered as they are, without front matter, as the API site does today. A `render-link` hook
  (ported from the API site) turns sibling `.md` links into page links and source links (`../src/`, `../lib/`,
  `../tests/`, `../test/`, `../scripts/`, `../tool/`) into GitHub links **of the repository the document came
  from**, so the hook must know which section it is in.
- **Overlap rule.** Where the API site and heimdall-docs both cover a topic, the merged page keeps the more
  precise statement and the builder notes any contradiction in the pull request for the owner to settle. Facts are
  checked against the code, as `docs/fact-sheet.md` did for the original site.
- **Diagrams.** The API pages use Mermaid with `useMaxWidth: false` and a scrolling container
  (`_styles_project.scss`); heimdall-docs already configures this for Docsy v0.15.0. The builder carries over any
  style the moved diagrams need.
- **Swagger UI** loads as on the API site; the builder confirms it works under Docsy v0.15.0.
- `scripts/required_pages.txt` gains the new pages, and the site check must pass with the copied content in place.
- **First content.** The first copy of the coverage report, OpenAPI document and requirements goes in by hand
  (from the current `main` of each repository) with the site change, so the site is complete before the first
  sync runs. `.gitattributes` keeps `heimdall.json` at LF as heimdall-api does.

### 3. The code repositories

**heimdall-api:**

- Delete `docs/hugo.toml`, `docs/content/`, `docs/layouts/`, `docs/assets/`, `docs/archetypes/`, `docs/i18n/`,
  `docs/package.json`, `docs/package-lock.json`, `docs/prompts/` (if nothing still uses it; the builder checks),
  `docs.Dockerfile`, `docs.Dockerfile.dockerignore`, and the untracked `docs/themes/` (a leftover from when
  Docsy was a git submodule). Remove `deploy.inputs` from `yggdrasil.yml` and add the `sync` section.
- Keep `docs/requirements/`, `docs/superpowers/`, `docs/openapi/heimdall.json` (it is generated and checked here),
  and `docs/coverage-report/` as the generated, ignored output of `scripts/coverage.py`.
- README: stays as it is, every section included (owner's decision, 2026-11-02), with a link to the docs site
  added near the top. Its use case status tracking is ticked after each merged use case by the Development
  Workflow Document and the implement-use-case skill; the site's use case status pages link to it instead of
  copying it. Configure, run and deploy are therefore written in both the README and the site; this overrides
  anti-goal "two sources for the same page" for those sections.
- Update text that names the old site or the removed files: `scripts/openapi.py`, `scripts/coverage.py`,
  `ci/test.sh`, `ci/check.sh`, `SwaggerConfiguration.cs`, `Startup.cs`, `CONTRIBUTING.md`, `api-client/README.md`,
  `.gitignore`, `.gitattributes`, the implement-use-case skill's `references/repo-patterns.md` (both copies), and
  the `docker/*.env.example` files. A new CHANGELOG entry records the move. Old CHANGELOG entries and old specs and
  plans are history and stay as written.

**heimdall-ui:**

- README kept as it is, with a link to the docs site, as above. Add the `sync` section to `yggdrasil.yml`.
- `lib/features/privacy/domain/privacy_notice.dart` links readers to the requirements on heimdall-api's GitHub; it
  keeps doing so (the file is still there).

**heimdall-docs:** its own README's description ("The API's internals live on the heimdall-api site"), the site's
`hugo.toml` links (`API site` menu entry, `params.links.user`) and the `repositories` page are updated.

**yggdrasil:** the `sync` feature (code, `docs/catalog.md`, tests), the catalog change (remove `heimdall-api-docs`),
the deleted stack file, and whatever credential or access the publish agent's account needs on heimdall-docs.

### Old addresses

docs.artur-rios.tech/heimdall-api/... stops being served. My call: redirect it, so the links in old CHANGELOG
entries, specs, plans and anywhere else keep working. A Traefik redirect from `/heimdall-api/<page>` to the
matching heimdall-docs page where one exists, and to `/heimdall-docs/docs/api/` otherwise. It lives in yggdrasil's
proxy stack files (see "Order of work").

## Order of work

Settled after the review (my calls):

- The publish agent's account (`jenkins`) is already a write collaborator on every repository, so no new access
  is needed on heimdall-docs.
- The coverage report embeds its generation time, so every heimdall-api release makes a sync commit. Accepted.
- The commit message takes the version from the release merge's title.
- The first hand copy of the coverage report comes from the last Jenkins archive of the `test` check.
- The redirect is a Traefik router in yggdrasil's `stacks/*.proxy.yml` (taken from yggdrasil's `main`), not in
  heimdall-docs. It can only go live once the API site stops answering on `/heimdall-api`.
- Pipelines run the yggdrasil library at `YGGDRASIL_LIBRARY_VERSION` (the controller's `platform.env`, applied
  with `platform.sh up`). A `yggdrasil.yml` with a `sync` section fails validation until Jenkins runs a library
  that knows it.

Order:

1. **yggdrasil:** the `sync` feature, with tests. Released, and Jenkins moved to that release (operator step).
2. **heimdall-docs:** the moved and merged pages, the Application section, the render hook, and the first hand
   copy of the artifacts. Deployed. The API site still exists meanwhile, so nothing is lost.
3. **yggdrasil:** remove `heimdall-api-docs` from the catalog and its stack, and add the redirect router. Then the
   operator steps: compose down `heimdall-api-docs-production` on the VPS (removing it from the catalog does not
   stop it) and remove its Jenkins job. This lands **before** any heimdall-api release without `docs.Dockerfile`,
   or that job's next deploy breaks.
4. **heimdall-api and heimdall-ui:** the `sync` sections, the trimmed READMEs, the deleted site files, then a
   release of each, which runs the first sync (operator step).

Each step is developed and its pull request opened in turn (owner's decision); the operator steps are the owner's.
Each code step is its own pull request in its own repository, following that repository's workflow (heimdall-api
and heimdall-ui merge into `develop` and reach `main` by release; heimdall-docs and yggdrasil as they do today).
The plan also produces a short runbook for the operator steps, with a check after each.

## Left to the builder

- The `sync` section's exact field names, validation messages and retry count.
- Page names, weights and how the merged pages are split.
- Whether Swagger UI and the moved Mermaid diagrams need any change for Docsy v0.15.0, and whether that is
  worth moving the Docsy pin (only with the README's verified procedure).
