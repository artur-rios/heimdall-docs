#!/usr/bin/env python3
"""Checks a built Hugo site before it is published.

It fails when:

1. there is no built site (public/index.html is missing), or the file that
   lists the required pages (scripts/required_pages.txt) cannot be found;
2. a page listed in scripts/required_pages.txt was not built;
3. an internal link or asset does not resolve to a built file, points
   outside the site's base path, or names an #anchor the target page
   does not have;
4. the Hugo build log holds a warning or error other than the two
   deprecations Docsy v0.15.0 triggers under current Hugo;
5. the content directory is missing, or the content still holds
   placeholder text (the upper-case markers TODO, TBD and FIXME, or
   "lorem ipsum" in any case).

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

# The markers are case-sensitive on purpose: "Todo" is a real GitHub project
# status and "to-do" is ordinary prose. Only the shouted forms are leftovers.
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD|FIXME)\b|(?i:lorem ipsum)")
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

    if not (public / "index.html").is_file():
        errors.append(f"no built site: {public.as_posix()}/index.html is missing")

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
    if not content.is_dir():
        return [f"content directory not found: {content.as_posix()}"]
    errors = []
    for md in sorted(content.rglob("*.md")):
        for number, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if PLACEHOLDER.search(line):
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

    errors: list[str] = []
    required: list[str] = []
    if args.required.is_file():
        required = [line.strip() for line in args.required.read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.startswith("#")]
    else:
        errors.append(f"required-pages file not found: {args.required}")
    errors += check_pages(args.public, args.base_url or _base_url_from_config(), required)
    if args.build_log:
        errors += check_build_log(args.build_log.read_text(encoding="utf-8", errors="replace"))
    errors += check_content(args.content)

    for error in errors:
        print(f"ERROR: {error}")
    print(f"check_site: {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
