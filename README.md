# 나의 논문 지식 Wiki

개인 논문 원문을 보관하고 요청 시 요약·분석·비교·질의로 연결하는 로컬 Markdown 지식 저장소다. 사용자 본인과 Hermes가 사용하며 별도 DB는 없다.

## 시작점

- [논문 수집 자동화 — 쉬운 안내](docs/lectures/5w/paper-collection.md), [Cron 생성·현재 구성](docs/lectures/5w/paper-collection-cron.md), [설명서 목록](docs/README.md)
- [지식 색인](index.md), [스키마](SCHEMA.md), [에이전트 범위](AGENTS.md), [작업 이력](log.md)
- [AI Agent Security 원본 색인](raw/articles/4cff5b4f10ec/index.md)
- [HTML 원본 수집 규칙](_meta/COLLECTION.md), [정확한 검색식·한도](_meta/topics.json)
- [원본 HTML 직접 llm-wiki 컴파일 전략](_meta/COMPILATION.md)

## 현재 방식

**arXiv 검색 → 동일 버전 HTML 원본 저장 → 사용자가 요청하면 원본을 직접 읽어 llm-wiki 컴파일**

사전 파싱 단계는 없다. PDF 다운로드, fulltext/블록 추출, 이미지/표/페이지 분리, OCR, 구조화·정규화, 전처리 모델 호출 및 전용 환경을 운영 경로에서 제거했다. 정기 수집은 HTML 저장에서 끝나며 자동 지식 컴파일을 하지 않는다.

- 기존 대상 10편 중 **HTML 원본 8편** 저장, **HTML 미제공 2편**은 서지·미확보 상태만 유지한다.
- HTML 미제공: `2609.30614v1`, `2609.30824v1`. 공식 HTML URL 404와 abs 페이지 PDF-only 링크를 확인했다. 초록을 전문으로 저장하지 않았다.
- 사용자 명시 승인에 따라 PDF 10편·기존 전처리 산출물·시험본·전용 환경을 **새 백업 없이 영구 삭제**했다. 미제공 2편의 PDF도 삭제했다.
- 지식 페이지는 **0개**다. 이번 작업은 원본 형식 전환이며 Wiki 컴파일 실행이 아니다.
- 기존 Cron `4cff5b4f10ec`는 HTML 원본 전용으로 변경했다. 매일 **KST 00:00**, 정기 KST 날짜당 최대 5편, local 전달이다. 실제 재개/실행 상태는 Cron 목록과 최신 log를 확인한다.

## 폴더 구조

```text
raw/articles/<cron-id>/
  index.md
  arxiv-<version-id>/
    source.html       # arXiv가 제공한 HTTP HTML 본문 그대로
    source.json       # 서지·버전 고정 URL·시각·크기·SHA-256
entities/             # 수동 컴파일 요청으로 생성할 논문별 분석
concepts/             # 개념 연결
comparisons/          # 비교
queries/              # 질의 답변
_meta/topics.json     # 검색식·HTML 수집 정책
_meta/state/          # checkpoint·pending·HTML 미제공
_meta/runs/           # 정기 실행 근거
_meta/migrations/     # 이번 전환·삭제·검증 기록
```

HTML 미제공 논문에 가짜 원천 폴더/placeholder HTML을 만들지 않는다. 기존 raw/papers, transcripts, assets는 비어 있으며 이번 수집에 사용하지 않는다.

## 원본 그대로 저장한다는 의미

HTML을 Markdown으로 변환하거나 내용을 재작성하지 않는다. 페이지의 외부 이미지·CSS·폰트와 상대 링크도 그대로 유지하므로, 로컬 파일만 열면 일부 그림/스타일이 표시되지 않을 수 있다. 이것은 오프라인 자산 번들이 아니다. 정밀하게 읽을 때에는 source.json의 동일 버전 공식 URL을 기준으로 확인한다.

HTTP 상태·논문 버전·제목/본문 존재·응답 길이·해시 확인은 잘못된 응답을 원본으로 저장하지 않기 위한 검증이다. 문서 내용을 별도 구조로 재구성하는 전처리는 하지 않는다.

## 컴파일 요청 예

“저장된 원본 HTML을 직접 읽고 이 논문을 한국어 논문 페이지로 정리해줘.”

`llm-wiki`는 기존 지식과 중복을 확인하고 원본을 직접 읽어 entities/concepts/comparisons/queries를 작성한다. 원본 버전·HTML 앵커·읽은 범위·미검토 도표를 명시하고 index와 log를 갱신한다. 원문 저장 성공만으로 분석·시각 검토·실험 재현을 완료했다고 표시하지 않는다.

## 보존과 범위

새 HTML 원본은 불변이다. 같은 버전의 다른 응답 해시는 충돌로 기록하고 덮어쓰지 않는다. 새 버전은 별도 보존한다. 이번 영구 삭제 승인은 일반 삭제 권한이 아니며 이후 대량 이동·삭제는 다시 확인한다.

이번 작업에서 새 백업은 만들지 않았고, 이전 초기화 백업·다른 Wiki·DB·Hermes 프로필·Cron·전역 스킬은 접근하거나 변경하지 않았다. log는 과거 경로를 포함한 append-only 이력으로 유지하며 폐기된 전처리 지시를 현재 실행 규칙으로 사용하지 않는다.
