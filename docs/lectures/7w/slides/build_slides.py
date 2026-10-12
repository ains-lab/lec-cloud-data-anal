#!/usr/bin/env python3
"""Build an offline HTML lecture deck from reviewed lecture content and guide assets.

Uses only Python's standard library. No collection, model calls, or external writes.
"""
from pathlib import Path
import base64
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "llm-wiki-chapter-02-slides.html"


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def verified_bytes(record):
    path = (ROOT / record["local_path"]).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Asset path is outside the lecture directory")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError(f"Asset hash mismatch: {record['local_path']}")
    return data


def inline(text):
    """Render only Markdown inline code; preserve all displayed cell wording."""
    parts = re.split(r"(`[^`]*`)", text)
    return "".join(
        "<code>" + html.escape(part[1:-1]) + "</code>"
        if part.startswith("`") and part.endswith("`")
        else html.escape(part)
        for part in parts
    )


def render_table(table, slide):
    headers = table["headers"]
    rows = table["rows"]
    if any(len(row) != len(headers) for row in rows):
        raise ValueError(f"Ragged source table: {table['id']}")
    dense = len(headers) >= 5 or len(rows) >= 6
    widths = slide.get("widths")
    if widths is not None and (len(widths) != len(headers) or sum(widths) != 100):
        raise ValueError("Table column widths must cover every column and total 100")
    colgroup = ""
    if widths:
        colgroup = "<colgroup>" + "".join(f'<col style="width:{width}%">' for width in widths) + "</colgroup>"
    head = "<thead><tr>" + "".join(f'<th scope="col">{inline(cell)}</th>' for cell in headers) + "</tr></thead>"
    body = "<tbody>" + "".join("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>" for row in rows) + "</tbody>"
    return (
        '<div class="table-panel"><div class="table-scroll">'
        f'<table class="source-table{" dense" if dense else ""}" data-source-table="{table["id"]}">'
        f'<caption>{html.escape(slide["title"])} · 원문 표</caption>{colgroup}{head}{body}</table></div>'
        f'<p class="takeaway">{html.escape(slide.get("takeaway", "원문 표의 문구·행·열을 보존했다."))}</p></div>'
    )


def render_image(image, spec):
    payload = base64.b64encode(verified_bytes(image)).decode("ascii")
    return (
        '<figure class="original-image">'
        f'<img src="data:{image["content_type"]};base64,{payload}" '
        f'data-source-image="{html.escape(image["local_path"])}" '
        f'alt="{html.escape(image["alt"])}" width="{image["width"]}" height="{image["height"]}">'
        f'<figcaption>원문 삽화 그대로 · {html.escape(spec["source_author"])} / WikiDocs</figcaption></figure>'
    )


