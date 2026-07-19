#!/usr/bin/env python3
"""
호세아서 상세 연구본 — 빌드 스크립트

src/ 의 조각 파일들을 하나의 index.html 로 합치고, 기본 유효성을 검사한다.
부 번호(PART Ⅰ, Ⅱ …)와 사이드바 목차는 아래 PARTS 목록에서 자동 생성되므로,
새 부를 추가할 때 기존 파일을 고칠 필요가 없다.

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

# ─────────────────────────────────────────────────────────────
# 본문 구성 — 여기만 고치면 순서 · 부 번호 · 목차가 모두 따라온다.
#
#   file      : src/ 안의 파일명
#   anchor    : 그 부의 <section id="...">  (목차 링크 대상)
#   toc       : 목차에 표시할 이름. None 이면 목차에서 제외
#   numbered  : True 면 PART 번호를 자동 부여 (개요는 False)
#   sub       : 목차 하위 항목 [(앵커, 라벨), ...]
# ─────────────────────────────────────────────────────────────
PARTS: list[dict] = [
    {"file": "00-overview.html", "anchor": "overview",
     "toc": "개요·주석 프로필", "numbered": False, "sub": []},

    {"file": "01-background.html", "anchor": "part1",
     "toc": "배경 연구", "numbered": True,
     "sub": [("p1-person", "인물·출신"),
             ("p1-history", "역사 배경·사료"),
             ("p1-marriage", "호세아의 결혼(핵심 쟁점)"),
             ("p1-cult", "제의·바알·지식")]},

    {"file": "02-exegesis.html", "anchor": "part2",
     "toc": "각 장 주해", "numbered": True,
     "sub": [("ch1", "1–3장 · 결혼 서사"),
             ("ch4", "4–7장 · 소송과 타락"),
             ("ch8", "8–10장 · 파종과 심판"),
             ("ch11", "11–14장 · 사랑·부활·귀향")]},

    {"file": "03-preacher.html", "anchor": "part-preacher",
     "toc": "설교자를 위한 메시지", "numbered": True, "sub": []},

    {"file": "04-theology.html", "anchor": "part3",
     "toc": "신학적 메시지", "numbered": True, "sub": []},

    {"file": "05-crossrefs.html", "anchor": "part4",
     "toc": "상호 참조", "numbered": True, "sub": []},

    {"file": "05b-torah.html", "anchor": "part-torah",
     "toc": "호세아서와 토라", "numbered": True, "sub": []},

    {"file": "06-evangelical.html", "anchor": "part5",
     "toc": "복음적 해석", "numbered": True, "sub": []},

    {"file": "07-issues-table.html", "anchor": "part6",
     "toc": "쟁점 대조표", "numbered": True, "sub": []},

    {"file": "08-bibliography.html", "anchor": "part7",
     "toc": "연구 서지", "numbered": True, "sub": []},
]

ROMAN = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ", "Ⅺ", "Ⅻ"]
BAR = "═" * 14
TOC_MARKER = "<!-- BUILD:TOC -->"


def read(name: str) -> str:
    path = SRC / name
    if not path.exists():
        sys.exit(f"[오류] 파일이 없습니다: {path}")
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def numbering() -> dict[str, str]:
    """부 파일명 → 로마 숫자"""
    out, n = {}, 0
    for part in PARTS:
        if part["numbered"]:
            if n >= len(ROMAN):
                sys.exit("[오류] 로마 숫자가 부족합니다. ROMAN 을 늘리세요.")
            out[part["file"]] = ROMAN[n]
            n += 1
    return out


def build_toc(nums: dict[str, str]) -> str:
    lines = []
    for part in PARTS:
        if not part["toc"]:
            continue
        label = part["toc"]
        if part["numbered"]:
            label = f'{nums[part["file"]]}. {label}'
        lines.append(f'    <a class="lv1" href="#{part["anchor"]}">{label}</a>')
        for anchor, sublabel in part["sub"]:
            lines.append(f'    <a class="lv2" href="#{anchor}">{sublabel}</a>')
    return "\n".join(lines)


def build() -> str:
    nums = numbering()

    head = read("_head.html")
    if TOC_MARKER not in head:
        sys.exit(f"[오류] src/_head.html 에 {TOC_MARKER} 가 없습니다.")
    head = head.replace(TOC_MARKER, build_toc(nums))

    chunks = [head.rstrip()]

    for i, part in enumerate(PARTS):
        body = read(part["file"]).rstrip()

        # 부 번호 자동 부여
        if part["numbered"]:
            body, n = re.subn(r'(<div class="eyebrow">)PART\s*[^<]*(</div>)',
                              rf'\g<1>PART {nums[part["file"]]}\g<2>', body, count=1)
            if n == 0:
                sys.exit(f'[오류] {part["file"]} 에 <div class="eyebrow">PART …</div> 가 없습니다.')

        label = part["toc"] or "개요"
        if part["numbered"]:
            label = f'{nums[part["file"]]}부 · {label}'

        chunks.append("")
        if i > 0:                       # 개요 앞에는 구분선을 넣지 않는다
            chunks.append('<hr class="furrow">')
            chunks.append("")
        chunks.append(f"<!-- {BAR} {label} {BAR} -->")
        chunks.append(body)

    chunks.append("")
    chunks.append(read("_foot.html").rstrip())
    chunks.append("")
    return "\n".join(chunks)


def validate(html: str) -> list[str]:
    """치명적 문제만 오류로 보고한다."""
    errors: list[str] = []

    anchors = set(re.findall(r'href="#([\w-]+)"', html))
    ids = set(re.findall(r'id="([\w-]+)"', html))
    missing = anchors - ids - {"top"}
    if missing:
        errors.append(f"연결되지 않는 목차 앵커: {sorted(missing)}")

    for part in PARTS:                  # 각 부의 앵커가 실제로 있는가
        if f'id="{part["anchor"]}"' not in html:
            errors.append(f'{part["file"]} 의 앵커 #{part["anchor"]} 를 찾을 수 없습니다')

    for tag in ("html", "head", "body", "main", "nav", "footer",
                "section", "div", "table", "tr", "td", "th", "ol", "ul"):
        opened = len(re.findall(rf"<{tag}[ >]", html))
        closed = len(re.findall(rf"</{tag}>", html))
        if opened != closed:
            errors.append(f"<{tag}> 태그 불균형: 여는 태그 {opened}개 / 닫는 태그 {closed}개")

    for tag in ("</html>", "</body>", "</main>"):
        if html.count(tag) != 1:
            errors.append(f"{tag} 가 {html.count(tag)}번 나타납니다 (1번이어야 함)")

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
