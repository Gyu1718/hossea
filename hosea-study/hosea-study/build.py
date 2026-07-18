#!/usr/bin/env python3
"""
호세아서 상세 연구본 — 빌드 스크립트

src/ 의 조각 파일들을 하나의 index.html 로 합치고, 기본 유효성을 검사한다.

사용법:
    python3 build.py           # index.html 생성 + 검증
    python3 build.py --check   # 생성하지 않고 검증만 (CI 용)

의존성 없음 (표준 라이브러리만 사용).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "index.html"

# 본문 순서 — 파일명: 구분선에 넣을 라벨
PARTS: list[tuple[str, str]] = [
    ("00-overview.html", "개요"),
    ("01-background.html", "Ⅰ부 · 배경 연구"),
    ("02-exegesis.html", "Ⅱ부 · 각 장 주해"),
    ("03-preacher.html", "Ⅲ부 · 설교자를 위한 신학적 메시지"),
    ("04-theology.html", "Ⅳ부 · 신학적 메시지"),
    ("05-crossrefs.html", "Ⅴ부 · 상호 참조"),
    ("06-evangelical.html", "Ⅵ부 · 복음적 해석"),
    ("07-issues-table.html", "Ⅶ부 · 쟁점 대조표"),
    ("08-bibliography.html", "Ⅷ부 · 연구 서지"),
]

BAR = "═" * 14


def read(name: str) -> str:
    path = SRC / name
    if not path.exists():
        sys.exit(f"[오류] 파일이 없습니다: {path}")
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def build() -> str:
    chunks = [read("_head.html")]

    for i, (name, label) in enumerate(PARTS):
        chunks.append("")
        # 개요 앞에는 구분선을 넣지 않는다 (히어로 바로 뒤이므로)
        if i > 0:
            chunks.append('<hr class="furrow">')
            chunks.append("")
        chunks.append(f"<!-- {BAR} {label} {BAR} -->")
        chunks.append(read(name).rstrip())

    chunks.append("")
    chunks.append(read("_foot.html").rstrip())
    chunks.append("")
    return "\n".join(chunks)


def validate(html: str) -> list[str]:
    """치명적 문제만 오류로 보고한다."""
    errors: list[str] = []

    # 1) 목차 앵커가 실제 id 로 연결되는가
    anchors = set(re.findall(r'href="#([\w-]+)"', html))
    ids = set(re.findall(r'id="([\w-]+)"', html))
    missing = anchors - ids - {"top"}
    if missing:
        errors.append(f"연결되지 않는 목차 앵커: {sorted(missing)}")

    # 2) 주요 태그 균형
    for tag in ("html", "head", "body", "main", "nav", "footer",
                "section", "div", "table", "tr", "td", "th", "ol", "ul"):
        opened = len(re.findall(rf"<{tag}[ >]", html))
        closed = len(re.findall(rf"</{tag}>", html))
        if opened != closed:
            errors.append(f"<{tag}> 태그 불균형: 여는 태그 {opened}개 / 닫는 태그 {closed}개")

    # 3) 문서가 한 번만 닫히는가
    for tag in ("</html>", "</body>", "</main>"):
        if html.count(tag) != 1:
            errors.append(f"{tag} 가 {html.count(tag)}번 나타납니다 (1번이어야 함)")

    # 4) 섹션 개수
    n = len(re.findall(r'<section class="part"', html))
    if n != len(PARTS):
        errors.append(f"섹션 개수 불일치: {n}개 (예상 {len(PARTS)}개)")

    return errors


def report(html: str) -> None:
    stats = {
        "줄 수": html.count("\n"),
        "용량(KB)": round(len(html.encode("utf-8")) / 1024, 1),
        "섹션": len(re.findall(r'<section class="part"', html)),
        "장 블록": len(set(re.findall(r'id="(ch\d+)"', html))),
        "히브리어": html.count('class="hw"'),
        "주석 칩": len(re.findall(r'class="c [a-z]+"', html)),
        "표": html.count("<table>"),
        "한글 글자": len(re.findall(r"[가-힣]", html)),
    }
    print("  " + " · ".join(f"{k} {v}" for k, v in stats.items()))


def main() -> None:
    check_only = "--check" in sys.argv
    html = build()

    errors = validate(html)
    if errors:
        print("검증 실패:")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)

    print("검증 통과 ✓")
    report(html)

    if check_only:
        print("(--check 모드: 파일을 쓰지 않았습니다)")
        return

    OUT.write_text(html, encoding="utf-8")
    print(f"생성 완료 → {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
