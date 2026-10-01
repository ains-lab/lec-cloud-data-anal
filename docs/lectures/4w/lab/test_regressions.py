"""Regression cases found during the handout's integration review."""
import datetime as dt
import json
import sqlite3
import unittest
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from email.message import Message

import pipeline


class RegressionTests(unittest.TestCase):
    def test_utc_rejects_unsupported_or_out_of_range_values_as_value_error(self):
        for value in ([], {}, True, False, 1e30, -1e30, 1e18, 10 ** 400,
                      float('inf'), float('-inf'), float('nan')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                pipeline.utc(value)

    def test_utc_preserves_supported_timestamp_semantics(self):
        cases = [
            (dt.datetime(2026, 1, 1, 9, tzinfo=dt.timezone(dt.timedelta(hours=9))),
             '2026-01-01T00:00:00Z'),
            ('2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z'),
            ('2026-01-01T09:00:00+09:00', '2026-01-01T00:00:00Z'),
            ('2026-01-01T09:00:00+0900', '2026-01-01T00:00:00Z'),
            (0, '1970-01-01T00:00:00Z'),
            (0.5, '1970-01-01T00:00:00.500000Z'),
            (-1, '1969-12-31T23:59:59Z')]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(pipeline.utc(value), expected)
        before = dt.datetime.now(dt.timezone.utc)
        now_values = (pipeline.utc(), pipeline.utc(None))
        after = dt.datetime.now(dt.timezone.utc)
        for value in now_values:
            self.assertTrue(value.endswith('Z'))
            self.assertLessEqual(before, dt.datetime.fromisoformat(value))
            self.assertLessEqual(dt.datetime.fromisoformat(value), after)
        for value in (dt.datetime(2026, 1, 1), '2026-01-01T00:00:00'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, '^timezone required$'):
                pipeline.utc(value)

    def test_article_query_identity_is_preserved_without_token(self):
        url = 'https://example.org/article?id=42&access_token=SECRET#section'
        self.assertEqual(pipeline.safe_url(url), 'https://example.org/article?id=42')

    def test_reddit_userinfo_never_reaches_storage_or_export(self):
        for userinfo in ('', ':', ':FIXTURE_PASSWORD', 'fixture-user',
                         'fixture-user:FIXTURE_PASSWORD'):
            with self.subTest(userinfo=userinfo), tempfile.TemporaryDirectory() as temp:
                url = 'https://' + userinfo + '@example.invalid/article'
                raw = {'data': {'children': [{'data': {
                    'id': 'synthetic-1', 'created_utc': 1767225600,
                    'permalink': '/r/test/comments/synthetic-1/article/',
                    'title': '[SYNTHETIC] URL fixture', 'url': url}}], 'after': None}}
                live = pipeline.Live(
                    {'REDDIT_ACCESS_TOKEN': 'fixture-only-token', 'REDDIT_USER_AGENT': 'lab/1.0'},
                    lambda *args: raw)
                page = live('reddit', 'Hermes', None)
                data = Path(temp) / 'data'
                config = {'queries': [{'id': 'q', 'platform': 'reddit', 'query': 'Hermes'}]}
                self.assertEqual(pipeline.run(config, data, 'live', live), 0)
                report = pipeline.report(data)
                self.assertEqual((report['posts'], report['versions'], report['observations']),
                                 (1, 1, 1))
                exported = [json.loads(line) for line in Path(report['export']).read_text().splitlines()]
                self.assertEqual(len(exported), 1)
                self.assertEqual(exported[0]['external_urls'], [])
                self.assertEqual(page['posts'][0]['external_urls'], [])
                payload = json.loads(Path(exported[0]['payload_path']).read_text())
                self.assertEqual(payload['posts'][0]['external_urls'], [])
                with sqlite3.connect(data / 'pipeline.sqlite3') as connection:
                    for table in ('posts', 'post_versions', 'observation_facts'):
                        rows = connection.execute('SELECT external_urls_json FROM ' + table).fetchall()
                        self.assertEqual(rows, [('[]',)], table)
                for path in data.iterdir():
                    self.assertNotIn(b'FIXTURE_PASSWORD', path.read_bytes(), path.name)
                self.assertEqual(pipeline.safe_url(url), '')

    def test_http_status_survives_without_secret_error_text(self):
        def denied(request, timeout):
            raise HTTPError('https://example.invalid/?token=DO_NOT_SAVE',
                            401, 'DO_NOT_SAVE', Message(), None)

        def fetch(*args):
            return pipeline.http_get('https://api.x.com/test', {}, {}, opener=denied)

        with tempfile.TemporaryDirectory() as temp:
            data = Path(temp) / 'data'
            config = {'queries': [{'id': 'q', 'platform': 'x', 'query': 'Hermes'}]}
            self.assertEqual(pipeline.run(config, data, 'live', fetch), 1)
            health = pipeline.report(data)['health']
            self.assertEqual(health[0]['reason'], 'http_401')
            self.assertNotIn('DO_NOT_SAVE', str(health))

    def test_threads_final_cursor_without_next_stops(self):
        # Graph cursors may describe the current page even with no next page.
        payload = {'data': [], 'paging': {'cursors': {'after': 'last-cursor'}}}
        live = pipeline.Live({'THREADS_ACCESS_TOKEN': 'fixture-only-token'},
                             lambda *args: payload)
        self.assertIsNone(live('threads', 'Hermes', None)['next_token'])


if __name__ == '__main__':
    unittest.main()
