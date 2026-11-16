"""Tests for check_site.py. Run: python -m unittest discover -s scripts -p "test_*.py"

Every test builds its own site, content and files in a temporary directory: none reads the repository's
content/ or public/ folders, and none touches the network.
"""
import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

import check_site

BASE = "https://docs.artur-rios.tech/demo-docs/"


def write(root: Path, rel: str, body: str | bytes) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(body, bytes):
        path.write_bytes(body)
    else:
        path.write_text(body, encoding="utf-8", newline="")
    return path


class TempDirTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)


class CheckPagesTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        self.public = self.root / "public"
        write(self.public, "index.html",
              '<a href="/demo-docs/docs/">Docs</a>'
              '<a href="docs/#intro">Intro</a>'
              '<a href="https://github.com/x">ext</a>'
              '<a href="mailto:a@b.c">mail</a><a href="#">top</a>')
        write(self.public, "docs/index.html", '<h2 id="intro">Intro</h2><a href="../">home</a>')

    def check(self, required=(), base=BASE):
        return check_site.check_pages(self.public, base, list(required))

    # The built site and the required pages

    def test_given_clean_site_when_checked_then_reports_nothing(self):
        self.assertEqual(self.check(["", "docs/"]), [])

    def test_given_required_page_not_built_when_checked_then_reports_it(self):
        self.assertEqual(self.check(["docs/usage/"]), ["required page not built: docs/usage/"])

    def test_given_required_page_without_trailing_slash_when_its_directory_is_built_then_passes(self):
        self.assertEqual(self.check(["docs"]), [])

    def test_given_required_page_that_is_a_file_when_checked_then_only_a_missing_file_fails(self):
        write(self.public, "404.html", "<p>not found</p>")
        self.assertEqual(self.check(["404.html", "robots.txt"]), ["required page not built: robots.txt"])

    def test_given_required_directory_without_index_html_when_checked_then_reports_it(self):
        write(self.public, "docs/empty/style.css", "")
        self.assertEqual(self.check(["docs/empty/"]), ["required page not built: docs/empty/"])

    def test_given_site_root_not_built_when_checked_then_reports_no_site_and_the_root_page(self):
        (self.public / "index.html").unlink()
        write(self.public, "docs/index.html", "<p>no links</p>")
        self.assertEqual(self.check([""]), [
            f"no built site: {self.public.as_posix()}/index.html is missing",
            "required page not built: /",
        ])

    def test_given_missing_public_directory_when_checked_then_reports_no_built_site_with_a_posix_path(self):
        public = self.root / "nope" / "public"
        errors = check_site.check_pages(public, BASE, [])
        self.assertEqual(errors, [f"no built site: {public.as_posix()}/index.html is missing"])
        self.assertNotIn("\\", errors[0])

    # Internal links

    def test_given_broken_relative_link_when_checked_then_reports_page_link_and_target(self):
        write(self.public, "docs/index.html", '<h2 id="intro">x</h2><a href="missing/">x</a>')
        self.assertEqual(self.check(), ["docs/index.html: broken link 'missing/' -> docs/missing/"])

    def test_given_link_to_directory_without_trailing_slash_when_it_has_index_html_then_passes(self):
        write(self.public, "index.html", '<a href="docs">x</a><a href="/demo-docs/docs">y</a>')
        self.assertEqual(self.check(), [])

    def test_given_link_to_directory_without_index_html_when_checked_then_reports_it(self):
        write(self.public, "assets/app.css", "")
        write(self.public, "index.html", '<a href="assets/">x</a>')
        self.assertEqual(self.check(), ["index.html: broken link 'assets/' -> assets/"])

    def test_given_relative_link_in_non_index_page_when_checked_then_resolves_from_the_pages_directory(self):
        write(self.public, "docs/guide/install.html", '<a href="setup.html">x</a><a href="../">up</a>')
        self.assertEqual(self.check(), ["docs/guide/install.html: broken link 'setup.html' -> docs/guide/setup.html"])
        write(self.public, "docs/guide/setup.html", "<p>setup</p>")
        self.assertEqual(self.check(), [])

    def test_given_existing_assets_in_every_link_tag_when_checked_then_passes(self):
        for asset in ("css/site.css", "img/logo.png", "js/app.js", "media/clip.mp4", "embed/index.html"):
            write(self.public, asset, "x")
        write(self.public, "index.html",
              '<link rel="stylesheet" href="css/site.css"><img src="img/logo.png"><script src="js/app.js"></script>'
              '<video><source src="media/clip.mp4"></video><iframe src="embed/"></iframe>')
        self.assertEqual(self.check(), [])

    def test_given_missing_assets_in_every_link_tag_when_checked_then_reports_each(self):
        write(self.public, "index.html",
              '<link rel="stylesheet" href="css/site.css"><img src="img/logo.png"><script src="js/app.js"></script>'
              '<video><source src="media/clip.mp4"></video><iframe src="embed/"></iframe>')
        self.assertEqual(self.check(), [
            "index.html: broken link 'css/site.css' -> css/site.css",
            "index.html: broken link 'img/logo.png' -> img/logo.png",
            "index.html: broken link 'js/app.js' -> js/app.js",
            "index.html: broken link 'media/clip.mp4' -> media/clip.mp4",
            "index.html: broken link 'embed/' -> embed/",
        ])

    def test_given_link_attribute_on_a_tag_the_checker_does_not_follow_when_checked_then_it_is_ignored(self):
        write(self.public, "index.html",
              '<video src="gone.mp4" poster="gone.png"></video><div href="gone/"></div><form action="gone/"></form>')
        self.assertEqual(self.check(), [])

    def test_given_empty_link_attributes_when_checked_then_they_are_ignored(self):
        write(self.public, "index.html", '<a href="">x</a><a href>y</a><img src="">')
        self.assertEqual(self.check(), [])

    def test_given_same_broken_link_on_several_pages_when_checked_then_reports_each_occurrence_in_path_order(self):
        write(self.public, "b.html", '<a href="/demo-docs/gone/">x</a><a href="/demo-docs/gone/">y</a>')
        write(self.public, "a/index.html", '<a href="/demo-docs/gone/">x</a>')
        self.assertEqual(self.check(), [
            "a/index.html: broken link '/demo-docs/gone/' -> gone/",
            "b.html: broken link '/demo-docs/gone/' -> gone/",
            "b.html: broken link '/demo-docs/gone/' -> gone/",
        ])

    def test_given_query_string_and_html_entities_in_link_when_checked_then_only_the_path_is_resolved(self):
        write(self.public, "index.html", '<a href="docs/?tab=1&amp;view=2#intro">x</a>')
        self.assertEqual(self.check(), [])

    def test_given_percent_encoded_space_in_link_when_the_file_exists_then_passes(self):
        write(self.public, "files/release notes.html", "<p>x</p>")
        write(self.public, "index.html", '<a href="files/release%20notes.html">x</a>')
        self.assertEqual(self.check(), [])

    def test_given_unicode_path_raw_or_percent_encoded_when_the_page_exists_then_passes(self):
        write(self.public, "café/index.html", "<p>x</p>")
        write(self.public, "index.html", '<a href="café/">raw</a><a href="caf%C3%A9/">encoded</a>')
        self.assertEqual(self.check(["café/"]), [])

    def test_given_broken_unicode_link_when_checked_then_reports_the_decoded_target(self):
        write(self.public, "index.html", '<a href="caf%C3%A9/">x</a>')
        self.assertEqual(self.check(), ["index.html: broken link 'caf%C3%A9/' -> café/"])

    def test_given_page_with_invalid_utf8_bytes_when_checked_then_its_links_are_still_checked(self):
        write(self.public, "index.html", b'\xff\xfe<p>\x80</p><a href="gone/">x</a>')
        self.assertEqual(self.check(), ["index.html: broken link 'gone/' -> gone/"])

    def test_given_skipped_schemes_and_bare_fragment_when_checked_then_they_are_not_followed(self):
        write(self.public, "index.html",
              '<a href="mailto:a@b.c">m</a><a href="tel:+1555">t</a><a href="javascript:void(0)">j</a>'
              '<img src="data:image/png;base64,AAAA"><a href="#">top</a>')
        self.assertEqual(self.check(), [])

    # The base path and the host

    def test_given_root_absolute_link_missing_the_base_path_when_checked_then_reports_outside_the_site(self):
        write(self.public, "docs/index.html", '<h2 id="intro">x</h2><a href="/docs/">x</a>')
        self.assertEqual(self.check(),
                         ["docs/index.html: link '/docs/' points outside the site (missing /demo-docs/)"])

    def test_given_link_to_the_host_root_when_checked_then_reports_outside_the_site(self):
        write(self.public, "index.html", '<a href="/">x</a>')
        self.assertEqual(self.check(), ["index.html: link '/' points outside the site (missing /demo-docs/)"])

    def test_given_relative_link_climbing_above_the_base_path_when_checked_then_reports_outside_the_site(self):
        write(self.public, "index.html", '<a href="../docs/">x</a>')
        self.assertEqual(self.check(),
                         ["index.html: link '../docs/' points outside the site (missing /demo-docs/)"])

    def test_given_other_site_on_the_same_host_when_checked_then_it_is_external(self):
        write(self.public, "index.html", '<a href="https://docs.artur-rios.tech/heimdall-api/docs/">x</a>'
                                         '<a href="/heimdall-api/docs/">y</a>')
        self.assertEqual(self.check(), [])

    def test_given_absolute_url_on_own_host_when_target_is_missing_then_reports_it(self):
        for link in (f"{BASE}docs/gone/", "http://docs.artur-rios.tech/demo-docs/docs/gone/",
                     "//docs.artur-rios.tech/demo-docs/docs/gone/"):
            with self.subTest(link=link):
                write(self.public, "index.html", f'<a href="{link}">x</a>')
                self.assertEqual(self.check(), [f"index.html: broken link {link!r} -> docs/gone/"])

    def test_given_protocol_relative_url_to_another_host_when_checked_then_it_is_external(self):
        write(self.public, "index.html", '<a href="//cdn.example.com/x.js">x</a>')
        self.assertEqual(self.check(), [])

    def test_given_base_url_without_trailing_slash_when_checked_then_it_behaves_as_with_one(self):
        base = BASE.rstrip("/")
        self.assertEqual(self.check(["", "docs/"], base=base), [])
        write(self.public, "index.html", '<a href="/docs/">x</a><a href="gone/">y</a>')
        self.assertEqual(self.check(base=base), [
            "index.html: link '/docs/' points outside the site (missing /demo-docs/)",
            "index.html: broken link 'gone/' -> gone/",
        ])

    # Anchors

    def test_given_link_to_anchor_the_target_lacks_when_checked_then_reports_it(self):
        write(self.public, "index.html", '<a href="docs/#nope">x</a>')
        self.assertEqual(self.check(), ["index.html: link 'docs/#nope' names #nope, which the target lacks"])

    def test_given_same_page_anchor_when_checked_then_only_a_missing_id_fails(self):
        write(self.public, "index.html", '<h2 id="top">x</h2><a href="#top">ok</a><a href="#gone">bad</a>')
        self.assertEqual(self.check(), ["index.html: link '#gone' names #gone, which the target lacks"])

    def test_given_anchor_named_by_a_name_attribute_when_it_is_on_an_a_tag_then_it_counts(self):
        write(self.public, "docs/index.html", '<a name="legacy"></a><div name="other"></div>')
        write(self.public, "index.html", '<a href="docs/#legacy">ok</a><a href="docs/#other">bad</a>')
        self.assertEqual(self.check(), ["index.html: link 'docs/#other' names #other, which the target lacks"])

    def test_given_unicode_anchor_raw_or_percent_encoded_when_the_target_has_it_then_passes(self):
        write(self.public, "docs/index.html", '<h2 id="überblick">x</h2>')
        write(self.public, "index.html", '<a href="docs/#überblick">raw</a><a href="docs/#%C3%BCberblick">enc</a>')
        self.assertEqual(self.check(), [])

    def test_given_anchor_on_a_non_html_target_when_checked_then_the_anchor_is_not_checked(self):
        write(self.public, "openapi/api.json", "{}")
        write(self.public, "index.html", '<a href="openapi/api.json#/paths/~1users">x</a>')
        self.assertEqual(self.check(), [])

    def test_given_anchor_on_a_missing_target_when_checked_then_reports_only_the_broken_link(self):
        write(self.public, "index.html", '<a href="gone/#intro">x</a>')
        self.assertEqual(self.check(), ["index.html: broken link 'gone/#intro' -> gone/"])


