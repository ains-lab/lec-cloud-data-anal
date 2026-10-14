# 9주차 · 2장. LLM위키의 기본 구조

## 열기

`llm-wiki-chapter-02-slides.html`을 브라우저에서 연다. 이미지와 글꼴을 내장한 단일 HTML이다. 파일 하나만 복사해도 발표·전체 읽기는 동작한다. 하단 원전 링크를 방문할 때만 인터넷이 필요하다.

## 수업 구성

- 학습 목표 → 핵심 개념 → 원문 삽화·비교표 → 가상 학생 프로젝트 사례 → 이해 확인 → 실습과 제출 기준 → 복습.
- 부록의 원문 표는 필요한 경우 선택해서 사용한다. 표의 행·열·셀 문구는 원문을 보존한다.
- 학생은 LLM 사용 경험과 기본 파일·폴더 조작 경험이 있다고 가정한다. 계정·설치가 어려우면 종이나 편집기로 동일한 설계·근거 대조 활동을 한다.
- 실습 사례는 수업용 가상 예시다. 실습 제안·예시 답은 실제 모델 실행, 승인, 측정 성과가 아니다.
- 화면: 화살표 이동, R 전체 읽기, F 전체 화면, 슬라이드 선택 메뉴. 모바일은 전체 읽기로 전환된다.

## 자료와 출처

- 원문 삽화 4개, 원문 표·문서 예시 표 19개.
- `assets/source-images.json`: URL, 무변경 파일 경로, SHA-256, 이미지 크기.
- `assets/source-tables.json`: 원문 머리글·셀 문구·행 순서와 추출된 표 원문.
- `assets/source-pages.json`, `assets/sources/`: 실제 조회한 WikiDocs 본문과 해시. 웹 추출본이며 원본 HTML 캡처라고 주장하지 않는다.
- `assets/source-diagrams.json`: 추출본에 코드로 남아 있는 Mermaid 도해만 보존한다. 슬라이드의 단순화 흐름도는 강의용 재구성으로 구분한다.
- `slides-content.json`: 강의 순서·해설. `slides-provenance.json`: 실제 HTML 해시·자산 수·슬라이드별 출처.
- 원전: 박승규, 『LLM위키 완벽 가이드』, WikiDocs, https://wikidocs.net/book/19830 . 책의 표시된 최종 편집일은 2026-05-16이다.

## 재생성

저장소 루트에서 `python3 docs/lectures/llm-wiki-course/build_course.py --week 9`를 실행한다. 네트워크·모델 호출 없이 보존된 자산을 사용한다. 해당 HTML과 `slides-provenance.json`을 다시 생성한다.

공통 검사: `python3 -m unittest discover -s docs/lectures/llm-wiki-course -p 'test_course.py' -v` . 브라우저 검증의 실제 범위는 공통 `verification.json`을 확인한다. 소스·해시 검사가 곧 전체 시각 검토 또는 학습 효과 검증은 아니다.
