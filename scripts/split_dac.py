#!/usr/bin/env python3
"""Split DAC proceedings into per-paper PDFs.

DAC 61 (2024): embedded TOC with a### IDs on pages 1-29, body from page 30.
DAC 62 (2025): no embedded TOC; papers start at page 22, detected via Abstract markers.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import fitz

# DAC 61 (2024) — 3649329
DAC61_TOC_PAGES = 29
DAC61_BODY_START = 30

# DAC 62 (2025) — 3778334
DAC62_BODY_START = 22


def norm(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sanitize(name: str) -> str:
    name = re.sub(r"[^\w\s.-]", "", name)
    return re.sub(r"\s+", "_", name.strip())[:100] or "untitled"


def parse_toc(doc: fitz.Document, toc_pages: int) -> list[tuple[str, str]]:
    toc_text = "".join(doc[i].get_text() + "\n" for i in range(toc_pages))
    entries: list[tuple[str, str]] = []
    for part in re.split(r"\n(?=a\d+\s*\n)", toc_text):
        match = re.match(r"(a\d+)\s*\n(.+?)(?:\n\n|\Z)", part.strip(), re.S)
        if not match:
            continue
        aid, rest = match.group(1), match.group(2).strip()
        lines = [line.strip() for line in rest.splitlines() if line.strip()]
        if lines:
            entries.append((aid, lines[0]))
    return entries


def locate_papers_toc(
    doc: fitz.Document, entries: list[tuple[str, str]], body_start: int
) -> list[tuple[str, str, int]]:
    page_texts = [norm(doc[i].get_text()[:1500]) for i in range(body_start, doc.page_count)]
    located: list[tuple[str, str, int]] = []

    for aid, title in entries:
        probe = norm(title)
        probe = probe[:40] if len(probe) >= 40 else probe[:30]
        start_page = None
        for idx, page_text in enumerate(page_texts):
            if probe in page_text:
                start_page = idx + body_start + 1
                break
        if start_page is not None:
            located.append((aid, title, start_page))

    located.sort(key=lambda item: item[2])
    return located


def is_paper_start(text: str) -> bool:
    head = text[:1500]
    match = re.search(r"Abstract[—\-–]", head)
    if not match or match.start() > 900:
        return False
    pre = head[: match.start()]
    lines = [line.strip() for line in pre.splitlines() if line.strip()]
    return len(lines) >= 1


def extract_title(text: str) -> str:
    match = re.search(r"Abstract[—\-–]", text)
    if not match:
        return "untitled"
    pre = text[: match.start()]
    lines = [line.strip() for line in pre.splitlines() if line.strip()]
    title_lines: list[str] = []
    for line in lines:
        if re.search(
            r"(University|College|Dept\.|Department|Institute|Laboratory|School of|@|\*\d|\d,\d)",
            line,
            re.I,
        ):
            break
        if re.search(r"\d+\s*(College|University|Dept|School)", line, re.I):
            break
        if re.match(r"^[A-Z][^\n]{2,50},\s", line) and re.search(r"\d", line):
            break
        if " and " in line and re.search(r"\d+\*?[, ]", line):
            break
        title_lines.append(line)
    title = " ".join(title_lines).strip()
    title = re.split(r"\s+[A-Z][a-z]+ [A-Z][a-z]+(?:\d|\*)", title)[0].strip()
    return title or "untitled"


def locate_papers_abstract(doc: fitz.Document, body_start: int) -> list[tuple[str, str, int]]:
    located: list[tuple[str, str, int]] = []
    for i in range(body_start - 1, doc.page_count):
        text = doc[i].get_text()
        if not is_paper_start(text):
            continue
        page_num = i + 1
        title = extract_title(text)
        paper_id = f"p{len(located) + 1:03d}"
        located.append((paper_id, title, page_num))
    return located


def split_proceedings(src: Path, out_dir: Path, *, edition: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(src))

    if edition == "61":
        entries = parse_toc(doc, DAC61_TOC_PAGES)
        located = locate_papers_toc(doc, entries, DAC61_BODY_START)
        print(f"TOC entries: {len(entries)}")
    elif edition == "62":
        located = locate_papers_abstract(doc, DAC62_BODY_START)
        print(f"Body starts at page: {DAC62_BODY_START}")
    else:
        raise ValueError(f"Unknown edition: {edition}")

    print(f"Source: {src}")
    print(f"Pages: {doc.page_count}")
    print(f"Matched papers: {len(located)}")
    print(f"Output: {out_dir}")

    for index, (paper_id, title, start_page) in enumerate(located):
        end_page = located[index + 1][2] - 1 if index + 1 < len(located) else doc.page_count
        out_path = out_dir / f"{paper_id}_{sanitize(title)}.pdf"
        split = fitz.open()
        split.insert_pdf(doc, from_page=start_page - 1, to_page=end_page - 1)
        split.save(str(out_path))
        split.close()
        print(
            f"Wrote {out_path.name} "
            f"(pages {start_page}-{end_page}, {end_page - start_page + 1} pp)"
        )

    doc.close()


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Split DAC proceedings into per-paper PDFs")
    parser.add_argument(
        "--edition",
        choices=("61", "62"),
        default="62",
        help="DAC edition: 61 (2024, TOC-based) or 62 (2025, Abstract-based)",
    )
    parser.add_argument("--src", type=Path, help="Source proceedings PDF")
    parser.add_argument("--out", type=Path, help="Output directory for split papers")
    args = parser.parse_args()

    if args.edition == "61":
        src = args.src or next((repo_root / "references").rglob("3649329*.pdf"))
        out_dir = args.out or repo_root / "references" / "DAC(61)" / "papers"
    else:
        src = args.src or (
            repo_root / "references" / "conferences" / "DAC(62) 2025" / "3778334.pdf"
        )
        out_dir = args.out or (
            repo_root / "references" / "conferences" / "DAC(62) 2025" / "papers"
        )

    split_proceedings(src, out_dir, edition=args.edition)
    print("Done.")


if __name__ == "__main__":
    main()
