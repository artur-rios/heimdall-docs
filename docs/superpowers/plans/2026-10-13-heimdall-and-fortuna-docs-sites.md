# Heimdall and Fortuna documentation sites — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, verify and publish on GitHub Pages two Hugo + Docsy sites —
`heimdall-docs` and `fortuna-docs` — that are the home page and documentation
source for the Heimdall and Fortuna projects.

**Architecture:** Each site is its own repository, structured exactly like
`D:\Repositories\alexandria-docs` (Docsy v0.15.0 as a Hugo Module, PostCSS via
npm, Mermaid, offline search, light/dark toggle, `content/en/`), deployed by a
GitHub Actions workflow to GitHub Pages. A stdlib-only Python checker,
`scripts/check_site.py`, is each site's test: it fails the build on missing
pages, broken internal links or anchors, unexpected Hugo warnings, and
placeholder text. Content is written from cited fact sheets committed as
`docs/fact-sheet.md`, which are themselves drawn from the code repositories.

**Tech Stack:** Hugo extended 0.165.0 (min 0.158.0), Go 1.26.7, Docsy v0.15.0,
Node 24 + npm (autoprefixer, postcss, postcss-cli), Mermaid 11.17.2 (CDN),
swagger-ui-dist 5.32.13 (CDN, Fortuna only), Python 3 stdlib, GitHub Actions,
GitHub Pages, `gh` CLI.

**Specs:**
- `D:\Repositories\heimdall-docs\docs\superpowers\specs\2026-10-13-heimdall-docs-site-design.md`
- `D:\Repositories\fortuna-docs\docs\superpowers\specs\2026-10-13-fortuna-docs-site-design.md`

This plan is committed identically to both repositories.

## Global Constraints

