# Centralized docs site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** heimdall-docs holds everything the heimdall-api site shows today, plus an Application section for
heimdall-ui and both repositories' requirements, so the API site can be retired in step 3.

**Architecture:** The API site's pages move into heimdall-docs' Hugo/Docsy (v0.15.0) site.
- **Where the pages go:**
  - Where heimdall-docs already covers a topic (Overview, Architecture, Installation), the API page is merged in,
    or becomes a child page of that section.
  - Everything API-specific goes into a new `docs/api/` section, which replaces today's page of links.
  - A new `docs/application/` section covers heimdall-ui.
- **Copied artifacts:** the coverage report, the OpenAPI document and both repositories' requirements are copied
  in by hand once, at the paths the yggdrasil `sync` will own afterwards. The site's own pages never live under
  those paths.

**Tech Stack:** Hugo extended 0.158+ (0.165 locally), Docsy v0.15.0 as a Hugo Module, Python 3.11+ for
`scripts/check_site.py`.

**Spec:** `docs/superpowers/specs/2026-11-02-centralized-documentation-design.md` (committed in Task 1). This
plan is the spec's step 2, "The site (heimdall-docs)".

## Global Constraints

- Sync-owned paths are written only by the copy, never by hand-written pages:
  - `static/api/coverage-report/` (from heimdall-api `docs/coverage-report`)
  - `static/api/openapi/heimdall.json` (from heimdall-api `docs/openapi/heimdall.json`)
  - `content/en/docs/api/requirements/documents/` (from heimdall-api `docs/requirements`)
  - `content/en/docs/application/requirements/documents/` (from heimdall-ui `docs/requirements`)

  Nothing else goes in these folders: no `_index.md`, and no file they would not get from the source.
- The first copies come from each repository's `origin/main`: heimdall-api `82f7d353` (v4.2.0), heimdall-ui
  `82219b7` (v1.10.0). The coverage report's source is decided by the owner (see Task 1).
- Docsy stays pinned at v0.15.0. Mermaid stays configured through `params.mermaid`, as `hugo.toml` does today.
- CHANGELOG and CONTRIBUTING are not rendered on the site. Pages link to them on GitHub
  (`https://github.com/artur-rios/<repo>/blob/main/<file>`).
- Use case status is not copied. The API and Application sections each link to the tracker in their repository's
  README (`https://github.com/artur-rios/<repo>#use-case-status`).
- No link to `docs.artur-rios.tech/heimdall-api` remains anywhere on the site. Internal links are relative, or go
  through `relURL`/`relref`, so the site works under any `PUBLIC_PATH`.
- Overlap rule: when the API site and heimdall-docs both state a fact, keep the more precise statement. When they
  contradict, check the code (heimdall-api / heimdall-ui at the commits above), keep what it says, and list each
  contradiction in the pull request body.
- The site check must pass: `hugo --minify 2>&1 | tee hugo.log && python scripts/check_site.py --public public --build-log hugo.log`.
  So must its own tests: `python -m unittest discover -s scripts -p "test_*.py"`.
- Branch `feature/centralized-docs` from `main`, with a pull request into `main` (heimdall-docs is `rules: basic`;
  merging deploys production). Lowercase Conventional Commits. No `TODO`/`TBD`/`FIXME` (the checker refuses them).

## Review Focus

1. A link in a copied requirements document to a sibling document (`Technology%20Stack%20Document.md`) or to
   source (`../src/...`, `../lib/...`, `../test/...`) must resolve: a sibling becomes its page, and source becomes
   a GitHub link **to the repository the document came from**. (Task 1: render-hook tests through the site check
   on both requirements sets.)
