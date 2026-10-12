"""End-to-end regression for the lecture deck's original guide assets."""
from html.parser import HTMLParser
from pathlib import Path
import base64
import hashlib
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent


class SourceTableReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = {}
        self.table_id = None
        self.rows = None
        self.row = None
        self.cell = None
        self.images = []
        self.slide_ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and "slide" in (attrs.get("class") or "").split():
            self.slide_ids.append(attrs["id"])
        if tag == "table" and "data-source-table" in attrs:
            self.table_id = attrs["data-source-table"]
            self.rows = []
        elif tag == "tr" and self.table_id:
            self.row = []
        elif tag in ("td", "th") and self.table_id:
            self.cell = []
        elif tag == "img" and "data-source-image" in attrs:
            self.images.append(attrs)

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            assert self.row is not None
            self.row.append("".join(self.cell))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            assert self.rows is not None
            self.rows.append(self.row)
            self.row = None
        elif tag == "table" and self.table_id:
            self.tables[self.table_id] = self.rows
            self.table_id = self.rows = None


class GuideAssetsTest(unittest.TestCase):
    def test_deck_preserves_original_guide_assets(self):
        builder = ROOT / "build_slides.py"
        self.assertTrue(builder.exists(), "HTML deck builder has not been implemented")
        subprocess.run([sys.executable, str(builder)], check=True, cwd=ROOT)
        output = ROOT / "llm-wiki-chapter-02-slides.html"
        parser = SourceTableReader()
        parser.feed(output.read_text(encoding="utf-8"))
        tables = json.loads((ROOT / "assets/source-tables.json").read_text())
        self.assertEqual(set(parser.tables), {table["id"] for table in tables})
        for table in tables:
            expected = [table["headers"], *table["rows"]]
            expected = [[re.sub(r"`([^`]*)`", r"\1", cell) for cell in row] for row in expected]
            self.assertEqual(parser.tables[table["id"]], expected, table["id"])
        images = json.loads((ROOT / "assets/source-images.json").read_text())
        self.assertEqual({image["data-source-image"] for image in parser.images},
                         {image["local_path"] for image in images})
        by_path = {image["local_path"]: image for image in images}
        for image in parser.images:
            original = by_path[image["data-source-image"]]
            embedded = base64.b64decode(image["src"].split(",", 1)[1], validate=True)
            self.assertEqual(hashlib.sha256(embedded).hexdigest(), original["sha256"])
            self.assertEqual(hashlib.sha256((ROOT / original["local_path"]).read_bytes()).hexdigest(),
                             original["sha256"])
        spec = json.loads((ROOT / "slides-content.json").read_text())
        self.assertEqual(len(parser.slide_ids), len(spec["slides"]))
        self.assertEqual(len(parser.slide_ids), len(set(parser.slide_ids)))
        self.assertIn("<html lang=\"ko\">", output.read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
