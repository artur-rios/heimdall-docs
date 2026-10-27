"""Tests for check_site.py. Run: python -m unittest discover -s scripts -p "test_*.py" """
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import check_site

BASE = "https://docs.artur-rios.tech/demo-docs/"


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
        write(self.public, "index.html", '<a href="https://docs.artur-rios.tech/heimdall-api/docs/">x</a>')
        self.assertEqual(check_site.check_pages(self.public, BASE, []), [])

    def test_missing_public_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = check_site.check_pages(Path(tmp) / "nope", BASE, [])
            self.assertEqual(len(errors), 1)
            self.assertIn("no built site", errors[0])


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

    def test_todo_as_a_project_status_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "en/docs/a.md", "Each issue moves from Todo to Done.\n")
            self.assertEqual(check_site.check_content(Path(tmp)), [])

    def test_uppercase_todo_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "en/docs/a.md", "TODO: write this\n")
            self.assertEqual(len(check_site.check_content(Path(tmp))), 1)

    def test_uppercase_tbd_and_fixme_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "en/docs/a.md", "Size: TBD\n\nFIXME later\n")
            self.assertEqual(len(check_site.check_content(Path(tmp))), 2)

    def test_lorem_ipsum_fails_in_any_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp), "en/docs/a.md", "lorem ipsum\n\nLorem Ipsum dolor\n")
            self.assertEqual(len(check_site.check_content(Path(tmp))), 2)

    def test_clean_content_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            # "to-do list" is UI prose, not a placeholder marker.
            write(Path(tmp), "en/docs/a.md", "Keep a to-do list of what to read next.\n")
            self.assertEqual(check_site.check_content(Path(tmp)), [])

    def test_missing_content_dir_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = check_site.check_content(Path(tmp) / "nope")
            self.assertEqual(len(errors), 1)


class MainTests(unittest.TestCase):
    def test_main_fails_without_required_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "public/index.html", "<p>ok</p>")
            write(root, "content/en/a.md", "Fine.\n")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = check_site.main([
                    "--public", str(root / "public"),
                    "--content", str(root / "content"),
                    "--required", str(root / "missing.txt"),
                    "--base-url", BASE,
                ])
            self.assertEqual(code, 1)
            self.assertIn("required-pages file not found", out.getvalue())


if __name__ == "__main__":
    unittest.main()
