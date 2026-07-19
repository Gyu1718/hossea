#!/usr/bin/env python3
"""
호세아서 연구본 — 「호세아서와 토라」 확장 설치 스크립트

기존 저장소(hosea-study)에 이 확장을 적용한다.
바꾸기 전에 원본을 .bak 으로 백업하고, 마지막에 빌드까지 실행해 확인한다.

사용법:
    python3 install.py /경로/hosea-study      # 설치
    python3 install.py /경로/hosea-study --dry-run   # 무엇이 바뀌는지만 보기

의존성 없음 (표준 라이브러리만 사용).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (확장 안의 경로, 저장소 안의 경로, 성격)
FILES = [
    ("src/05b-torah.html", "src/05b-torah.html", "신규"),
    ("src/_head.html",     "src/_head.html",     "교체"),
    ("build.py",           "build.py",           "교체"),
]

# 설치 대상이 맞는지 확인할 파일들
REQUIRED = ["build.py", "src/_head.html", "src/02-exegesis.html", "index.html"]


def fail(msg: str) -> None:
    sys.exit(f"[중단] {msg}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv

    if not args:
        fail("설치할 저장소 경로를 지정하세요.\n"
             "  예: python3 install.py ~/hosea-study")

    repo = Path(args[0]).expanduser().resolve()
    if not repo.is_dir():
        fail(f"디렉터리가 아닙니다: {repo}")

    missing = [f for f in REQUIRED if not (repo / f).exists()]
    if missing:
        fail(f"호세아 연구본 저장소가 아닌 것 같습니다.\n"
             f"  다음 파일이 없습니다: {', '.join(missing)}")

    print(f"대상 저장소: {repo}")
    print(f"{'(모의 실행 — 아무것도 바꾸지 않습니다)' if dry else ''}\n")

    for rel_src, rel_dst, kind in FILES:
        src, dst = HERE / rel_src, repo / rel_dst
        if not src.exists():
            fail(f"확장 파일이 없습니다: {src}")

        if dst.exists():
            if dst.read_bytes() == src.read_bytes():
                print(f"  = {rel_dst} (이미 같음, 건너뜀)")
                continue
            print(f"  {'~' if kind == '교체' else '+'} {rel_dst} ({kind}, 백업 → {dst.name}.bak)")
            if not dry:
                shutil.copy2(dst, dst.with_suffix(dst.suffix + ".bak"))
        else:
            print(f"  + {rel_dst} ({kind})")

        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    if dry:
        print("\n모의 실행을 마쳤습니다. 실제로 적용하려면 --dry-run 을 빼고 실행하세요.")
        return

    print("\n파일 적용 완료. 빌드를 실행합니다.\n")
    result = subprocess.run([sys.executable, "build.py"], cwd=repo)
    if result.returncode != 0:
        fail("빌드에 실패했습니다. .bak 파일로 되돌린 뒤 INSTALL.md 를 확인하세요.")

    print("\n설치가 끝났습니다.")
    print("  · index.html 을 열어 Ⅵ부「호세아서와 토라」를 확인하세요.")
    print("  · 문제가 없으면 .bak 파일을 지우고 커밋하면 됩니다:")
    print("      rm src/_head.html.bak build.py.bak")
    print('      git add -A && git commit -m "Ⅵ부 호세아서와 토라 추가"')


if __name__ == "__main__":
    main()