- Published on **GitHub Pages**: `https://artur-rios.github.io/heimdall-docs/` and `https://artur-rios.github.io/fortuna-docs/`; Pages source = **GitHub Actions**.
- GitHub repositories `artur-rios/heimdall-docs` and `artur-rios/fortuna-docs`: **public**, default branch **`main`**; initial site pushed directly to `main`.
- Docsy **v0.15.0** as a Hugo Module, pinned (v0.16.0 resolves but builds no output).
- Hugo extended, `module.hugoVersion.min = "0.158.0"`; CI `HUGO_VERSION: 0.165.0`.
- Mermaid pinned to **11.17.2** via `params.mermaid.version` (Docsy v0.15's loader predates Mermaid 12).
- Content under `content/en/`; English only.
- **Correctness rule:** every factual claim sourced from the code repositories (READMEs, changelogs, `docs/initial/`, `docs/requirements/`, OpenAPI, workflows, releases) or the heimdall-api site. Nothing invented. Unverifiable → link to the source instead of asserting.
- Heimdall portal **links into** `https://artur-rios.github.io/heimdall-api/` for API internals and never copies them.
- Fortuna API explorer loads `https://raw.githubusercontent.com/artur-rios/fortuna-api/main/docs/openapi/fortuna.json` at view time; "Try it out" and "Authorize" disabled.
- License: Artur Rios Attribution License (already committed in both repos); footer must not say "All Rights Reserved".
- Commits: lowercase Conventional Commits subject ≤ 50 chars, body wrapped at 72, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Links inside content: always relative (`../installation/`) or Hugo `relref`; never root-absolute `/docs/...` (the site lives under a sub-path).

## Review Focus

1. **Sub-path links** — a root-absolute link such as `/docs/overview/` works nowhere because the site is served under `/heimdall-docs/`; expected: the checker rejects it. Pinned by `test_root_absolute_link_outside_base_path_fails` (Task 1).
2. **Stale or invented facts** — a version, command, env var or use case that does not match the code repositories; expected: every page passes a fact-check against its sources. Pinned by the "fact-check" step in every content task.
3. **Dark mode** — Mermaid diagrams, landing bands and the Swagger explorer unreadable in dark mode; expected: legible in both modes. Pinned by Task 15's light/dark screenshots.
4. **Phone width** — wide tables and diagrams pushing the page sideways at 375px; expected: they scroll inside their own box. Pinned by Task 15's mobile pass (`document.documentElement.scrollWidth <= innerWidth`).
5. **Explorer source unavailable** — `fortuna.json` moved or GitHub raw unreachable; expected: the page still tells the reader where the document is. Pinned by Task 13's visible link to the raw document above the widget.

---

## File map

Both repositories end up with this layout (Fortuna differences marked):

```txt
<repo>/
├── .github/workflows/deploy.yml     # build on PR; build + deploy to Pages on main
├── .gitignore
├── README.md                        # what the repo is, run locally, layout, theme pin, deployment
├── LICENSE                          # exists
├── .wakatime-project                # exists
├── go.mod / go.sum                  # Docsy v0.15.0
├── package.json / package-lock.json # PostCSS toolchain
├── hugo.toml
├── i18n/en.toml                     # hide "All Rights Reserved"
├── assets/scss/_styles_project.scss # diagrams, dark bands, wide tables (+ Swagger in Fortuna)
├── scripts/check_site.py            # the site's test
├── scripts/test_check_site.py       # the checker's own tests
├── scripts/required_pages.txt       # pages that must be built
├── docs/fact-sheet.md               # cited facts the content is written from
├── docs/superpowers/{specs,plans}/
└── content/en/
    ├── _index.md                    # landing page
    ├── about/_index.md
    └── docs/_index.md + one folder per section (see Tasks 3–7, 9–14)
```

Paths below: `H` = `D:\Repositories\heimdall-docs`, `F` = `D:\Repositories\fortuna-docs`,
`SCRATCH` = the session scratchpad holding `heimdall-facts.md` and `fortuna-facts.md`.

---

### Task 1: Site checker (both repos)

**Files:**
- Create: `H/scripts/check_site.py`, `H/scripts/test_check_site.py`
- Create (identical copies): `F/scripts/check_site.py`, `F/scripts/test_check_site.py`

**Interfaces:**
- Produces: `python scripts/check_site.py --public public --build-log hugo.log [--content content] [--required scripts/required_pages.txt] [--base-url URL]` → exit 0 when clean, 1 with one `ERROR:` line per problem. `--base-url` defaults to `baseURL` in `hugo.toml`.
- Functions: `check_pages(public: Path, base_url: str, required: list[str]) -> list[str]`, `check_build_log(text: str) -> list[str]`, `check_content(content: Path) -> list[str]`, `main(argv: list[str] | None = None) -> int`.

- [ ] **Step 1: Write the failing tests** — `H/scripts/test_check_site.py`:

```python
"""Tests for check_site.py. Run: python -m unittest discover -s scripts -p "test_*.py" """
import tempfile
import unittest
from pathlib import Path

import check_site

BASE = "https://artur-rios.github.io/demo-docs/"


def write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


class CheckPagesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.public = Path(self.tmp.name)
        write(self.public, "index.html",
              '<a href="/demo-docs/docs/">Docs</a>'
              '<a href="docs/#intro">Intro</a>'
              '<a href="https://github.com/x">ext</a>'
              '<a href="mailto:a@b.c">mail</a><a href="#">top</a>')
        write(self.public, "docs/index.html", '<h2 id="intro">Intro</h2><a href="../">home</a>')

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_site_passes(self):
        self.assertEqual(check_site.check_pages(self.public, BASE, ["", "docs/"]), [])

    def test_missing_required_page_fails(self):
        errors = check_site.check_pages(self.public, BASE, ["docs/usage/"])
        self.assertEqual(len(errors), 1)
        self.assertIn("docs/usage/", errors[0])

    def test_broken_internal_link_fails(self):
        write(self.public, "docs/index.html", '<h2 id="intro">x</h2><a href="missing/">x</a>')
        errors = check_site.check_pages(self.public, BASE, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("docs/missing/", errors[0])

    def test_root_absolute_link_outside_base_path_fails(self):
        write(self.public, "docs/index.html", '<h2 id="intro">x</h2><a href="/docs/">x</a>')
        errors = check_site.check_pages(self.public, BASE, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("outside the site", errors[0])

    def test_broken_fragment_fails(self):
        write(self.public, "index.html", '<a href="docs/#nope">x</a>')
        errors = check_site.check_pages(self.public, BASE, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("#nope", errors[0])

    def test_absolute_url_on_own_host_is_checked(self):
        write(self.public, "index.html", f'<a href="{BASE}docs/gone/">x</a>')
        errors = check_site.check_pages(self.public, BASE, [])
        self.assertEqual(len(errors), 1)

    def test_other_site_on_same_host_is_external(self):
        write(self.public, "index.html", '<a href="https://artur-rios.github.io/heimdall-api/docs/">x</a>')
        self.assertEqual(check_site.check_pages(self.public, BASE, []), [])


class CheckBuildLogTests(unittest.TestCase):
    def test_known_docsy_deprecations_pass(self):
        log = ("WARN  deprecated: .Language.LanguageDirection was deprecated in Hugo v0.158.0\n"
               "WARN  deprecated: .Site.AllPages was deprecated in Hugo v0.156.0\n"
               "Total in 900 ms\n")
        self.assertEqual(check_site.check_build_log(log), [])

    def test_other_warning_fails(self):
        self.assertEqual(len(check_site.check_build_log("WARN  found no layout file\n")), 1)

    def test_error_fails(self):
        self.assertEqual(len(check_site.check_build_log("ERROR render failed\n")), 1)


class CheckContentTests(unittest.TestCase):
    def test_placeholder_text_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "en/docs/a.md", "Install it.\n\nTODO: write the rest\n")
            errors = check_site.check_content(Path(tmp))
            self.assertEqual(len(errors), 1)
            self.assertIn("a.md", errors[0])

    def test_clean_content_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            # "to-do list" is UI prose, not a placeholder marker.
            write(Path(tmp), "en/docs/a.md", "Keep a to-do list of what to read next.\n")
            self.assertEqual(check_site.check_content(Path(tmp)), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd H && python -m unittest discover -s scripts -p "test_*.py"`
Expected: `ModuleNotFoundError: No module named 'check_site'`.

- [ ] **Step 3: Write the checker** — `H/scripts/check_site.py`:

```python
#!/usr/bin/env python3
"""Checks a built Hugo site before it is published.

It fails when:

1. a page listed in scripts/required_pages.txt was not built;
2. an internal link or asset does not resolve to a built file, points
   outside the site's base path, or names an #anchor the target page
   does not have;
3. the Hugo build log holds a warning or error other than the two
   deprecations Docsy v0.15.0 triggers under current Hugo;
4. the content still holds placeholder text (TODO, TBD, FIXME).

Usage:
    hugo --minify 2>&1 | tee hugo.log
    python scripts/check_site.py --public public --build-log hugo.log
"""
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

# Docsy v0.15.0's templates call two APIs Hugo has since deprecated. They
# are warnings, not failures, and go away when the Docsy pin can be lifted
# (see the readme). Anything else Hugo warns about is a real problem.
KNOWN_DOCSY_WARNINGS = (
    "deprecated: .Language.LanguageDirection",
    "deprecated: .Site.AllPages",
)

PLACEHOLDER = re.compile(r"\b(TODO|TBD|FIXME)\b|lorem ipsum", re.IGNORECASE)
LINK_TAGS = {"a", "link", "img", "script", "source", "iframe"}
SKIPPED_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value for name, value in attrs if value}
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "a" and "name" in attributes:
            self.ids.add(attributes["name"])
        if tag in LINK_TAGS:
            for name in ("href", "src"):
                if name in attributes:
                    self.links.append(attributes[name])


def _parse(path: Path, cache: dict[Path, _Page]) -> _Page:
    if path not in cache:
        page = _Page()
        page.feed(path.read_text(encoding="utf-8", errors="replace"))
        cache[path] = page
    return cache[path]


def _target_file(public: Path, rel: str) -> Path:
    target = public / rel
    if rel == "" or rel.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def check_pages(public: Path, base_url: str, required: list[str]) -> list[str]:
    errors: list[str] = []
    base = urlsplit(base_url)
    base_path = base.path if base.path.endswith("/") else base.path + "/"
    cache: dict[Path, _Page] = {}

    for rel in required:
        if not _target_file(public, rel).is_file():
            errors.append(f"required page not built: {rel or '/'}")

    for html in sorted(public.rglob("*.html")):
        rel_page = html.relative_to(public).as_posix()
        page_url = f"{base.scheme}://{base.netloc}{base_path}{rel_page}"
        if rel_page.endswith("index.html"):
            page_url = page_url[: -len("index.html")]
        for link in _parse(html, cache).links:
            if link.startswith(SKIPPED_SCHEMES) or link in ("#", ""):
                continue
            absolute = urlsplit(urljoin(page_url, link))
            if absolute.netloc != base.netloc:
                continue
            path = unquote(absolute.path)
            if not path.startswith(base_path):
                # Same host, different path: another project's Pages site
                # unless it is a root-absolute link that forgot the sub-path.
                first = path.strip("/").split("/", 1)[0]
                if (public / first).exists() or first == "":
                    errors.append(f"{rel_page}: link {link!r} points outside the site (missing {base_path})")
                continue
            target = _target_file(public, path[len(base_path):])
            if not target.is_file():
                errors.append(f"{rel_page}: broken link {link!r} -> {path[len(base_path):]}")
                continue
            if absolute.fragment and target.suffix == ".html":
                if unquote(absolute.fragment) not in _parse(target, cache).ids:
                    errors.append(f"{rel_page}: link {link!r} names #{absolute.fragment}, which the target lacks")
    return errors


def check_build_log(text: str) -> list[str]:
    errors = []
    for line in text.splitlines():
        if line.startswith(("WARN", "ERROR")) and not any(k in line for k in KNOWN_DOCSY_WARNINGS):
            errors.append(f"hugo: {line.strip()}")
    return errors


def check_content(content: Path) -> list[str]:
    errors = []
    for md in sorted(content.rglob("*.md")):
        for number, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if PLACEHOLDER.search(line) and not re.search(r"\bto-?do (list|lists)\b", line, re.IGNORECASE):
                errors.append(f"{md.as_posix()}:{number}: placeholder text: {line.strip()}")
    return errors


def _base_url_from_config() -> str:
    with open("hugo.toml", "rb") as handle:
        return tomllib.load(handle)["baseURL"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--public", type=Path, default=Path("public"))
    parser.add_argument("--build-log", type=Path)
    parser.add_argument("--content", type=Path, default=Path("content"))
    parser.add_argument("--required", type=Path, default=Path("scripts/required_pages.txt"))
    parser.add_argument("--base-url")
    args = parser.parse_args(argv)

    required = []
    if args.required.is_file():
        required = [line.strip() for line in args.required.read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.startswith("#")]
    errors = check_pages(args.public, args.base_url or _base_url_from_config(), required)
    if args.build_log:
        errors += check_build_log(args.build_log.read_text(encoding="utf-8", errors="replace"))
    errors += check_content(args.content)

    for error in errors:
        print(f"ERROR: {error}")
    print(f"check_site: {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd H && python -m unittest discover -s scripts -p "test_*.py" -v`
Expected: 12 tests, `OK`.

- [ ] **Step 5: Copy to Fortuna and run there**

```bash
mkdir -p /d/Repositories/fortuna-docs/scripts
cp /d/Repositories/heimdall-docs/scripts/check_site.py /d/Repositories/heimdall-docs/scripts/test_check_site.py /d/Repositories/fortuna-docs/scripts/
cd /d/Repositories/fortuna-docs && python -m unittest discover -s scripts -p "test_*.py"
```
Expected: `OK`.

- [ ] **Step 6: Commit in each repo**

```bash
git add scripts/check_site.py scripts/test_check_site.py
git commit -m "test: add the built-site checker"
```

---

### Task 2: Heimdall scaffold

**Files (all in `H`):** Create `.gitignore`, `go.mod`, `go.sum`, `package.json`, `package-lock.json`, `hugo.toml`, `i18n/en.toml`, `assets/scss/_styles_project.scss`, `.github/workflows/deploy.yml`, `README.md`, `scripts/required_pages.txt`, `docs/fact-sheet.md`, `content/en/_index.md`, `content/en/docs/_index.md`.

**Interfaces:**
- Consumes: `scripts/check_site.py` (Task 1).
- Produces: a building site; `scripts/required_pages.txt` that later tasks append to; the build-and-check command used by every later Heimdall task:

```bash
cd /d/Repositories/heimdall-docs && hugo --minify 2>&1 | tee "$SCRATCH/hugo-h.log" && python scripts/check_site.py --public public --build-log "$SCRATCH/hugo-h.log"
```

- [ ] **Step 1: Required pages (failing test).** `scripts/required_pages.txt`:

```txt
# Pages that must be built, relative to the site root. Later tasks append.

docs/
```

- [ ] **Step 2: Run the checker** — `python scripts/check_site.py --public public --base-url https://artur-rios.github.io/heimdall-docs/` → FAIL (`required page not built: /` … no `public/`).

- [ ] **Step 3: Toolchain files.**
  - `.gitignore` — copy `D:\Repositories\alexandria-docs\.gitignore` verbatim.
  - `go.sum` — copy `D:\Repositories\alexandria-docs\go.sum` verbatim (same module graph).
  - `go.mod`:
    ```txt
    module github.com/artur-rios/heimdall-docs

    go 1.26.7

    // Pinned: v0.16.0 moved Docsy's layouts/assets into a submodule the Hugo
    // Module zip omits, so it resolves but builds no output.
    require github.com/google/docsy v0.15.0 // indirect
    ```
  - `package.json` — copy alexandria's; `package-lock.json` — copy alexandria's and change both `"name": "alexandria-docs"` occurrences to `"heimdall-docs"`; then `npm ci`.
  - `i18n/en.toml` — copy alexandria's verbatim.
  - `assets/scss/_styles_project.scss` — copy `D:\Repositories\heimdall-api\docs\assets\scss\_styles_project.scss` and **delete everything from the line `// --- Swagger UI on the API explorer page` to the end of the file** (Heimdall's portal has no explorer). Keep the header, diagrams, dark bands and wide-tables sections unchanged.

- [ ] **Step 4: `hugo.toml`:**

```toml
baseURL = "https://artur-rios.github.io/heimdall-docs/"
title = "Heimdall"
# `locale`, not the deprecated `languageCode` (renamed in Hugo v0.158.0).
locale = "en-us"

enableGitInfo = false
enableRobotsTXT = true

# Docsy renders section landing pages from each section's _index.md and
# needs the section tree, so only taxonomies are excluded.
disableKinds = ["taxonomy", "term"]

[module]
  [module.hugoVersion]
    extended = true
    # `locale` and `languages.*.label` arrived in 0.158.0.
    min = "0.158.0"
  [[module.imports]]
    path = "github.com/google/docsy"

[markup]
  [markup.goldmark.renderer]
    # Docsy's shortcodes emit HTML; Goldmark drops it otherwise.
    unsafe = true
  [markup.highlight]
    # Class-based highlighting so code blocks follow the light/dark mode;
    # the per-mode stylesheets come from assets/scss/_styles_project.scss.
    noClasses = false
    lineNos = false
  [markup.tableOfContents]
    startLevel = 2
    endLevel = 3

[languages]
  [languages.en]
    label = "English"
    contentDir = "content/en"
    weight = 1
    title = "Heimdall"
    [languages.en.params]
      description = "Centralized identity management with scope-based multi-tenancy — the API and the application that drives it."

[params]
  copyright.authors = "Artur Rios | [Artur Rios Attribution License](https://github.com/artur-rios/heimdall-docs/blob/main/LICENSE)"
  github_repo = "https://github.com/artur-rios/heimdall-docs"
  github_branch = "main"
  offlineSearch = true

  [params.mermaid]
    enable = true
    # Docsy v0.15.0's loader predates Mermaid 12; "latest" would pick it up.
    version = "11.17.2"
    # Draw diagrams at natural size; the stylesheet lets wide ones scroll.
    [params.mermaid.flowchart]
      useMaxWidth = false
    [params.mermaid.sequence]
      useMaxWidth = false
    [params.mermaid.class]
      useMaxWidth = false
    [params.mermaid.state]
      useMaxWidth = false

  [params.ui]
    showLightDarkModeMenu = true
    sidebar_menu_compact = false
    sidebar_search_disable = false
    navbar_logo = false
    breadcrumb_disable = false
    [params.ui.feedback]
      enable = false

  [params.links]
    [[params.links.developer]]
      name = "heimdall-api"
      url = "https://github.com/artur-rios/heimdall-api"
      icon = "fab fa-github"
      desc = "The ASP.NET Core identity API"
    [[params.links.developer]]
      name = "heimdall-ui"
      url = "https://github.com/artur-rios/heimdall-ui"
      icon = "fab fa-github"
      desc = "The Flutter application for web, Windows, Linux and Android"
    [[params.links.developer]]
      name = "heimdall-docs"
      url = "https://github.com/artur-rios/heimdall-docs"
      icon = "fab fa-github"
      desc = "This site"
    [[params.links.user]]
      name = "API documentation"
      url = "https://artur-rios.github.io/heimdall-api/"
      icon = "fa-solid fa-book"
      desc = "The heimdall-api developer site"

# Documentation and About add themselves from their own front matter.
[[menu.main]]
  name = "API site"
  weight = 30
  url = "https://artur-rios.github.io/heimdall-api/"
  pre = "<i class='fa-solid fa-book'></i>"
[[menu.main]]
  name = "GitHub"
  weight = 50
  url = "https://github.com/artur-rios/heimdall-api"
  pre = "<i class='fab fa-github'></i>"
```

- [ ] **Step 5: Minimal content.** `content/en/_index.md` with front matter `title: Heimdall` / `linkTitle: Heimdall` and a one-line body; `content/en/docs/_index.md`:

```markdown
---
title: Documentation
linkTitle: Documentation
menu:
  main:
    weight: 10
weight: 20
description: >
  What Heimdall is, how it is put together, how to run it, and how to use it.
---
```
Body is written in Task 3.

- [ ] **Step 6: Fact sheet.** Copy `SCRATCH/heimdall-facts.md` to `docs/fact-sheet.md`, prefixed with:

```markdown
# Heimdall — fact sheet

The cited facts this site is written from, compiled 2026-10-13 from
`heimdall-api` and `heimdall-ui`. When a page and its source disagree, the
source wins: fix the page, then this file.
```

- [ ] **Step 7: Workflow.** `.github/workflows/deploy.yml` — copy `D:\Repositories\alexandria-docs\.github\workflows\deploy.yml` verbatim, then replace the two build steps and the verify step with:

```yaml
      - name: Build
        if: github.event_name != 'pull_request'
        run: hugo --minify --baseURL "${{ steps.pages.outputs.base_url }}/" 2>&1 | tee hugo.log

      - name: Build (pull request)
        if: github.event_name == 'pull_request'
        run: hugo --minify 2>&1 | tee hugo.log

      # A build that writes no output is the failure mode the Docsy pin
      # exists for, and it does not fail the Hugo command -- see the readme.
      - name: Verify the build produced a site
        run: test -s public/index.html

      - name: Test the checker
        run: python3 -m unittest discover -s scripts -p "test_*.py"

      # Required pages, internal links and anchors, unexpected Hugo
      # warnings, and placeholder text.
      - name: Check the site
        run: python3 scripts/check_site.py --public public --build-log hugo.log
```
(`set -o pipefail` is the default for `shell: bash` in Actions, so a failing `hugo` still fails the step.) The `--base-url` default is read from `hugo.toml`; on `main` the Pages base URL equals it.

- [ ] **Step 8: README.md** — adapt alexandria-docs's README: title `heimdall-docs`; one-paragraph description ("The home page and documentation portal for Heimdall … API internals live on the heimdall-api site"); live link `https://artur-rios.github.io/heimdall-docs/`; "The project" table (heimdall-api, heimdall-ui, heimdall-docs); "Running it locally" (same requirements and commands); a "Checking it" section with the build-and-check command above and `python -m unittest discover -s scripts -p "test_*.py"`; layout tree matching this repo; "Updating the theme" (copy alexandria's text — the pin rationale is identical); "Deployment" (GitHub Pages, Source = GitHub Actions).

- [ ] **Step 9: Build and check** with the command in **Interfaces**. Expected: `check_site: 0 problem(s)`, exit 0. If Hugo emits any warning other than the two known Docsy deprecations, fix the cause (do not extend the allowlist).

- [ ] **Step 10: Commit**

```bash
git add -A && git commit -m "build: scaffold the heimdall docs site"
```

---

### Tasks 3–7: Heimdall content

Every content task follows the same cycle:

1. **Append** its pages to `scripts/required_pages.txt`.
2. **Run** the build-and-check command → FAIL with `required page not built: …` for exactly those pages.
3. **Write** the pages from the listed sources (the fact sheet first, then the cited source files to confirm). Docsy shortcodes as in alexandria-docs; diagrams as ```` ```mermaid ```` fences; links relative or `relref`.
4. **Run** the build-and-check command → `0 problem(s)`.
5. **Fact-check**: re-read each page against its sources; every version, command, env var name, role, use-case number and URL must match the source verbatim. Fix and re-run step 4.
6. **Commit** with the given message.

Deep links to the API site use the URLs listed in the fact sheet's deep-link map, and only those.

### Task 3: Heimdall landing, docs index, overview, about

**Pages:** `content/en/_index.md` (rewrite), `content/en/docs/_index.md` (body), `content/en/docs/overview/_index.md`, `content/en/about/_index.md`. Append `docs/overview/` and `about/`.

**Sources:** heimdall-api `README.md` (Overview), heimdall-ui `README.md` (Overview), both Vision Documents, heimdall-api site Overview page.

**Content:**
- Landing — follow `alexandria-docs/content/en/_index.md`'s structure: `blocks/cover` (title "Heimdall", one-line pitch, "Get started" → `relref "/docs"`, "Source" → heimdall-api GitHub), `blocks/lead` (what Heimdall is in two sentences), two `blocks/section type="row"` bands of three `blocks/feature` each: scope-based multi-tenancy; persons and applications; scope permissions in the JWT; sign-in options (password, Google, two-factor); one UI on four targets; open source (licence link).
- Docs index — intro paragraph plus a table of every docs section (Overview, Architecture, Installation, User guide, Integrating a client system, API documentation, Repositories) with one line each.
- Overview — "What Heimdall is", "What it is not" (exclusions from the sources), "Concepts" (scopes; the three roles; persons; applications; scope permissions and `IncludeAsJwtClaim`; Google users; two-factor; deletion strategies — two to four sentences each, each ending with a link to the API site page that holds the full rules), "Where to go next".
- About — `blocks/cover` + `blocks/lead` (why Heimdall exists, from the Vision Document) + feature row: API (.NET), UI (Flutter), licence.

**Commit:** `docs: add the heimdall landing page and overview`

### Task 4: Heimdall architecture

**Pages:** `content/en/docs/architecture/_index.md`. Append `docs/architecture/`.

**Sources:** fact sheet §3; heimdall-api `README.md`, Technology Stack Document, Operations & Infrastructure Document, site Architecture page; heimdall-ui `README.md`, System Requirements Document, Technology Stack Document, `lib/` layout, `swagger_parser.yaml`.

**Content (four Mermaid diagrams, each followed by a short explanation):**
1. System context — client systems (Fortuna named as one, linking to `https://artur-rios.github.io/fortuna-docs/`), heimdall-ui, heimdall-api, PostgreSQL, and every external integration the sources name.
2. API layers — Domain / Application (Command, Query, Shared) / Infrastructure / Presentation; one sentence each; link to the API site's Architecture page.
3. UI architecture — the UI's structure, state management, generated API client and how the client is regenerated/checked, configuration, secure storage; as the sources state them.
4. Role-based UI — flowchart of System Admin / Scope Admin / User and what each sees, with the note that the API is the sole authority.

**Commit:** `docs: add the heimdall architecture page`

### Task 5: Heimdall installation

**Pages:** `content/en/docs/installation/_index.md`. Append `docs/installation/`.

**Sources:** fact sheet §4; heimdall-api `README.md`, `CONTRIBUTING.md`, `docker-compose.yml`, `.github/workflows/`, releases; heimdall-ui `README.md` (Prerequisites, running, building), Operations & Infrastructure Document, `.github/workflows/`, releases; API site Getting started and Environments pages.

**Content:** "Getting a release" (exactly what the workflows/releases publish, with links; if nothing is published for a target, say so and point to building from source); "Running the API" (prerequisites with versions, configuration — env var names only, Docker Compose, migrations; link to API site Getting started for the full table); "Running the UI" (Flutter version, per-target prerequisites — including Windows ATL and Linux packages exactly as the README lists them — run and build commands per target, how the UI is pointed at an API); "Environments" (one paragraph + link to the API site page).

**Commit:** `docs: add the heimdall installation guide`

### Task 6: Heimdall user guide

**Pages:** `content/en/docs/user-guide/_index.md` plus one page per group, e.g. `signing-in.md`, `your-account.md`, `scopes.md`, `persons.md`, `applications.md`, `permissions.md`, `google-users.md` — the final grouping follows the UI's Use Case Specification Document. Append each page's URL (`docs/user-guide/signing-in/`, …).

**Sources:** heimdall-ui Use Case Specification Document (UI-01 … UI-30), System Requirements Document (screen inventory, authorization matrix); fact sheet §5.

**Content:** index page with a role × page matrix (which role reaches which page). Each page: what it is for, who can reach it, then one subsection per use case — "UI-xx: name", steps as the use case's main flow states them, notable alternative flows as a short list. Every UI-xx appears exactly once across the guide.

**Commit:** `docs: add the heimdall user guide`

### Task 7: Heimdall integrating, API map, repositories

**Pages:** `content/en/docs/integrating/_index.md`, `content/en/docs/api/_index.md`, `content/en/docs/repositories/_index.md`. Append `docs/integrating/`, `docs/api/`, `docs/repositories/`.

**Sources:** heimdall-api System Requirements and Use Case documents (scopes, applications, permissions, caller key), API site Flows (login, scope-permission-claims); fortuna-api's Heimdall integration as cited in the Fortuna fact sheet; fact sheet §6 and §9.

**Content:**
- Integrating — "What a client system gets" (a scope, its persons and applications, its permissions); "Authenticating" (login, the JWT, the claims folded into it); "The caller key" (what it is and why, as the sources state); "Example: Fortuna" (how Fortuna uses Heimdall, linking to the Fortuna site's architecture page); links to the relevant API site flows.
- API documentation — a table: every section of the heimdall-api site, what it covers, deep link. Includes the data-protection documents.
- Repositories — table of the three repositories (holds, default branch, latest release); then per code repository, every requirements document with a one-line description and a GitHub link (using the branch the fact sheet says carries the docs); project boards and milestones.

**Commit:** `docs: add integration, api map and repositories`

---

### Task 8: Fortuna scaffold

**Files (all in `F`):** same set as Task 2.

**Interfaces:** the Fortuna build-and-check command used by Tasks 9–14:

```bash
cd /d/Repositories/fortuna-docs && hugo --minify 2>&1 | tee "$SCRATCH/hugo-f.log" && python scripts/check_site.py --public public --build-log "$SCRATCH/hugo-f.log"
```

- [ ] **Step 1:** `scripts/required_pages.txt` with the header comment and `docs/`. **Step 2:** run the checker → FAIL.
- [ ] **Step 3: Toolchain files** — exactly as Task 2 Step 3, with `heimdall-docs` → `fortuna-docs` in `go.mod` and `package-lock.json`, and **keeping** the Swagger UI section of the SCSS with every `.heimdall-swagger` renamed `.fortuna-swagger` and the comment path `content/en/docs/api-explorer.md` changed to `content/en/docs/api/explorer.md`.
- [ ] **Step 4: `hugo.toml`** — Task 2's file with these differences: `baseURL = "https://artur-rios.github.io/fortuna-docs/"`; `title`/`languages.en.title = "Fortuna"`; `description = "A personal finance system that tracks your whole financial life in one place — and turns it into tables, charts and projections."`; copyright and `github_repo` → `fortuna-docs`; developer links `fortuna-api` ("The .NET API and the native core"), `fortuna-ui` ("The Flutter application for web, Windows, Linux and Android"), `fortuna-docs` ("This site"); the `params.links.user` entry becomes `name = "Heimdall"`, `url = "https://artur-rios.github.io/heimdall-docs/"`, `icon = "fa-solid fa-shield-halved"`, `desc = "The identity system Fortuna signs in through"`; `[[menu.main]]` keeps only GitHub → `https://github.com/artur-rios/fortuna-api`.
- [ ] **Step 5:** minimal `content/en/_index.md` and `content/en/docs/_index.md` (description: "What Fortuna is, how it is put together, how to install it, how to use it, and its API.").
- [ ] **Step 6:** `docs/fact-sheet.md` from `SCRATCH/fortuna-facts.md` with the Task 2 header adapted to Fortuna.
- [ ] **Step 7:** `deploy.yml` as Task 2 Step 7. **Step 8:** README as Task 2 Step 8, adapted to Fortuna (no API-site paragraph; mention the explorer reads `fortuna.json` from fortuna-api's `main`).
- [ ] **Step 9:** build and check → `0 problem(s)`.
- [ ] **Step 10:** `git add -A && git commit -m "build: scaffold the fortuna docs site"`

### Tasks 9–14: Fortuna content

Same six-step cycle as Tasks 3–7, using the Fortuna build-and-check command.

### Task 9: Fortuna landing, docs index, overview, concepts, about

**Pages:** `_index.md`, `docs/_index.md`, `docs/overview/_index.md`, `docs/concepts/_index.md`, `about/_index.md`. Append `docs/overview/`, `docs/concepts/`, `about/`.

**Sources:** both READMEs (What it does / doesn't, Status), both Project Overview and Vision Documents, both Business Rules documents; fact sheet §1, §2, §8.

**Content:**
- Landing — cover ("Fortuna", pitch, Get started, Source), lead, two feature rows: every account in one place; many ways in (manual, Pluggy, Excel, PDF statements); spreadsheet and drill-down charts; projections; multiple currencies with PTAX; desktop offline mode. A third `blocks/section` "What Fortuna never does" (moves money, stores bank credentials, gives advice).
- Docs index — table of every docs section.
- Overview — what it does, what it doesn't, who it is for, status (cite the README status lines with their date of reading).
- Concepts — holdings; money movement; installments; recurring commitments; categories, budgets, goals; reconciliation; currencies and PTAX; imports; exports and attachments; consent and data rights. Each with the `BR-xx` rules a user must know, cited by number with a link to the Business Rules document.
- About — why Fortuna exists, stack per repo, licence, link to Heimdall.

**Commit:** `docs: add the fortuna landing page and concepts`

### Task 10: Fortuna architecture

**Pages:** `docs/architecture/_index.md`. Append `docs/architecture/`.

**Sources:** fact sheet §3; fortuna-api README, Technology Stack and Operations & Infrastructure Documents, System Requirements (architecture/data model), `native/`, `src/` layout; fortuna-ui README (offline paragraph), Technology Stack Document, `native/`.

**Content — five Mermaid diagrams with explanations:** component graph; deployment modes (shared multi-user vs desktop offline in-process native core); import pipeline (sources → source contract → per-row outcomes); signing in through Heimdall (sequence) plus the offline-account exception; chart drill-down (aggregation → transactions). Then "What offline mode does not support yet", listing exactly the features the UI README names, with the stated reason.

**Commit:** `docs: add the fortuna architecture page`

### Task 11: Fortuna installation

**Pages:** `docs/installation/_index.md`. Append `docs/installation/`.

**Sources:** both READMEs (Installation/Prerequisites), both Operations & Infrastructure Documents, `docker-compose.yml`, `Dockerfile`s, `.github/workflows/`, releases; fact sheet §4.

**Content:** "Getting a release" (what is actually published, per platform, with links; say plainly what is not); "Running the API" (prerequisites, PostgreSQL vs offline store, configuration — env var names only, migrations, Docker Compose); "Building the native core"; "Running the UI" per target, including offline mode setup; "Connecting to Heimdall" (configuration, linking to the Heimdall site's Integrating page).

**Commit:** `docs: add the fortuna installation guide`

### Task 12: Fortuna user guide

**Pages:** `docs/user-guide/_index.md` plus one page per area: `signing-in.md`, `holdings.md`, `transactions.md`, `installments-and-recurring.md`, `imports.md`, `spreadsheet.md`, `charts.md`, `projections.md`, `exports.md`, `data-rights.md`, `offline-mode.md` — final grouping follows fortuna-ui's Use Case Specification Document. Append each URL.

**Sources:** fortuna-ui Use Case Specification Document, System Requirements Document (screens, navigation); fortuna-api Use Case Specification Document for behaviour the UI exposes; fact sheet §5.

**Content:** index page with the navigation map. Each page: purpose, then one subsection per use case ("UC-xx: name", main flow as steps, notable alternatives). Every UI use case appears exactly once. `offline-mode.md` explains what works, what shows "Not available offline" and why.

**Commit:** `docs: add the fortuna user guide`

### Task 13: Fortuna API reference and explorer

**Pages:** `docs/api/_index.md` (reference), `docs/api/explorer.md`. Append `docs/api/`, `docs/api/explorer/`.

**Sources:** fortuna-api System Requirements Document (endpoint surface, authorization matrix, error model, conventions), Operations & Infrastructure (rate limiting), `docs/openapi/fortuna.json`; fact sheet §6.

- [ ] Reference page: authentication (Heimdall JWT; offline), authorization matrix summary, error model, pagination/filtering/sorting, rate limiting, then a table of endpoint groups (tag, count, what it covers) — counts taken from `fortuna.json`.
- [ ] Explorer page `content/en/docs/api/explorer.md`:

````markdown
---
title: API explorer
linkTitle: API explorer
weight: 20
description: Swagger UI over fortuna-api's OpenAPI document — every endpoint, its schema, and its authorization.
---

Every endpoint the API exposes, rendered from
[`docs/openapi/fortuna.json`](https://github.com/artur-rios/fortuna-api/blob/main/docs/openapi/fortuna.json)
on fortuna-api's `main` branch — read live, so this page always shows the
released document. If the explorer below stays empty, open
[the raw document](https://raw.githubusercontent.com/artur-rios/fortuna-api/main/docs/openapi/fortuna.json)
directly.

{{% alert title="This explorer does not call anything" color="info" %}}
There is no server behind this page, so **Try it out** and **Authorize** are
removed. To call the endpoints, run the API (see [Installation](../../installation/))
and use its own Swagger UI. For what each endpoint means and who may call it,
see the [API reference](../).
{{% /alert %}}

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.32.13/swagger-ui.css" integrity="sha384-tRpWwikYYdk1+1Mu0osh0Tz/Ay5xgS+s/Nf2Aa7GVAFtZLFdJlAbozfrq4g+xHBK" crossorigin="anonymous">

<div id="swagger-ui" class="fortuna-swagger"></div>

<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.32.13/swagger-ui-bundle.js" integrity="sha384-PsJla434CobCNv3y1K4wRavOqkUAvwGEQEfbUmI98CCqqGCJsmuDsgIjM6ZQQODP" crossorigin="anonymous"></script>
<script>
  // Width, dark mode and the inert padlocks: assets/scss/_styles_project.scss, .fortuna-swagger.
  window.addEventListener('load', function () {
    window.SwaggerUIBundle({
      url: 'https://raw.githubusercontent.com/artur-rios/fortuna-api/main/docs/openapi/fortuna.json',
      dom_id: '#swagger-ui',
      supportedSubmitMethods: [],
      docExpansion: 'none',
      defaultModelsExpandDepth: 0,
      deepLinking: true,
      filter: true,
      tryItOutEnabled: false,
      presets: [window.SwaggerUIBundle.presets.apis],
      plugins: [{ wrapComponents: { authorizeBtn: function () { return function () { return null; }; } } }],
      layout: 'BaseLayout'
    });
  });
</script>
````

- [ ] Run build-and-check; then verify in the browser (Task 15 tooling) that operations render, and that with the network request to `raw.githubusercontent.com` blocked the intro's raw-document link is still visible.

**Commit:** `docs: add the fortuna api reference and explorer`

### Task 14: Fortuna operations, development, repositories

**Pages:** `docs/operations/_index.md`, `docs/development/_index.md`, `docs/repositories/_index.md`. Append each.

**Sources:** both Operations & Infrastructure Documents (environments, health, logging, `IR-01` … `IR-20`, `UC-75`), Development Workflow and Testing Specification Documents, both `CONTRIBUTING.md`; fact sheet §7–§9.

**Content:** Operations — configuration (env var names), environments, health checks, logging, the IR list as a table (id, one line). Development — how a use case is delivered (branch pattern, gates, Definition of Done), testing standards and how to run tests in each repo, contributing links. Repositories — as Heimdall Task 7, plus every `initial/` document.

**Commit:** `docs: add operations, development and repositories`

---

### Task 15: Visual verification (both sites)

**Files:** none unless fixes are needed.

- [ ] **Step 1:** `hugo server --port 1313` in `H` and `hugo server --port 1314` in `F` (via `.claude/launch.json` entries `heimdall-docs` / `fortuna-docs` in `D:\Repositories\.claude\launch.json` and `preview_start`). Sites at `http://localhost:1313/heimdall-docs/` and `http://localhost:1314/fortuna-docs/`.
- [ ] **Step 2:** For every page, light mode, desktop width: screenshot; every Mermaid fence must have rendered to an `<svg>` (`document.querySelectorAll('pre.mermaid:not([data-processed])').length === 0`); no console errors.
- [ ] **Step 3:** Repeat in dark mode (toggle in the navbar): landing bands, diagrams, tables, the Swagger explorer all legible.
- [ ] **Step 4:** Mobile preset (375×812): on every page `document.documentElement.scrollWidth <= window.innerWidth`; navbar and sidebar usable.
- [ ] **Step 5:** Fix anything found in the owning page/SCSS, re-run the build-and-check command, commit `fix: <what>` per fix.

---

### Task 16: Publish on GitHub Pages

- [ ] **Step 1: Final local gate** — both build-and-check commands → `0 problem(s)`; both unit-test runs → `OK`; `git status` clean in both repos.
- [ ] **Step 2: Create and push the repositories**

```bash
cd /d/Repositories/heimdall-docs && gh repo create artur-rios/heimdall-docs --public --description "Heimdall's home page and documentation portal" --homepage "https://artur-rios.github.io/heimdall-docs/" --source . --remote origin --push
cd /d/Repositories/fortuna-docs && gh repo create artur-rios/fortuna-docs --public --description "Fortuna's home page and documentation" --homepage "https://artur-rios.github.io/fortuna-docs/" --source . --remote origin --push
```

- [ ] **Step 3: Enable Pages with the GitHub Actions source**

```bash
gh api -X POST repos/artur-rios/heimdall-docs/pages -f build_type=workflow
gh api -X POST repos/artur-rios/fortuna-docs/pages -f build_type=workflow
```
Then re-run the deploy if the first push's run raced Pages being enabled: `gh workflow run deploy.yml -R artur-rios/<repo> --ref main`.

- [ ] **Step 4: Watch the runs** — `gh run watch -R artur-rios/<repo> <run-id> --exit-status` → success for build and deploy.
- [ ] **Step 5: Live check** — `curl -sI https://artur-rios.github.io/heimdall-docs/` and `…/fortuna-docs/` → `200`; open both in the browser pane; run a one-off external link sweep over each `public/` (every `https://` href requested with `curl -sI -L`, non-2xx/3xx listed) and fix real breaks.
- [ ] **Step 6:** Report the live URLs and anything left open.