class CheckBuildLogTests(unittest.TestCase):
    def test_given_clean_log_when_checked_then_reports_nothing(self):
        self.assertEqual(check_site.check_build_log("Start building sites\nTotal in 900 ms\n"), [])

    def test_given_empty_log_when_checked_then_reports_nothing(self):
        self.assertEqual(check_site.check_build_log(""), [])

    def test_given_deprecation_warning_when_checked_then_reports_it(self):
        # Docsy v0.15.0's two deprecations were allowed until the theme moved on; v0.18.1 triggers none.
        log = "WARN  deprecated: .Site.AllPages was deprecated in Hugo v0.156.0\n"
        self.assertEqual(check_site.check_build_log(log),
                         ["hugo: WARN  deprecated: .Site.AllPages was deprecated in Hugo v0.156.0"])

    def test_given_warnings_and_errors_when_checked_then_reports_each_in_log_order(self):
        log = "Start\nWARN  found no layout file\nERROR render failed\nWARNING: odd\nTotal in 9 ms\n"
        self.assertEqual(check_site.check_build_log(log), [
            "hugo: WARN  found no layout file",
            "hugo: ERROR render failed",
            "hugo: WARNING: odd",
        ])

    def test_given_crlf_log_when_checked_then_messages_hold_no_carriage_return(self):
        self.assertEqual(check_site.check_build_log("Start\r\nERROR render failed  \r\n"),
                         ["hugo: ERROR render failed"])

    def test_given_level_word_not_at_line_start_or_in_lower_case_when_checked_then_it_is_not_a_finding(self):
        log = "  WARN  indented\nPages | 0 WARN\nwarn: lower case\nerror: lower case\n"
        self.assertEqual(check_site.check_build_log(log), [])


