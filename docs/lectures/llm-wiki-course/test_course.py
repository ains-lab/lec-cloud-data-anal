"""Verify every requested deck against its captured WikiDocs source assets."""
from pathlib import Path
from html.parser import HTMLParser
import base64
import hashlib
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent
LECTURES = ROOT.parent


class DeckReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = {}
        self.table_id = None
        self.rows = None
        self.row = None
        self.cell = None
        self.images = []
        self.slide_ids = []
        self.links = []
        self.external_dependencies = []
        self.font_data = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and 'slide' in (attrs.get('class') or '').split():
            self.slide_ids.append(attrs['id'])
        if tag == 'table' and 'data-source-table' in attrs:
            self.table_id = attrs['data-source-table']
            self.rows = []
        elif tag == 'tr' and self.table_id:
            self.row = []
        elif tag in ('td', 'th') and self.table_id:
            self.cell = []
        elif tag == 'img' and 'data-source-image' in attrs:
            self.images.append(attrs)
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag in ('script', 'img', 'link'):
            address = attrs.get('src') or attrs.get('href') or ''
            if address.startswith(('http:', 'https:')):
                self.external_dependencies.append(address)

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            assert self.row is not None
            self.row.append(''.join(self.cell))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            assert self.rows is not None
            self.rows.append(self.row)
            self.row = None
        elif tag == 'table' and self.table_id:
            self.tables.setdefault(self.table_id, []).append(self.rows)
            self.table_id = None
            self.rows = None


def displayed(cell):
    return re.sub(r'`([^`]*)`', r'\1', cell)


class DeckTest(unittest.TestCase):
    def test_captured_source_tables_have_complete_manifest_coverage(self):
        for week in range(9, 16):
            folder = LECTURES / f'{week}w/slides'
            manifest = json.loads((folder / 'assets/source-tables.json').read_text())
            for source in sorted((folder / 'assets/sources').glob('*.md')):
                lines = source.read_text().splitlines()
                expected = []
                for index, line in enumerate(lines):
                    if index == 0 or not re.fullmatch(r'\s*\|(?:\s*:?-{3,}:?\s*\|)+\s*', line):
                        continue
                    header = lines[index - 1].strip()
                    if not re.fullmatch(r'(?:Copy)?\|.*\|', header):
                        continue
                    # The extractor's Copy toolbar label is outside the first delimiter.
                    header = header[header.index('|'):]
                    split = lambda row: [c.strip() for c in re.split(r'(?<!\\)\|', row.strip().strip('|'))]
                    rows = []
                    cursor = index + 1
                    while cursor < len(lines) and lines[cursor].strip().startswith('|'):
                        rows.append(split(lines[cursor]))
                        cursor += 1
                    expected.append([split(header), *rows])
                actual = [[t['headers'], *t['rows']] for t in manifest
                          if t['page_url'].endswith('/' + source.stem)]
                self.assertCountEqual(actual, expected, f'{week}w source table omitted: {source.name}')

    def check_week(self, week):
        builder = ROOT / 'build_course.py'
        self.assertTrue(builder.exists(), 'Requested multi-week offline deck builder missing')
        subprocess.run([sys.executable, str(builder), '--week', str(week)], check=True, capture_output=True, text=True)
        folder = LECTURES / f'{week}w/slides'
        chapter = week - 7
        output = folder / f'llm-wiki-chapter-{chapter:02d}-slides.html'
        text = output.read_text()
        parser = DeckReader()
        parser.feed(text)
        source_tables = json.loads((folder / 'assets/source-tables.json').read_text())
        source_images = json.loads((folder / 'assets/source-images.json').read_text())
        self.assertEqual(set(parser.tables), {t['id'] for t in source_tables})
        for table in source_tables:
            parts = parser.tables[table['id']]
            headers = [displayed(c) for c in table['headers']]
            self.assertTrue(all(part[0] == headers for part in parts))
            self.assertEqual([row for part in parts for row in part[1:]],
                             [[displayed(c) for c in row] for row in table['rows']], table['id'])
        self.assertEqual([i['data-source-image'] for i in parser.images],
                         [i['local_path'] for i in source_images])
        for rendered, original in zip(parser.images, source_images):
            embedded = base64.b64decode(rendered['src'].split(',', 1)[1], validate=True)
            self.assertEqual(hashlib.sha256(embedded).hexdigest(), original['sha256'])
            self.assertEqual(embedded, (folder / original['local_path']).read_bytes())
        self.assertTrue(parser.slide_ids)
        self.assertEqual(len(parser.slide_ids), len(set(parser.slide_ids)))
        self.assertNotIn('원문 삽화 그대로 · 박승규 / WikiDocs', text)
        self.assertIn(f'{week}주차', text)
        self.assertIn('<html lang="ko">', text)
        self.assertIn('window.LectureDeck', text)
        self.assertIn('data:font/', text)
        self.assertNotRegex(text, r'@@[A-Z_]+@@')
        self.assertEqual(parser.external_dependencies, [])
        pages = json.loads((folder / 'assets/source-pages.json').read_text())
        self.assertTrue({p['url'] for p in pages}.issubset(set(parser.links)))
        provenance = json.loads((folder / 'slides-provenance.json').read_text())
        self.assertEqual(provenance['html_sha256'], hashlib.sha256(output.read_bytes()).hexdigest())
        self.assertEqual(provenance['slide_count'], len(parser.slide_ids))
        self.assertEqual(provenance['original_table_count'], len(source_tables))
        self.assertEqual(provenance['original_image_count'], len(source_images))

    def test_09w_chapter_02(self): self.check_week(9)
    def test_10w_chapter_03(self): self.check_week(10)
    def test_11w_chapter_04(self): self.check_week(11)
    def test_12w_chapter_05(self): self.check_week(12)
    def test_13w_chapter_06(self): self.check_week(13)
    def test_14w_chapter_07(self): self.check_week(14)
    def test_15w_chapter_08(self): self.check_week(15)


if __name__ == '__main__':
    unittest.main(verbosity=2)
