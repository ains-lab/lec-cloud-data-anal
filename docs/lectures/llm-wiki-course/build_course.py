#!/usr/bin/env python3
"""Build the requested 9w–15w decks offline from reviewed content and assets.

No collection, installation, model calls, or external writes are performed.
"""
from pathlib import Path
import argparse
import base64
import copy
import hashlib
import html
import json
import math
import re


HERE = Path(__file__).resolve().parent
LECTURES = HERE.parent


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verified_bytes(root, record):
    path = (root / record['local_path']).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Asset outside requested directory')
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != record['sha256']:
        raise ValueError(f'Asset hash mismatch: {path}')
    return data


def inline(text):
    parts = re.split(r'(`[^`]*`)', text)
    return ''.join('<code>' + html.escape(p[1:-1]) + '</code>'
                   if p.startswith('`') and p.endswith('`') else html.escape(p) for p in parts)


def plain(text):
    return html.unescape(re.sub(r'<[^>]*>', ' ', text)).strip()


def table_parts(table, widths=None):
    """Repeat the original header, partition rows only, never shorten cells."""
    columns = len(table['headers'])
    if any(len(row) != columns for row in table['rows']):
        raise ValueError(f'Ragged original table: {table["id"]}')
    if widths and (len(widths) != columns or sum(widths) != 100):
        raise ValueError('Column widths must total 100')
    sizes = widths or [100 / columns] * columns
    parts, rows, used = [], [], 0
    for row in table['rows']:
        heights = [math.ceil(len(re.sub(r'`', '', cell)) / max(8, int(1760 * width / 100 / 26) - 2))
                   for cell, width in zip(row, sizes)]
        height = max(heights, default=1) * 39 + 28
        if rows and (used + height > 430 or len(rows) >= 5):
            parts.append(rows)
            rows, used = [], 0
        rows.append(row)
        used += height
    if rows or not parts:
        parts.append(rows)
    return parts


def render_table(table, slide):
    widths = slide.get('widths')
    colgroup = '<colgroup>' + ''.join(f'<col style="width:{w}%">' for w in widths) + '</colgroup>' if widths else ''
    head = '<thead><tr>' + ''.join(f'<th scope="col">{inline(cell)}</th>' for cell in table['headers']) + '</tr></thead>'
    rows = '<tbody>' + ''.join('<tr>' + ''.join(f'<td>{inline(cell)}</td>' for cell in row) + '</tr>' for row in slide['_rows']) + '</tbody>'
    note = slide.get('takeaway', '원문의 머리글·셀 문구·행 순서를 보존했다. 아래 해설은 강의용 설명이다.')
    if table.get('in_code_example'):
        note = '원문 코드·문서 예시의 표이며 실제 실행 결과가 아니다. ' + note
    return (f'<div class="table-panel"><div class="table-scroll"><table class="source-table dense" '
            f'data-source-table="{table["id"]}" data-source-part="{slide["_part"]}">'
            f'<caption>{html.escape(plain(slide["title"]))} · 원문 표</caption>{colgroup}{head}{rows}</table></div>'
            f'<p class="takeaway">{html.escape(note)}</p></div>')


