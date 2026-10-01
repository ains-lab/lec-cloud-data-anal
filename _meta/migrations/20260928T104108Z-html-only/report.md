# HTML 원본 전용 전환 결과

- 완료시각: 2026-09-28T10:55:48.928660+00:00
- 범위: 기존 arXiv 논문 **10편**. 신규 논문 검색·수집은 수행하지 않았다.
- 결과: **동일 버전 HTML 원본 8편 저장 / 공식 HTML 미제공 2편**. 10편 모두 HTML 저장 성공이라고 보고하지 않는다.
- 사용자 승인: 기존 PDF·추출 이미지/표·전처리 시험본·전용 환경을 **새 백업 없이 영구 삭제**, HTML 미제공 2편도 PDF 삭제, HTML 원본 전용 Cron 재개.

## 원본 저장

원본은 `raw/articles/4cff5b4f10ec/arxiv-<version-id>/source.html`과 최소 `source.json`이다. arXiv가 반환한 HTTP 본문을 그대로 보존했으며 Markdown 변환, DOM 재직렬화, HTML 내용/링크 변경, 그림/표 추출·분할·렌더링을 하지 않았다. HTTP 200·응답 형식·동일 버전 최종 URL·제목/본문 존재·응답 길이·SHA-256 및 로컬 재읽기 일치를 검증했다.

| 버전 | 결과 |
| --- | --- |
| [2609.30217v1](https://arxiv.org/abs/2609.30217v1) | 원본 HTML 저장·해시 검증 |
| [2609.30266v1](https://arxiv.org/abs/2609.30266v1) | 원본 HTML 저장·해시 검증 |
| [2609.30614v1](https://arxiv.org/abs/2609.30614v1) | **HTML 미제공 · 로컬 전문 없음** |
| [2609.30824v1](https://arxiv.org/abs/2609.30824v1) | **HTML 미제공 · 로컬 전문 없음** |
| [2609.30830v1](https://arxiv.org/abs/2609.30830v1) | 원본 HTML 저장·해시 검증 |
| [2609.30940v1](https://arxiv.org/abs/2609.30940v1) | 원본 HTML 저장·해시 검증 |
| [2609.31039v1](https://arxiv.org/abs/2609.31039v1) | 원본 HTML 저장·해시 검증 |
| [2609.31318v1](https://arxiv.org/abs/2609.31318v1) | 원본 HTML 저장·해시 검증 |
| [2609.31358v1](https://arxiv.org/abs/2609.31358v1) | 원본 HTML 저장·해시 검증 |
| [2609.31562v1](https://arxiv.org/abs/2609.31562v1) | 원본 HTML 저장·해시 검증 |

공식 HTML 미제공 2편은 `/html/<version-id>`의 HTTP 404와 공식 abs의 PDF-only fulltext 링크를 확인했다. state의 `html_unavailable`에 확인시각과 7일 후 재확인 시각을 기록했다. 초록 페이지·PDF 변환본·제3자 HTML로 대체하지 않았고 해당 raw 폴더/가짜 HTML을 만들지 않았다.

## 제거한 기능·파일

- PDF 원본 10편과 fulltext/blocks/pages/images/tables/parsing/revisions 및 모델 응답·시험본
- 이전 PDF/파싱 staging·run/validation 결과와 전용 `_meta/pdf-env`, requirements, 페이지/텍스트 파싱 prompt, 파싱 전략 제안
- topics의 파서·fallback·text_structuring 설정 및 Cron의 pdf 스킬/파싱 절차
- 삭제 대상 파일 수: **1805개**. 스코프와 실행은 `deletion-scope.json`, `cutover.json`에 기록했다. 새 백업은 만들지 않았다. 이전 별도 백업·다른 Wiki·DB·프로필·Cron·전역 스킬은 건드리지 않았다.
- log는 과거 경로를 포함한 append-only 이력으로 유지한다. 폐기된 이력의 파일이 더 이상 존재하지 않을 수 있으며 이력을 실행 정책으로 쓰지 않는다.

## 운영·직접 컴파일 전략

- SCHEMA/AGENTS/README/COLLECTION/topics/state/root index/topic index를 HTML 원본 전용으로 바꿨다.
- `_meta/COMPILATION.md`: 수동 요청 시 `llm-wiki`가 원본 HTML을 직접 읽어 지식 페이지를 만든다. 사전 파싱본이나 별도 compiler 입력 graph를 요구하지 않는다.
- 이번 전환에서 Wiki 컴파일·요약·도표 시각 분석·과학적 검토는 하지 않았고 지식 페이지는 **0개**다.
- Cron `4cff5b4f10ec` 재개를 실제 읽기 확인했다: enabled=true, skills=[arxiv], script/monitor/continuity/context_from 없음. 모델은 도구 조정용 `codex-lb/gpt-6-astra/xhigh`를 유지하며 전처리용 외부 호출은 없다.
- 매일 KST 00:00, 일일 최대 5편, local 전달. 다음 예정: **2026-09-29T00:00:00+09:00**.
- 기존 discovery floor/checkpoint와 KST 날짜별 시도 기록은 유지했다. 이번 전환으로 신규 검색 범위를 넓히거나 일일 한도를 초기화하지 않았다.
- 실제 HTML 다운로드와 파일 검증은 완료했다. 새 정책의 정기 Cron 전체 실행을 지금 별도로 발화하지 않았으므로 end-to-end 정기 실행 성공으로 표시하지 않는다. Cron의 과거 interrupted_policy_change 기록을 이번 실행 성공으로 조작하지 않았다.

## 제한과 검증

- HTML 파일은 원본 그대로이며 외부 이미지/CSS/폰트는 별도로 저장하지 않았다. 완전한 오프라인 번들이 아니므로 로컬 파일 화면에서 일부 자산·스타일이 보이지 않을 수 있다. 필요할 때 version-pinned source_url을 기준으로 읽는다.
- 실제 HTML 8편 전체 ID/제목/길이/해시 확인, 미제공 2편과의 중복 없는 합계 10편 대조, 변조 바이트/다른 버전/404 응답 거부 검사 3건 통과.
- 활성 Wiki에 PDF/PNG/SVG/CSV/전처리 Python 코드·가상환경 없음, 지식 디렉터리 변경 없음, 원래 log 바이트 접두 보존을 검증했다. HTML 내부의 원래 SVG는 원문의 일부로 유지된다.
- 원본 보존 검증은 논문 내용의 사실성·수식/도표 의미 검토·실험 재현 성공이 아니다.

## 근거

- [수집 결과](downloads.json), [미제공 확인](html-unavailable-evidence.json), [삭제·게시](cutover.json)
- [원본/상태 전수 검증](validation.json), [검색 checkpoint 보존](checkpoint-verification.json)
- [Cron 재개 읽기 확인](cron-after-resume.json), [기계 판독 보고서](report.json)