class CheckContentTests(TempDirTestCase):
    def check(self):
        return check_site.check_content(self.root)

    def test_given_placeholder_text_when_checked_then_reports_posix_path_line_number_and_line(self):
        md = write(self.root, "en/docs/a.md", "Install it.\n\n  TODO: write the rest  \n")
        errors = self.check()
        self.assertEqual(errors, [f"{md.as_posix()}:3: placeholder text: TODO: write the rest"])
        self.assertNotIn("\\", errors[0])

    def test_given_each_upper_case_marker_when_checked_then_reports_each_line(self):
        write(self.root, "en/docs/a.md", "TODO: write this\nSize: TBD\n(FIXME.)\nDone.\n")
        self.assertEqual(len(self.check()), 3)

    def test_given_lorem_ipsum_in_any_case_when_checked_then_reports_it(self):
        write(self.root, "en/docs/a.md", "lorem ipsum\n\nLorem Ipsum dolor\nLOREM IPSUM\n")
        self.assertEqual(len(self.check()), 3)

    def test_given_several_markers_on_one_line_when_checked_then_reports_the_line_once(self):
        write(self.root, "en/docs/a.md", "TODO and FIXME and lorem ipsum\n")
        self.assertEqual(len(self.check()), 1)

    def test_given_marker_words_in_mixed_case_or_prose_when_checked_then_they_pass(self):
        # "Todo" is a real GitHub project status and "to-do" is ordinary prose.
        write(self.root, "en/docs/a.md",
              "Each issue moves from Todo to Done.\nKeep a to-do list.\nTbd fixme todo\nloremipsum\n")
        self.assertEqual(self.check(), [])

    def test_given_marker_inside_a_longer_word_when_checked_then_it_passes(self):
        write(self.root, "en/docs/a.md", "TODOS\nMY_TODO\nFIXMES\nTBD2\n")
        self.assertEqual(self.check(), [])

    def test_given_placeholder_in_front_matter_when_checked_then_reports_it(self):
        write(self.root, "en/docs/a.md", "---\ntitle: TBD\n---\n\nBody.\n")
        self.assertEqual(len(self.check()), 1)

    def test_given_malformed_front_matter_when_checked_then_the_file_is_still_scanned(self):
        write(self.root, "en/docs/a.md", "---\ntitle: [unclosed\n: : :\nBody without a closing fence. FIXME\n")
        write(self.root, "en/docs/b.md", "+++\ntitle = \nBody.\n")
        self.assertEqual(len(self.check()), 1)

    def test_given_placeholder_in_a_code_block_when_checked_then_reports_it(self):
        write(self.root, "en/docs/a.md", "```python\n# TODO: remove\n```\n")
        self.assertEqual(len(self.check()), 1)

    def test_given_placeholder_outside_markdown_files_when_checked_then_it_is_ignored(self):
        for name in ("en/docs/a.html", "en/docs/data.yaml", "en/docs/notes.txt"):
            write(self.root, name, "TODO\n")
        self.assertEqual(self.check(), [])

    def test_given_placeholders_in_nested_files_when_checked_then_reports_them_sorted_by_path(self):
        # A file of the top directory sorts after one in a sub-directory: a directory walk lists it first.
        b = write(self.root, "en/b.md", "TBD\n")
        a = write(self.root, "en/a/z.md", "TBD\n")
        self.assertEqual(self.check(), [f"{a.as_posix()}:1: placeholder text: TBD",
                                        f"{b.as_posix()}:1: placeholder text: TBD"])

    def test_given_crlf_content_when_checked_then_line_numbers_are_right_and_no_carriage_return_is_kept(self):
        md = write(self.root, "en/a.md", "One.\r\nTwo.\r\nTODO\r\n")
        self.assertEqual(self.check(), [f"{md.as_posix()}:3: placeholder text: TODO"])

    def test_given_unicode_content_when_checked_then_only_real_markers_are_reported(self):
        md = write(self.root, "en/a.md", "﻿Configuração ✓ 日本語 🚀\nÉtat : TODO\n")
        self.assertEqual(self.check(), [f"{md.as_posix()}:2: placeholder text: État : TODO"])

    def test_given_empty_content_directory_when_checked_then_reports_nothing(self):
        self.assertEqual(self.check(), [])

    def test_given_empty_markdown_file_when_checked_then_reports_nothing(self):
        write(self.root, "en/a.md", "")
        self.assertEqual(self.check(), [])

    def test_given_missing_content_directory_when_checked_then_reports_it_with_a_posix_path(self):
        content = self.root / "nope"
        self.assertEqual(check_site.check_content(content), [f"content directory not found: {content.as_posix()}"])

    def test_given_content_path_that_is_a_file_when_checked_then_reports_it_not_found(self):
        content = write(self.root, "content", "TODO")
        self.assertEqual(check_site.check_content(content), [f"content directory not found: {content.as_posix()}"])