2. The API explorer must load the OpenAPI document under the site's real base path, not `/heimdall-api/` and not
   a hard-coded `/heimdall-docs/`. (Task 2: the built page's script URL is checked to start with the base path.)
3. A moved page that linked `../contributing/` or `../changelog/` (pages that no longer exist) must point to the
   GitHub file instead. (Task 2: the site check refuses dead internal links; `grep` for `contributing/` and
   `changelog/` in `content/` finds no relative link.)
4. The coverage report's own HTML has hundreds of internal links, and the site check must accept it as it is.
   (Task 1: the site check passes with the report in `static/`.)
5. Wide Mermaid diagrams from the moved pages (the domain-model class diagram is about 2570 px wide) must scroll
   rather than shrink. (Task 3: the existing `pre.mermaid` styles cover them; checked visually in the built page.)

---

### Task 1: Plumbing, copied artifacts, the spec

**Files:**
- Create: `layouts/_markup/render-link.html`, `layouts/_shortcodes/swagger-ui.html`
- Create (copies): `static/api/openapi/heimdall.json`, `static/api/coverage-report/**`,
  `content/en/docs/api/requirements/documents/*.md`, `content/en/docs/application/requirements/documents/*.md`
- Modify: `hugo.toml`, `assets/scss/_styles_project.scss`, `.gitattributes`, `scripts/required_pages.txt`
- Add: `docs/superpowers/specs/2026-11-02-centralized-documentation-design.md` and this plan (both already in
  the working tree, untracked)

**Interfaces:**
- Produces:
  - **`render-link.html`**, ported from heimdall-api `docs/layouts/_markup/render-link.html` with one change: the
    GitHub repository for source links is chosen by the page's path. A page under `docs/api/` maps to
    `https://github.com/artur-rios/heimdall-api`, and a page under `docs/application/` maps to
    `https://github.com/artur-rios/heimdall-ui`. Branch `main`.
    - Source prefixes: `../src/`, `../tests/`, `../scripts/`, `../lib/`, `../test/`, `../tool/`, `../api-client/`.
    - Any other page keeps today's behaviour, passing the link through untouched.
  - **`{{< swagger-ui >}}`** emits the API site's Swagger UI block: the same pinned `swagger-ui-dist@5.32.13`
    CSS and JS with the same SRI hashes, and the same options. Its `url` is `"api/openapi/heimdall.json" | relURL`.
  - **Swagger styles:** the `.heimdall-swagger` rules move from heimdall-api `docs/assets/scss/_styles_project.scss`
    into heimdall-docs' stylesheet, with any other rule the moved pages need (diagram and table rules that
    heimdall-docs lacks).

- [ ] **Step 0: Branch** with `git switch -c feature/centralized-docs` from an up-to-date `main`. (The controller
  may already have done this.)
- [ ] **Step 1: Copy the artifacts.**
  - Run `git -C ../heimdall-api show 82f7d353:docs/openapi/heimdall.json > static/api/openapi/heimdall.json`.
  - Copy the requirements trees from `git -C <repo> archive <commit> docs/requirements`, so that each target
    folder holds exactly the source folder's files.
  - Copy the coverage report from the source the owner chose.
  - Add `static/api/openapi/heimdall.json text eol=lf` to `.gitattributes`.
- [ ] **Step 2: Build once** with `hugo --minify 2>&1 | tee hugo.log`, then run the checker. Expected: it fails,
  naming the requirements' broken sibling and source links. That failure is the red state for the render hook.
- [ ] **Step 3: Add `render-link.html`.** Rebuild and recheck. Expected: no requirements link errors. Spot-check
  one source link in each set: an API document links to `github.com/artur-rios/heimdall-api/blob/main/src/...`,
  and a UI document links to `github.com/artur-rios/heimdall-ui/blob/main/lib/...`.
- [ ] **Step 4: Add the shortcode and styles.** Update `hugo.toml`:
  - Drop the `API site` menu entry and the `API documentation` `params.links.user` entry.
  - Point the `GitHub` menu entry at the heimdall-docs repository.
- [ ] **Step 5: Add the requirements pages and the coverage report to `scripts/required_pages.txt`.**
  - Requirements: `docs/api/requirements/documents/vision-document/` and
    `docs/application/requirements/documents/vision-document/`.
  - Coverage report: add it if the checker's format allows a static file; otherwise rely on the link from Task 2's
    page.
  - Run the full site check and the checker's tests. Expected: pass.
- [ ] **Step 6: Commit.** Commit as
  `git commit -m "docs: copy the api and ui artifacts and add their render hooks"`, including the spec and plan
  files.

### Task 2: The API section

**Files:**
- Replace: `content/en/docs/api/_index.md`, which becomes the section landing page: what the API is and a map of
  its pages.
- Create these pages, moved from heimdall-api `docs/content/en/docs/` at `82f7d353`:
  - `content/en/docs/api/reference.md`, from `api-reference.md`
  - `content/en/docs/api/explorer.md`, from `api-explorer.md`, using `{{< swagger-ui >}}`
  - `content/en/docs/api/flows/_index.md` and the eight flow pages
  - `content/en/docs/api/operations.md`
  - `content/en/docs/api/test-coverage.md`, a short page linking `static/api/coverage-report/` and explaining that
    CI regenerates the report on every release
  - `content/en/docs/api/use-case-status.md`, a short page linking the heimdall-api README tracker
  - `content/en/docs/api/requirements/_index.md`, the API site's requirements index, adjusted so its table links
    resolve to `documents/<slug>/`
- Modify: `scripts/required_pages.txt`

- [ ] **Step 1: Move the pages.**
  - Rewrite every link that pointed into the API site so it points to the new location. That includes
    `../contributing/` and `../changelog/`, which become GitHub links (see Global Constraints), and
    `/heimdall-api/...`.
  - Keep each page's substance. Adjust only wording that describes "this site" as the API site.
