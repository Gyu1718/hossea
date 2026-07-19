# 확장: 「호세아서와 토라」

호세아서 상세 연구본에 **Ⅵ부 · 호세아서와 토라**를 추가하는 확장 패키지.
기존 저장소(`hosea-study`)에 적용한다.

---

## 무엇이 들어 있나

주석들이 제시하는 호세아서와 오경 율법의 상관관계를 정리한 새 부(部).

| 절 | 내용 |
|---|---|
| 1 | **쟁점** — 호세아가 아는 "토라"는 무엇인가. 여섯 입장 대조표(Stuart 직접 의존 / Moon 누적 논증 / Dearman 공통 전승 / Keil 전제된 오경 / Goldingay 유보 / 비평 다수설)와 순환 논증 경고 |
| 2 | **8:12 크럭스** — "내 율법을 만 가지로 기록하였으나". 기록된 토라를 알았는가에 대한 Dearman의 정밀 분석 |
| 3 | **언약 저주와 축복의 틀** — Stuart의 저주 27유형 분류 중 호세아에 반향되는 16유형을 오경 근거와 함께 표로 |
| 4 | **신명기 32장(모세의 노래)** — Dearman이 정리한 14개 병행을 표로 |
| 5 | **십계명과 4:2** |
| 6 | **개별 법조문의 반향** — 호세아 32개 구절 ↔ 토라 본문 ↔ 관계 유형(인용에 가까움/인유/주제적) ↔ 출처 |
| 7 | **창세기·출애굽 전승** — 야곱 유형론, 광야의 이중성 |
| 8 | **종합** — 신학적 함의와 설교 착안점 |

표 4개, 히브리어 26곳, 일곱 주석 모두 반영.

---

## 설치

### 자동 (권장)

```bash
python3 install.py /경로/hosea-study
```

무엇이 바뀌는지 먼저 보려면:

```bash
python3 install.py /경로/hosea-study --dry-run
```

스크립트가 하는 일 — 대상이 올바른 저장소인지 확인하고, 바꾸는 파일을 `.bak`으로
백업한 뒤 복사하고, 마지막에 `build.py`를 실행해 검증까지 마친다.
빌드가 실패하면 중단하므로 깨진 상태로 남지 않는다.

설치 후 확인이 끝나면:

```bash
cd /경로/hosea-study
rm build.py.bak src/_head.html.bak
git add -A && git commit -m "Ⅵ부 호세아서와 토라 추가"
```

### 수동

세 파일을 저장소에 복사하면 된다.

| 파일 | 성격 | 설명 |
|---|---|---|
| `src/05b-torah.html` | 신규 | 새 부의 본문 |
| `src/_head.html` | 교체 | 목차를 `<!-- BUILD:TOC -->` 마커로 대체 |
| `build.py` | 교체 | 부 번호·목차 자동 생성 기능 추가 |

복사 후 `python3 build.py`를 실행한다.

---

## 이 확장이 바꾸는 것

새 부가 **Ⅵ부**로 들어가고, 뒤의 세 부가 한 칸씩 밀린다.

```
        기존                          확장 후
  Ⅴ. 상호 참조                  Ⅴ. 상호 참조
                          →     Ⅵ. 호세아서와 토라   ← 신규
  Ⅵ. 복음적 해석                Ⅶ. 복음적 해석
  Ⅶ. 쟁점 대조표                Ⅷ. 쟁점 대조표
  Ⅷ. 연구 서지                  Ⅸ. 연구 서지
```

**기존 본문 파일은 하나도 고치지 않는다.** `build.py`가 부 번호(`PART Ⅵ` 등)와
사이드바 목차를 자동으로 생성하도록 바뀌었기 때문이다. 이 구조 덕분에 앞으로
새 부를 더할 때도 `src/`에 파일을 넣고 `build.py`의 `PARTS` 목록에 한 줄만
추가하면 된다.

---

## 앞으로 부를 더 추가하려면

`build.py`의 `PARTS` 목록에 항목을 넣는다. 순서·번호·목차가 모두 따라온다.

```python
{"file": "05c-reception.html", "anchor": "part-reception",
 "toc": "수용사", "numbered": True, "sub": []},
```

새 본문 파일은 다음 형태를 지키면 된다. `PART` 뒤의 숫자는 아무 값이나 써도
빌드가 덮어쓴다.

```html
<section class="part" id="part-reception">
  <div class="part-head">
    <div class="heb">…</div>
    <div class="eyebrow">PART Ⅹ</div>
    <h2>제목</h2>
    <div class="gloss">부제</div>
  </div>
  …
  <div class="back"><a href="#top">↑ 처음으로</a></div>
</section>
```

---

## 되돌리기

```bash
cd /경로/hosea-study
mv build.py.bak build.py
mv src/_head.html.bak src/_head.html
rm src/05b-torah.html
python3 build.py
```

또는 커밋 전이라면 `git checkout -- .` 후 `rm src/05b-torah.html`.

---

## 인용 주의

새 부의 표에 실린 "관계" 분류(인용에 가까움 / 인유 / 주제적)는 주석들의 판단을
정리한 것이지 **합의된 결론이 아니다**. 특히 문헌적 의존을 주장하려면 신명기
연대 논의를 함께 다뤄야 한다. 본문의 마지막 경고 상자와 저장소의 `NOTICE.md`를
함께 볼 것.