def build():
    spec = load_json("slides-content.json")
    table_records = load_json("assets/source-tables.json")
    image_records = load_json("assets/source-images.json")
    fonts = load_json("assets/fonts/fonts.json")
    tables = {record["id"]: record for record in table_records}
    images = {record["local_path"]: record for record in image_records}
    slides = spec["slides"]
    table_ids = [slide["table"] for slide in slides if "table" in slide]
    image_paths = [slide["image"] for slide in slides if "image" in slide]
    if len(table_ids) != len(set(table_ids)) or set(table_ids) != set(tables):
        raise ValueError("Each captured original table must appear exactly once")
    if len(image_paths) != len(set(image_paths)) or set(image_paths) != set(images):
        raise ValueError("Each captured original image must appear exactly once")
    page_titles = {table["page_url"]: table["page_title"].split(" - ")[0] for table in table_records}
    page_titles[spec["source_book_url"]] = spec["source_book"]
    page_titles["https://wikidocs.net/353381"] = "2장. LLM위키의 기본 구조"
    rendered = []
    inventory = []
    options = []
    main_count = sum(not slide.get("appendix", False) for slide in slides)
    for number, slide in enumerate(slides, 1):
        plain_title = html.unescape(re.sub(r"<[^>]+>", " ", slide["title"]))
        source_urls = slide.get("sources", [])
        subtitle = slide.get("subtitle", "")
        if slide["kind"] == "table":
            table = tables[slide["table"]]
            body = render_table(table, slide)
            source_urls = [table["page_url"]]
            subtitle = "원문 표 그대로 · 행·열·셀 문구 유지 · 아래 해설은 강의용 설명"
        elif slide["kind"] in ("image", "cover"):
            figure = render_image(images[slide["image"]], spec)
            if slide["kind"] == "cover":
                body = f'<div class="cover-layout"><div>{slide["body"]}</div>{figure}</div>'
            else:
                body = f'<div class="illustration-layout">{figure}<article>{slide["body"]}</article></div>'
        elif slide["kind"] == "sources":
            bibliography = "<ul class=\"bibliography\">" + "".join(
                f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">'
                f'[{identifier}] {html.escape(page_titles[url])}</a><span class="url">{html.escape(url)}</span></li>'
                for url, identifier in sorted(spec["citation_ids"].items(), key=lambda item: item[1])
            ) + "</ul>"
            body = f'<div class="sources-grid"><div>{bibliography}</div><div>{slide["body"]}</div></div>'
        elif slide["kind"] == "inventory":
            stats = f'<p class="inventory-stat">원문 이미지 {len(images)}개 · 원문 표 {len(tables)}개 · 본편 {main_count}장 + 부록 {len(slides)-main_count}장</p>'
            body = stats + slide["body"]
        else:
            body = slide["body"]
        for url in source_urls:
            if url not in spec["citation_ids"] or url not in page_titles:
                raise ValueError(f"Unknown source: {url}")
        citations = "".join(
            f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">'
            f'[{spec["citation_ids"][url]}] {html.escape(page_titles[url])}</a>'
            for url in source_urls
        )
        identifier = f"slide-{number:02d}"
        rendered.append(
            f'<section class="slide" id="{identifier}" data-kind="{slide["kind"]}" '
            f'data-title="{html.escape(plain_title)}" aria-labelledby="heading-{number:02d}" aria-hidden="true">'
            f'<header class="slide-header"><p class="kicker">{html.escape(slide["section"])}</p>'
            f'<h2 id="heading-{number:02d}">{slide["title"]}</h2><p class="subtitle">{html.escape(subtitle)}</p></header>'
            f'<div class="slide-body">{body}</div>'
            f'<footer class="slide-footer"><div class="source-links">{citations}</div>'
            f'<span class="slide-number">{number:02d} / {len(slides):02d}</span></footer></section>'
        )
        options.append(f'<option value="{number}">{number:02d} · {"부록 · " if slide.get("appendix") else ""}{html.escape(plain_title)}</option>')
        inventory.append({"id": identifier, "title": plain_title, "section": slide["section"], "kind": slide["kind"],
                          "appendix": slide.get("appendix", False), "sources": source_urls,
                          "source_table": slide.get("table"), "source_image": slide.get("image")})
    font_css = []
    for font in fonts:
        encoded = base64.b64encode(verified_bytes(font)).decode("ascii")
        font_css.append(f'@font-face{{font-family:"Lecture Noto";font-style:normal;font-weight:{font["weight"]};font-display:swap;src:url(data:font/woff2;base64,{encoded}) format("woff2")}}')
    license_text = (ROOT / "assets/fonts/OFL.txt").read_text(encoding="utf-8")
    substitutions = {"@@TITLE@@": html.escape(spec["title"]), "@@FONTS@@": "\n".join(font_css),
                     "@@SLIDES@@": "\n".join(rendered), "@@OPTIONS@@": "\n".join(options),
                     "@@FONT_LICENSE@@": license_text.replace("--", "—")}
    output = (ROOT / "slides-template.html").read_text(encoding="utf-8")
    for placeholder, value in substitutions.items():
        if placeholder not in output:
            raise ValueError(f"Missing template placeholder: {placeholder}")
        output = output.replace(placeholder, value)
    if re.search(r"@@[A-Z_]+@@", output):
        raise ValueError("Unresolved HTML template placeholder")
    OUTPUT.write_text(output, encoding="utf-8")
    provenance = {"schema_version": "material_artifact/v1", "status": "generated",
                  "format": "offline HTML slide deck", "audience": spec["audience"],
                  "source_author": spec["source_author"], "source_book": spec["source_book"],
                  "output": OUTPUT.name, "html_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
                  "slide_count": len(slides), "main_slide_count": main_count,
                  "appendix_slide_count": len(slides)-main_count, "original_image_count": len(images),
                  "original_table_count": len(tables), "image_transformation": "none; original bytes embedded as base64",
                  "table_transformation": "HTML rendering only; header/row/cell wording and order preserved",
                  "font_license": "SIL Open Font License 1.1; license embedded and supplied in assets/fonts/OFL.txt",
                  "visual_review": "not_completed: image tool returned Gemini HTTP 403 PERMISSION_DENIED",
                  "runtime_qa": "see slides-verification.json", "slides": inventory}
    (ROOT / "slides-provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({key: provenance[key] for key in ("output", "html_sha256", "slide_count", "main_slide_count", "appendix_slide_count", "original_image_count", "original_table_count")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