- [ ] **Step 2: Add every new page to `required_pages.txt`.** Build and check. Expected: pass.
- [ ] **Step 3: Check the explorer's URL.** Build with `--baseURL https://example.test/sub/` into a scratch
  folder. The built `docs/api/explorer/index.html` must reference `/sub/api/openapi/heimdall.json`.
- [ ] **Step 4: Commit** with `git commit -m "docs: move the api site's pages into an api section"`.

### Task 3: Merge into Overview, Architecture and Installation

**Files:**
- Modify: `content/en/docs/overview/_index.md`, merging the API site's `overview.md` (domain vocabulary and rules).
- Modify: `content/en/docs/architecture/_index.md`, merging the API site's `architecture.md` (four layers, CQRS
  mediator, auditing decorator, HTTP pipeline).
- Create: `content/en/docs/architecture/domain-model.md`, from the API site's `domain-model.md`.
- Modify: `content/en/docs/installation/_index.md` ("Running the API"), merging the API site's
  `getting-started.md` and the heimdall-api README's Configure, Email delivery, Google Sign-In, Migrations, Run
  and Deploy with Docker sections (container start-up, metrics, the host's PostgreSQL, naming the login), wherever
  the page lacks them.
- Create: `content/en/docs/installation/environments-and-deployment.md`, from the API site's page. The short
  "Environments" section of the installation page links to it.
- Modify: `scripts/required_pages.txt`

- [ ] **Step 1: Merge.** Apply the overlap rule in Global Constraints, and record each contradiction with its
  resolution in `docs/superpowers/plans/2026-11-02-centralized-docs-site-contradictions.md`, which the pull
  request body will quote.
- [ ] **Step 2: Fix every link into the merged pages** across the site, including the Task 2 pages that pointed
  to `../overview/`, `../architecture/`, `../domain-model/`, `../getting-started/` and
  `../environments-and-deployment/`.
- [ ] **Step 3: Build and check.** Expected: pass. Open the built domain-model page and confirm the class diagram
  scrolls horizontally at full size.
- [ ] **Step 4: Commit** with `git commit -m "docs: merge the api site's overview, architecture and setup pages"`.

### Task 4: The Application section

**Files:**
- Create: `content/en/docs/application/_index.md`, covering what heimdall-ui is and its platforms.
  - It covers what the heimdall-ui README teaches that `installation/_index.md` ("Running the UI") does not
    already say: the target scope, the environments table, the build matrix and the web container image.
  - Where the installation page already says something, the section links to it instead of repeating it.
- Create: `content/en/docs/application/use-case-status.md`, linking the heimdall-ui README tracker.
- Create: `content/en/docs/application/requirements/_index.md`, an index table of the seven UI documents in the
  style of the API one.
- Modify: `scripts/required_pages.txt`

- [ ] **Step 1: Write the pages from heimdall-ui at `82219b7`** (its README and the requirements' front matter).
- [ ] **Step 2: Build and check.** Expected: pass.
- [ ] **Step 3: Commit** with `git commit -m "docs: add an application section for heimdall-ui"`.

### Task 5: The rest of the site, and the pull request

**Files:**
- Modify: `content/en/docs/repositories/_index.md`.
  - Bring its facts up to date with the repositories: latest releases, the default branches, Forgejo as the home
    with GitHub as a mirror, and Jenkins instead of a Pages workflow.
  - Link each repository's CHANGELOG and CONTRIBUTING.
  - Say that the requirements are shown on this site, copied from each repository on release.
- Modify: `content/en/_index.md` and `content/en/about/_index.md`, removing any mention of the API site.
- Modify: `README.md` (heimdall-docs).
  - Remove "The API's internals live on the heimdall-api site".
  - Describe the sync-owned paths and that they must not be edited by hand.
  - Update the Layout tree.

- [ ] **Step 1: Make the edits.**
- [ ] **Step 2: Check the whole site.** Run `grep -rn "heimdall-api/" content README.md hugo.toml`. Expected: only
  GitHub URLs remain. Then run the full site check and the checker's tests. Expected: pass.
- [ ] **Step 3: Commit** with `git commit -m "docs: point the rest of the site at its new sections"`.
- [ ] **Step 4: Push and open the pull request.**
  - Run `git push -u origin feature/centralized-docs`, then
    `tea pulls create --repo artur-rios/heimdall-docs --base main --head feature/centralized-docs`.
  - Title: `docs: centralize the heimdall documentation`.
  - The body says what moved where and quotes the contradictions file. It notes that merging deploys production,
    and that the old API site keeps running until step 3 (yggdrasil). It ends with the Claude Code attribution line.