def build(week):
    if week not in range(9, 16):
        raise ValueError('Only explicitly requested weeks 9–15 are allowed')
    chapter = week - 7
    root = LECTURES / f'{week}w/slides'
    spec = read_json(root / 'slides-content.json')
    tables_list = read_json(root / 'assets/source-tables.json')
    images_list = read_json(root / 'assets/source-images.json')
    pages = read_json(root / 'assets/source-pages.json')
    tables = {t['id']: t for t in tables_list}
    images = {i['local_path']: i for i in images_list}
    sources = read_json(HERE / 'citations.json')['sources']
    by_url = {s['url']: s for s in sources}
    urls = [spec['source_book_url']] + [p['url'] for p in pages]
    original_slides = spec['slides']
    table_refs = [s['table'] for s in original_slides if 'table' in s]
    image_refs = [s['image'] for s in original_slides if 'image' in s]
    if len(table_refs) != len(set(table_refs)) or set(table_refs) != set(tables):
        raise ValueError(f'{week}w: each source table must appear exactly once in content')
    if len(image_refs) != len(set(image_refs)) or set(image_refs) != set(images):
        raise ValueError(f'{week}w: each source image must appear exactly once in content')
    slides = []
    for original in original_slides:
        if original['kind'] == 'table':
            table = tables[original['table']]
            parts = table_parts(table, original.get('widths'))
            for part, rows in enumerate(parts, 1):
                slide = copy.deepcopy(original)
                slide.update({'_rows': rows, '_part': part, 'sources': [table['page_url']]})
                if len(parts) > 1:
                    slide['title'] += f' · {part}/{len(parts)}'
                slides.append(slide)
        else:
            slides.append(copy.deepcopy(original))
    slides.append({'kind': 'sources', 'section': '출처와 사용 안내', 'title': '원전과 강의 설명 구분하기',
                   'subtitle': '원전: 박승규, 『LLM위키 완벽 가이드』 · WikiDocs', 'sources': [spec['source_book_url']]})
    options, rendered, inventory = [], [], []
    for number, slide in enumerate(slides, 1):
        kind = slide['kind']
        body = slide.get('body', '')
        subtitle = slide.get('subtitle', '')
        source_urls = slide.get('sources', [])
        if kind == 'table':
            body = render_table(tables[slide['table']], slide)
            subtitle = '원문 표 · 셀 문구와 행 순서 유지 · 길면 머리글을 반복하여 나눠 표시'
        elif kind in ('image', 'cover'):
            image = images[slide['image']]
            payload = base64.b64encode(verified_bytes(root, image)).decode('ascii')
            figure = (f'<figure class="original-image"><img src="data:{image["content_type"]};base64,{payload}" '
                      f'data-source-image="{html.escape(image["local_path"])}" alt="{html.escape(image["alt"])}" '
                      f'width="{image["width"]}" height="{image["height"]}"></figure>')
            if kind == 'cover':
                body = f'<div class="cover-layout"><div>{body}</div>{figure}</div>'
            else:
                body = f'<div class="illustration-layout">{figure}<article>{body}</article></div>'
            if image['page_url'] not in source_urls:
                source_urls = [image['page_url'], *source_urls]
        elif kind == 'sources':
            bibliography = '<ul class="bibliography">' + ''.join(
                f'<li><a href="{html.escape(u)}" target="_blank" rel="noopener noreferrer">'
                f'[{by_url[u]["id"]}] {html.escape(by_url[u]["title"])}</a>'
                f'<span class="url">{html.escape(u)}</span></li>' for u in urls) + '</ul>'
            body = ('<div class="sources-grid"><div>' + bibliography + '</div><div>'
                    '<p>원문 이미지·표: 박승규 / WikiDocs</p>' +
                    '<p>이미지 파일은 변환 없이 내장했다.<br>표는 원문 셀과 순서를 보존했다.</p>'
                    '<p>쉬운 설명·워크플로우 재구성·가상 예시는 강의용으로 덧붙였다. 책의 예시 수치는 수업의 측정 성과가 아니다.</p>'
                    '<p class="subtle">도구·명령 예시는 책의 확인 시점 기준이다. 실제 실행 전 최신 공식 문서와 입력 허용 범위를 확인한다.</p>'
                    '<p class="subtle">← / → 이동 · R 전체 읽기 · F 전체 화면<br>인쇄에는 전체 슬라이드와 접힌 답이 포함된다.</p>'
                    '</div></div>')
        for url in source_urls:
            if url not in urls or url not in by_url:
                raise ValueError(f'Unsupported citation in {week}w: {url}')
        citations = ''.join(f'<a href="{html.escape(url)}" title="{html.escape(by_url[url]["title"])}" '
                            f'target="_blank" rel="noopener noreferrer">[{by_url[url]["id"]}] '
                            f'{html.escape(by_url[url]["title"].split()[0] if url != spec["source_book_url"] else "원전")}</a>'
                            for url in source_urls)
        slide_id, heading_id = f'slide-{number:02d}', f'heading-{number:02d}'
        title = plain(slide['title'])
        classes = 'slide tall-title' if '<br' in slide['title'] else 'slide'
        rendered.append(f'<section class="{classes}" id="{slide_id}" data-kind="{kind}" '
                        f'data-title="{html.escape(title)}" aria-labelledby="{heading_id}" aria-hidden="true">'
                        f'<header class="slide-header"><p class="kicker">{html.escape(slide["section"])}</p>'
                        f'<h2 id="{heading_id}">{slide["title"]}</h2><p class="subtitle">{html.escape(subtitle)}</p></header>'
                        f'<div class="slide-body">{body}</div><footer class="slide-footer"><div class="source-links">{citations}</div>'
                        f'<span class="slide-number">{number:02d} / {len(slides):02d}</span></footer></section>')
        options.append(f'<option value="{number}">{number:02d} · {"부록 · " if slide.get("appendix") else ""}{html.escape(title)}</option>')
        inventory.append({'id': slide_id, 'title': title, 'section': slide['section'], 'kind': kind,
                          'appendix': slide.get('appendix', False), 'sources': source_urls,
                          'source_table': slide.get('table'), 'table_part': slide.get('_part'), 'source_image': slide.get('image')})
    fonts = read_json(HERE / 'assets/fonts.json')
    font_css = []
    for record in fonts:
        encoded = base64.b64encode(verified_bytes(HERE, record)).decode('ascii')
        unicode_range = ';unicode-range:' + record['unicode_range'] if record.get('unicode_range') else ''
        font_css.append(f'@font-face{{font-family:"Lecture Noto";font-style:normal;font-weight:{record["weight"]};'
                        f'font-display:swap;src:url(data:font/woff2;base64,{encoded}) format("woff2"){unicode_range}}}')
    substitutions = {'@@TITLE@@': html.escape(spec['title']), '@@WEEK@@': str(week), '@@CHAPTER@@': f'{chapter:02d}',
                     '@@FONTS@@': '\n'.join(font_css), '@@SLIDES@@': '\n'.join(rendered), '@@OPTIONS@@': '\n'.join(options),
                     '@@FONT_LICENSE@@': (HERE / 'assets/OFL.txt').read_text().replace('--', '—')}
    output = (HERE / 'slides-template.html').read_text()
    for placeholder, value in substitutions.items():
        if placeholder not in output:
            raise ValueError(f'Missing template placeholder {placeholder}')
        output = output.replace(placeholder, value)
    if re.search(r'@@[A-Z_]+@@', output):
        raise ValueError('Unresolved placeholder')
    if '원문 삽화 그대로 · 박승규 / WikiDocs' in output:
        raise ValueError('Removed attribution caption must not be regenerated')
    destination = root / f'llm-wiki-chapter-{chapter:02d}-slides.html'
    destination.write_text(output, encoding='utf-8')
    provenance = {'schema_version': 'material_artifact/v1', 'status': 'generated', 'week': week, 'chapter': chapter,
                  'title': spec['title'], 'format': 'offline self-contained HTML deck', 'output': destination.name,
                  'source_author': spec['source_author'], 'source_book_url': spec['source_book_url'],
                  'html_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(), 'slide_count': len(slides),
                  'main_slide_count': sum(not s.get('appendix', False) for s in slides),
                  'original_image_count': len(images), 'original_table_count': len(tables),
                  'source_page_count': len(pages), 'image_transformation': 'none; original bytes embedded as base64',
                  'table_transformation': 'original headers/cells/order preserved; long tables paginated with repeated headers',
                  'source_retrieval': 'WikiDocs primary pages via web_extract; direct site/browser blocked by Cloudflare',
                  'font_license': 'SIL Open Font License 1.1; embedded in HTML and shared assets/OFL.txt',
                  'source_last_edited': '2026-05-16 as displayed by retrieved pages',
                  'visual_review': 'not_performed by builder; see separately recorded browser verification', 'slides': inventory}
    (root / 'slides-provenance.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
    return {k: provenance[k] for k in ('week', 'chapter', 'output', 'html_sha256', 'slide_count', 'main_slide_count', 'original_image_count', 'original_table_count')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--week', type=int, choices=range(9, 16))
    args = parser.parse_args()
    weeks = [args.week] if args.week is not None else range(9, 16)
    print(json.dumps([build(week) for week in weeks], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