class MainTests(TempDirTestCase):
    def setUp(self):
        super().setUp()
        write(self.root, "public/index.html", '<a href="docs/">docs</a>')
        write(self.root, "public/docs/index.html", "<p>ok</p>")
        write(self.root, "content/en/a.md", "Fine.\n")
        write(self.root, "required.txt", "# Pages that must be built.\n\ndocs/\n")

    def run_main(self, *extra, required="required.txt", base_url=BASE):
        argv = ["--public", str(self.root / "public"), "--content", str(self.root / "content"),
                "--required", str(self.root / required)]
        if base_url is not None:
            argv += ["--base-url", base_url]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_site.main(argv + list(extra))
        return code, out.getvalue().splitlines()

    def chdir(self, path: Path) -> None:
        previous = os.getcwd()
        os.chdir(path)
        self.addCleanup(os.chdir, previous)

    def test_given_clean_site_when_run_then_exits_zero_and_prints_only_the_summary(self):
        self.assertEqual(self.run_main(), (0, ["check_site: 0 problem(s)"]))

    def test_given_required_file_with_comments_blank_lines_and_crlf_when_run_then_reads_only_the_pages(self):
        write(self.root, "required.txt", "# comment\r\n\r\n  docs/  \r\n# docs/usage/\r\ndocs/usage/\r\n")
        self.assertEqual(self.run_main(),
                         (1, ["ERROR: required page not built: docs/usage/", "check_site: 1 problem(s)"]))

    def test_given_blank_lines_in_required_file_when_the_site_root_is_missing_then_they_require_nothing(self):
        (self.root / "public" / "index.html").unlink()
        write(self.root, "required.txt", "\n   \ndocs/\n\n")
        self.assertEqual(self.run_main(), (1, [
            f"ERROR: no built site: {(self.root / 'public').as_posix()}/index.html is missing",
            "check_site: 1 problem(s)",
        ]))

    def test_given_missing_required_file_when_run_then_fails_and_still_checks_the_site(self):
        write(self.root, "public/index.html", '<a href="gone/">x</a>')
        code, lines = self.run_main(required="missing.txt")
        self.assertEqual(code, 1)
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("ERROR: required-pages file not found: "))
        self.assertTrue(lines[0].endswith("missing.txt"))
        self.assertEqual(lines[1:], ["ERROR: index.html: broken link 'gone/' -> gone/",
                                     "check_site: 2 problem(s)"])

    def test_given_build_log_with_warning_when_run_then_reports_it(self):
        write(self.root, "hugo.log", "Start\nWARN  found no layout file\n")
        self.assertEqual(self.run_main("--build-log", str(self.root / "hugo.log")),
                         (1, ["ERROR: hugo: WARN  found no layout file", "check_site: 1 problem(s)"]))

    def test_given_build_log_with_invalid_utf8_bytes_when_run_then_it_is_still_checked(self):
        write(self.root, "hugo.log", b"\xff\xfe\nERROR render failed\n")
        self.assertEqual(self.run_main("--build-log", str(self.root / "hugo.log")),
                         (1, ["ERROR: hugo: ERROR render failed", "check_site: 1 problem(s)"]))

    def test_given_no_build_log_option_when_run_then_the_log_is_not_checked(self):
        write(self.root, "hugo.log", "ERROR render failed\n")
        self.assertEqual(self.run_main(), (0, ["check_site: 0 problem(s)"]))

    def test_given_placeholder_in_content_when_run_then_reports_it(self):
        md = write(self.root, "content/en/a.md", "TBD\n")
        self.assertEqual(self.run_main(),
                         (1, [f"ERROR: {md.as_posix()}:1: placeholder text: TBD", "check_site: 1 problem(s)"]))

    def test_given_problems_in_every_check_when_run_then_reports_them_in_check_order(self):
        write(self.root, "public/index.html", '<a href="gone/">x</a>')
        write(self.root, "hugo.log", "ERROR render failed\n")
        md = write(self.root, "content/en/a.md", "FIXME\n")
        write(self.root, "required.txt", "docs/usage/\n")
        self.assertEqual(self.run_main("--build-log", str(self.root / "hugo.log")), (1, [
            "ERROR: required page not built: docs/usage/",
            "ERROR: index.html: broken link 'gone/' -> gone/",
            "ERROR: hugo: ERROR render failed",
            f"ERROR: {md.as_posix()}:1: placeholder text: FIXME",
            "check_site: 4 problem(s)",
        ]))

    def test_given_no_base_url_option_when_run_then_reads_base_url_from_hugo_toml_in_the_working_directory(self):
        write(self.root, "hugo.toml", 'baseURL = "https://docs.artur-rios.tech/other-docs/"\ntitle = "x"\n')
        self.chdir(self.root)
        self.assertEqual(self.run_main(base_url=None), (0, ["check_site: 0 problem(s)"]))
        write(self.root, "public/index.html", '<a href="/other-docs/gone/">x</a>')
        self.assertEqual(self.run_main(base_url=None),
                         (1, ["ERROR: index.html: broken link '/other-docs/gone/' -> gone/",
                              "check_site: 1 problem(s)"]))

    def test_given_base_url_option_when_run_then_hugo_toml_is_not_needed(self):
        self.chdir(self.root)
        self.assertFalse((self.root / "hugo.toml").exists())
        self.assertEqual(self.run_main(), (0, ["check_site: 0 problem(s)"]))

    def test_given_default_paths_when_run_from_the_repository_root_then_uses_public_content_and_required_pages(self):
        write(self.root, "scripts/required_pages.txt", "# Pages that must be built.\n\ndocs/\ndocs/usage/\n")
        self.chdir(self.root)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_site.main(["--base-url", BASE])
        self.assertEqual((code, out.getvalue().splitlines()),
                         (1, ["ERROR: required page not built: docs/usage/", "check_site: 1 problem(s)"]))


if __name__ == "__main__":
    unittest.main()
