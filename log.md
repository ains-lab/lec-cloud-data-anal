# 논문 Wiki 작업 이력

실제 수행한 작업만 추가하는 append-only 기록이다. 원천 보존, 기계적 검사, 의미적 검토, 실험 재현을 구분한다.

## [2026-09-28] create | 개인 논문 Wiki 빈 구조 재시작

- 사용자 승인: 기존 전체 백업 후 빈 llm-wiki 구조로 시작, 기존 논문 수집 Cron 제거, 커스텀 논문 수집 스킬 삭제. 후속 요청: 논문 수집·분석·질의·요약을 위한 개인 지식 폴더와 스키마 생성.
- 독자: 사용자 본인과 Hermes. 목적지: `/home/ainsdev/wiki/pkm-articles`. 관리 책임: 사용자 본인, 재사용 시 및 주 1회 점검 권장.
- 이전 Wiki의 PDF·원문·자산·수집 코드·환경·이력을 새 Wiki로 옮기지 않는다. 이전 전체 자료와 삭제 대상 스킬은 외부 백업에 보존한다.
- 백업 위치: `/home/ainsdev/wiki-backups/pkm-articles-reset-20260928T054657Z/`. 보존 검증은 `backup-verification.json`, 초기화 최종 검증은 실제 생성되는 `final-verification.json`에서 확인한다. 이 로그만으로 해당 검증이 완료됐다고 추정하지 않는다.
- 생성 파일: `README.md`, `SCHEMA.md`, `AGENTS.md`, `index.md`, `log.md`.
- 생성 폴더: `raw/`, `raw/papers/`, `raw/articles/`, `raw/transcripts/`, `raw/assets/`, `entities/`, `concepts/`, `comparisons/`, `queries/`.
- 시작 상태: 원천 자료 0개, 지식 페이지 0개. 논문 검색·다운로드·요약·실험을 수행하지 않는다.
- 기본 스킬 사용 분담: arxiv=검색·서지, pdf=원문 처리, llm-wiki=요약·분석·지식 연결·질의. 자동 수집이나 별도 모델 실행은 구성하지 않는다.
- 논문 수집 Cron은 전환 준비 시 현재 목록에 이미 없음을 확인했다. 다른 Cron과 기존 SQLite DB·팀 Wiki는 변경 범위 밖이다.
- 백업 이후 기존 작업 폴더가 이미 빈 상태로 바뀐 것을 확인해 원래 전환 절차의 안전 검사가 중단됐다. 변경 원인은 확인하지 않았다. 검증된 압축 백업에서 이전 Wiki 사본을 외부 `retired-wiki/`로 복구하고, 현재 빈 작업 폴더에 새 구조를 배치한다. 이 기록은 초기화 도중 생성한 새 논문이나 지식이 있다는 뜻이 아니다.

## [2026-09-28] lint | 초기화와 보존 검증 완료

- 실제 검증 시각: `2026-09-28T06:10:04.884523+00:00`. 검증 명령 종료 코드 0, 최종 상태 `passed`.
- 새 Wiki: 운영 문서 5개, 디렉터리 9개, 로컬 Markdown 링크 12개 확인. 원천 파일 0개, 지식 페이지 0개.
- 백업: archive member 1194개, 일반 파일 1099개, 심볼릭 링크 4개를 manifest와 대조했다. 별도로 복구한 이전 Wiki 사본도 기존 파일 해시·모드·수정시각과 일치했다.
- `paper-collection`은 실제 삭제 후 스킬 목록에서 부재를 확인했다. `llm-wiki`의 삭제 스킬 참조를 제거하고, 남겨 둔 legacy `paper-summary`에는 제거된 컴파일러·스케줄을 실행하지 않도록 경계를 명시했다.
- 논문 수집 Cron과 개인 수집 래퍼는 최종 조회 시 존재하지 않는다. 둘 다 전환 전에 이미 사라진 상태였으므로 이번 작업이 이들을 삭제했다고 주장하지 않는다. 다른 Cron의 설정은 초기 조회와 동일하다.
- 보호 범위인 기존 SQLite DB와 팀 Wiki의 파일·메타데이터가 초기 스냅샷과 일치함을 확인했다. 이 작업에서 논문 수집·다운로드·별도 모델 분석을 실행하지 않았다.
- 근거: 외부 백업 폴더의 `cutover.json`, `final-verification.json`, `manifest.json`, `backup-verification.json` 및 실제 Hermes 스킬/Cron 조회 결과.

## [2026-09-28] create | 주제별 원천 수집 Cron 구성 및 사전 검증

- 사용자 요청: 매일 KST 00:00 키워드 수집, Cron ID별 raw/articles 저장, DB 없는 중복 관리, PDF 멀티모달 사전 파싱, Wiki 컴파일 금지.
- 검색식은 `_meta/topics.json`에 사용자 원문과 arXiv all: 필드 표현을 함께 보존했다. 주제는 AI Agent Security, Cron ID는 `4cff5b4f10ec`다. 최초 최근 24시간, 이후 48시간 겹침(최초 하한 유지), KST 일일 최대 5편 정책이다.
- Hermes Cron을 우선 paused로 생성하고, 사용자 지정 `codex-lb/gpt-6-astra` 및 reasoning `xhigh`로 고정한 것을 실제 readback으로 확인했다. 현재 UTC 스케줄러에서 표현식은 `0 15 * * *`다. 활성화 여부는 후속 실제 결과를 기준으로 한다.
- `_meta/COLLECTION.md`, `_meta/topics.json`, `_meta/state/4cff5b4f10ec.json`, `_meta/page-parsing-prompt.txt`, 주제별 원천 index와 staging/run/lock 경로를 준비했다. SCHEMA, README, AGENTS, 루트 index에 수집 전용 경계를 반영했다. 커스텀 수집 스킬/실행 프로그램이나 별도 DB는 만들지 않았다.
- 승인받은 PyMuPDF 1.28.2를 `_meta/pdf-env` 격리 환경에 설치했다. Hermes 전역 환경·모델 설정·다른 Cron은 변경하지 않았다.
- 실제 arXiv 직접 API는 HTTP 406이었다. 같은 Boolean 검색의 browser DOM XML을 확인하고 Atom updated 내림차순·ID 유일성을 검사했다. 최근 24시간 대상은 0편이다. `lastUpdatedDate:[...]` 검색 조건이 submittedDate로 재작성된 것을 관측하여 갱신일 필터는 Atom updated 기반으로 변경했다. 근거: `_meta/validation/search-verification.json`과 저장된 검색 응답.
- 명시적인 합성 PDF fixture로 실제 GPT 이미지 호출, 표 숫자·그림 판독, page JSON 구조, fulltext·figure/table crop 패키지와 hash 검사를 수행했다. 재확인 no-op, 손상 거부, 독점 잠금, pending/checkpoint 절차를 fixture로 검사했다. 근거: `_meta/validation/*vision-probe.json`, `fixture-page-0001.json`, `package-verification.json`. fixture는 논문 원천이 아니며 raw에 게시하지 않았다.
- Gemini fallback 실제 호출은 HTTP 403으로 실패했다. 사용자는 이 제한을 명시한 상태에서 GPT 경로 활성화를 승인했다. 대체 경로 정상 작동을 주장하지 않는다. 실제 논문 전체 파싱과 실제 다주제 중복은 아직 관측되지 않았다.
- 지식 페이지 작성·llm-wiki 컴파일은 수행하지 않았다. 최근 1일 대상이 없으므로 실제 원천 논문은 아직 0편이다.


## [2026-09-28] update | AI Agent Security 실제 수동 실행 — 정상 검색 0편

- Cron `4cff5b4f10ec`, run `20260928T070713Z-928cbe2a`. 기존 validation 검색을 재사용하지 않고 최신 arXiv를 실제 조회했다.
- 최초 24시간 범위: `2026-09-27T16:07:13.632288+09:00` ~ `2026-09-28T16:07:13.632288+09:00` (KST). `first_window_floor`를 영구 저장하고, 빈 pending을 먼저 원자적으로 저장한 뒤 `discovered_through`를 `2026-09-28T07:07:13.632288+00:00`로 전진시켰다.
- 등록된 Boolean 식·lastUpdatedDate 내림차순 유지. 직접 API HTTP 406은 동일 URL의 실제 브라우저 `pre.textContent` XML로 회복했다. 저장 자료는 HTTP 원본 바이트가 아닌 DOM 텍스트 캡처다.
- 응답 100개의 실제 version ID 유일성·형식, updated 내림차순, XML/건수를 검사했다. 가장 최근 updated `2026-09-25T17:28:53Z`도 하한 이전이어서 첫 페이지에서 종료했다. 범위 내 후보 0편은 오류에 의한 빈 결과가 아니다.
- 신규 완료 0편, 재사용 0편, 새 주제 참조 0편, 파싱 시도 0편, 실패 논문 0편, pending 0편. KST 일일 사용 0/5편, 연속 실패 0회, safety_block=false.
- `raw/articles/`의 source/complete/reference, `raw/papers/`, 해당 staging을 확인했으며 기존 실제 원천·미완료 패키지는 없다. 완료 manifest의 해시/coverage 재사용과 실제 논문 전체 파싱·다주제 중복은 대상이 없어 실증하지 않았다. 모델 호출·PDF 다운로드·fixture 게시·Wiki 컴파일은 수행하지 않았다.
- 갱신: `_meta/state/4cff5b4f10ec.json`, `raw/articles/4cff5b4f10ec/index.md`, `log.md`; 신규 실행 증거: `_meta/runs/4cff5b4f10ec/20260928T070713Z-928cbe2a/`. 루트 index와 지식 페이지는 변경하지 않았다.
- 보고서: `_meta/runs/4cff5b4f10ec/20260928T070713Z-928cbe2a/report.json`; 검색 검증: `_meta/runs/4cff5b4f10ec/20260928T070713Z-928cbe2a/search-verification-0000.json`; 최종 로컬 검증: `_meta/runs/4cff5b4f10ec/20260928T070713Z-928cbe2a/final-verification.json`; 본 실행 소유 잠금 해제 결과: `_meta/runs/4cff5b4f10ec/20260928T070713Z-928cbe2a/lock-release.json`.

## [2026-09-28] lint | Cron 활성화 및 수동 실행 독립 검증 완료

- 실제 Cron 목록에서 `4cff5b4f10ec`의 enabled=true, state=scheduled, last_status=ok를 재확인했다. 다음 정기 실행은 `2026-09-29T00:00:00+09:00`이다. 다른 Cron 2개는 유지되어 있고 중복 논문 Cron을 추가하지 않았다.
- `2026-09-28T07:13:39.640471+00:00`에 실행 증거 파일 14개의 해시·크기를 재계산하고 실제 Atom XML을 독립 파싱했다. 검색식·정렬·100개 ID 유일성·검색 범위 내 후보 0편을 확인했다. 상태 checkpoint·보고서 건수·잠금 해제도 확인했다.
- 원본 논문 PDF 0개, 지식 페이지 0개다. 실제 논문 전체 파싱은 대상이 없어 미검증이며 합성 PDF로 검증한 GPT 이미지/표 파싱과 구분한다. Gemini fallback의 HTTP 403 제한은 남아 있다.
- 근거: `_meta/validation/final-audit.json`, `_meta/validation/activation.json`. 기존 실행 검증의 log 해시는 이 새 append 이전 시점의 스냅샷이며 변경 이력을 덮어쓰지 않았다.

## [2026-09-28] update | 사용자 지정 일회 범위 — 최근 논문 10편 수집 실행

- 사용자가 등록 Cron `4cff5b4f10ec`를 통해 설정 키워드의 최근 논문 10편 수집·저장을 명시적으로 요청했다.
- 이 실행에 한해 `max_paper_attempts_per_kst_day`를 5→10으로 일시 상향했다. 완료 확인 후 5로 복원한다.
- 선정 기준: 등록 Boolean 검색식에서 `submittedDate` 내림차순 최근 10편, 중복 arXiv ID는 최신 버전 1개만. `first_window_floor`보다 오래된 논문도 이번에는 사용자 지정 범위로 수집을 허용한다. 증분 checkpoint(`discovered_through`)는 후퇴시키지 않는다.

## [2026-09-28] update | PyMuPDF 추출 우선 + 선택적 텍스트 LLM 전환

- 사용자의 “추천 방식으로 적용해주세요” 승인에 따라 `SCHEMA.md`, `AGENTS.md`, `README.md`, 루트 `index.md`의 원천 운영 안내, `_meta/COLLECTION.md`, `_meta/topics.json`과 Cron `4cff5b4f10ec` 프롬프트를 `pymupdf-text-structure/v2`에 맞췄다. `_meta/text-structuring-prompt.txt`를 추가했다. 새 패키지·모델·커스텀 수집 스크립트·DB는 설치/생성하지 않았다.
- 전체 페이지 멀티모달 호출·이미지/PDF 모델 전송을 비활성화했다. 텍스트 LLM은 모호한 원문 블록의 ID 순서·역할만 반환하며 원문을 재작성하지 않는다. 논문당 최대 2개 chunk, 입력 16000자/chunk, 응답 4096 tokens다. 추출 완료와 텍스트 구조화·시각 검토 상태를 분리했다.
- 이전 run `20260928T075808Z-58958f18`의 worker를 중단했으나 기존 agent가 재시작한 것을 확인했다. 정확한 Cron fire owner를 확인한 `cron.jobs.mark_job_run(..., expected_fire_owner=...)`로 정책 전환 중단을 기록해 소유권 상실 watchdog을 적용하고, 재시작 worker도 종료했다. 이전 실행을 성공으로 위장하지 않았으며 서버측 이미 제출된 요청까지 취소됐다고 주장하지 않는다.
- 이전 잠금 소유권과 두 worker 종료를 확인한 뒤 `20260928T083759Z-textv2-a3e894c1`로 인계했다. 원래 staging 670개 파일은 해시 동일하게 보존하고 새 attempt에서 기계 추출물만 재사용했다. 과거 멀티모달 응답을 텍스트 LLM 결과로 재라벨하지 않았다.
- 이미 선정·다운로드된 10편, 251페이지를 검증하여 `raw/articles/4cff5b4f10ec/arxiv-<version-id>/`에 새 v2 원천 패키지로 원자 게시했다. 새 검색·다운로드는 하지 않았다. 원본 PDF·text layer·fulltext Markdown·전체 페이지 PNG·embedded 이미지·좌표·캡션 후보·표 후보 JSON/CSV/Markdown/crop·coverage·manifest가 포함된다.
- embedded 이미지 19개는 논문 그림 개수가 아니다. 표 후보 73개에는 도식/차트 오탐이 포함될 수 있고 모두 미검증 상태다. 시각 판독·수식 복원·표 값 정확성·논문 의미 검토는 하지 않았다.
- 실제 논문 `2609.30824v1` PDF 1페이지의 텍스트 15블록을 `codex-lb/gpt-6-astra` xhigh로 호출했다. 이미지 입력 0개, 반환 모델 gpt-6-astra, JSON/ID 전단사 검사 성공, 관측 호출시간 27.74초다. 정리본은 이 페이지에 한정되며 나머지 페이지의 선택적 구조화는 대기다. Gemini 텍스트 fallback은 호출하지 않았고 과거 시각 probe HTTP 403을 성공으로 바꾸지 않았다.
- 검증: 산출물 689개 해시·크기, 251페이지 coverage/PNG, 원본 ID·버전·PDF hash, 표 CSV의 escape/null 역변환, 원천 Markdown 본문 hash, 색인 10행, 탐색 링크 46개 통과. 잘못된 해시·누락 파일·중복 경로·다른 버전·잘못된 페이지 수의 5개 거부 테스트를 통과했다. 파일/구조 검증이며 의미 정확성 증명은 아니다.
- 주제 원천 index와 state를 반영했다. pending 0편, 수집 잠금 해제, discovery checkpoint 유지. 정기 한도는 하루 5편으로 복원하되 이미 승인된 KST 날짜의 10개 reservation은 별도 일회 승인 이력과 함께 보존했다. 지식 페이지 0개이며 Wiki 컴파일은 하지 않았다.
- Cron read-back: enabled=true, state=scheduled, 기존 `0 15 * * *`, `codex-lb/gpt-6-astra/xhigh`, local 전달 유지. 다음 정기 실행은 `2026-09-29T00:00:00+09:00`. 마지막 Cron 실행 표시는 `interrupted_policy_change`로 보존하며 이번 복구 성공은 별도 run report/state에 기록했다. 새 정책으로 정기 스케줄 실행 전체를 재실행한 것은 아니다.
- 근거: `_meta/runs/4cff5b4f10ec/20260928T083759Z-textv2-a3e894c1/report.json`, `prepublication-validation.json`, `final-audit.json`, `state-before.json`, `state-after.json`, `lock-release.json`; `_meta/validation/extraction-first-transition/`의 정책 snapshot, cron-interruption, text-request/text-response 및 cron-after JSON.

## [2026-09-28] lint | Figure 1 오분류 재현 및 컴파일 입력 전략 재검토

- 사용자 지적 대상: `raw/articles/4cff5b4f10ec/arxiv-2609.30217v1/`의 Figure 1을 막대 조각별 table로 저장한 문제. 기존 파일 보존·해시 검증 성공은 유효하지만, Wiki 컴파일용 문서 구조 준비 완료를 뜻하지 않는다. 이 사례는 전처리 품질 실패다.
- 원본 PDF 1페이지에서 embedded image 0개, vector path 38개를 확인했다. PyMuPDF lines/lines_strict 모두 내용 없는 표 후보 9개를 생성했고, text 전략은 본문을 포함하는 거대 후보를 생성했다. 4페이지 실제 Table 1은 기본 탐지에서 마지막 행만 추출됐다. 단순 빈 후보 제거 또는 파라미터 조정으로 전체 문제를 해결했다고 하지 않는다.
- 동일 버전 공식 HTML의 `#S0.F1`은 SVG 하나·Figure 1 캡션·본문 앵커 연결을 갖고 있고, `#S2.T1`은 별도 표·머리글·여러 데이터 행·✓/✗를 보존한다. 실제 브라우저 DOM으로 확인했다. SVG foreignObject/스타일 의존성도 확인했다.
- 이미지 시각 판독 도구는 Gemini HTTP 403으로 실패했다. 이번 진단은 사용자 관찰, PDF 구조/추출 재현, 공식 HTML 구조 대조에 근거하며 픽셀 시각 검토 성공을 주장하지 않는다.
- `_meta/PARSING-STRATEGY-PROPOSAL.md`에 **동일 버전 HTML 구조 우선 → PDF 전용이면 Docling 레이아웃 파서 평가 → 공통 document/figure/table/참조 구조와 품질 검사**를 제안했다. 정식 compiler 입력과 미검증 후보 diagnostics를 분리하고, 이 논문의 Figure 1 및 Table 1을 함께 회귀 검증하도록 명시했다.
- 이번 작업은 전략 재검토만 수행했다. 해당 원천 패키지 122개 산출물 해시와 manifest가 기존 감사 기록과 일치하고 Cron 설정도 그대로임을 확인했다. raw 재작성·재파싱 revision 게시·Docling 설치·자동 수집 정책 변경·Wiki 컴파일은 하지 않았다. 적용은 별도 승인 후 진행한다.

## [2026-09-28] repair | 2609.30217v1 단일 논문 구조화 시험 및 확대 gate 보류

- 사용자의 “논문 1편을 대상으로 검증 후 확대” 승인으로 Cron `4cff5b4f10ec`를 일시정지하고 해당 논문만 처리했다. 기존 PDF·추출물·complete manifest를 덮어쓰지 않고 `raw/articles/4cff5b4f10ec/arxiv-2609.30217v1/parsing/revisions/html-structure-pilot-v1/`에 검토용 revision을 원자적으로 게시했다.
- 동일 버전 HTML DOM/MHTML과 저자 지정 객체를 보존했다. 그림 22개, 표 9개, 본문 문단 98개, 절 컨테이너 51개, 텍스트 상자 7개, 참고문헌 항목 35개, 각주 7개를 구조화했다. 제목·저자 포함 231개 객체, 읽기 순서 224개, 링크 관계 209개이며 미해결 내부 참조는 0개다. Figure 내부 막대 조각을 정식 table로 만들지 않았다.
- PDF 34페이지를 기계적으로 대조했다. 31개 그림/표 캡션을 유일한 PDF 페이지에 연결했고, HTML 저자/소속 배치와 참고문헌 축약 차이는 PDF 1페이지 블록 및 14–16페이지 참고문헌 원문으로 보완했다. 전체 의미 동등성이나 과학적 주장 검증을 완료했다고 하지 않는다.
- 별도 확인을 통해 비교 이미지 4개만 기존 GPT 경로로 보내는 수동 시각 검증을 승인받았다. `codex-lb/gpt-6-astra` xhigh 1회, 반환 모델 gpt-6-astra, 관측 28.95초. 전체 PDF·다른 논문·추가 이미지·Gemini fallback은 보내지 않았다.
- Figure 1은 전체 그림·축·범례·모델 라벨·수치·특수기호 보존 판정 통과. Table 1은 헤더 1행 + 데이터 5행, 7열, 체크 5개/교차 15개를 HTML 원값대로 보존했으나 초기 PNG가 웹페이지 헤더를 담아 시각 검증에 실패했다. 실패 이미지와 원래 fail 응답을 보존하고, 이미 시각 확인한 PDF reference crop을 바이트 동일하게 재사용해 교정했다. 신규 모델 재검증 통과로 재라벨하지 않았다.
- 최종 회귀 검사 4개 통과, 게시 전 기준 파일 703개 해시 동일, 새 revision 산출물 164개 해시·크기 검증(manifest 포함 165개 파일), 읽기/검토 HTML 로컬 링크 255개와 계층 무순환을 확인했다. 파일 무결성 및 구조 검사는 나머지 렌더 29개의 시각 정확성 증명이 아니다.
- `quality.json`, `compile-input.json`은 `active:false`, `ready:false`/`structure_ready_for_compilation:false`로 남겼다. 나머지 렌더 정체성·잘림 검증 전에는 확대하지 않는다. 다른 9편 재처리·새 운영 파서 승격·Cron 재개는 하지 않았으며 정기 수집은 일시정지 유지다. topics/state와 원래 스케줄/모델/일일 한도는 변경하지 않았다.
- 변경: `SCHEMA.md` 단일 revision 계약, `_meta/COLLECTION.md` 보류 안내, `_meta/PARSING-STRATEGY-PROPOSAL.md` 시험 상태, 주제 raw index, 이 log. 검증 보고서와 기준/테스트/게시 근거는 `_meta/validation/html-pilot-2609.30217v1/`. `AGENTS.md`는 변경하지 않았다. 루트 지식 index 및 지식 디렉터리도 변경하지 않았고 지식 페이지는 0개다.

## [2026-09-28] update | 전처리 폐기·arXiv HTML 원본 전용 전환

- 사용자가 논문 원본 HTML 직접 llm-wiki 컴파일 전략, 모든 사전 파싱 기능 제거, 기존 모든 논문의 HTML 원본 저장을 요청했다. 추가 확인에서 **새 백업 없이 기존 PDF·전처리 산출물·전용 환경 영구 삭제**, HTML 미제공 2편도 PDF 삭제·미확보 기록만 유지, 검증 후 기존 Cron HTML 전용 재개를 명시 승인했다.
- 기존 대상 10개 ID/버전을 전수 확인했다. 8편은 공식 동일 버전 `/html/<version-id>`의 HTTP 본문을 바이트 그대로 다운로드하고 상태·형식·제목·버전 URL·길이·SHA-256을 검증했다. `source.html`과 최소 `source.json`만 활성 raw에 저장했다. HTML 변환·재작성·사전 구조화·자산 추출은 하지 않았다.
- `2609.30614v1`, `2609.30824v1`은 공식 HTML 404이고 abs 페이지에도 PDF만 있어 미제공이다. 초록을 전문 HTML로 대체하지 않았다. 승인에 따라 기존 PDF도 삭제했고 state/index에 미확보와 7일 후 재확인만 기록했다. 로컬 전문은 없다. 저장 성공 8편과 대상 전체 10편을 구분한다.
- 기존 PDF 10편 및 전처리 raw/staging/validation/run, `_meta/pdf-env`, pdf requirements, 파싱 prompt, 파싱 전략 제안을 영구 제거했다. 승인 대상 파일 1805개 삭제를 기록했다. 새 백업은 만들지 않았고 이전 별도 백업은 열거나 변경하지 않았다. 이전 log의 과거 파일 경로는 삭제 이력으로만 남으며 현재 실행 지시가 아니다.
- `SCHEMA.md`, `AGENTS.md`, `README.md`, `_meta/COLLECTION.md`, `_meta/topics.json`, `_meta/state/4cff5b4f10ec.json`, root index와 topic index를 변경하고 `_meta/COMPILATION.md`에 원본 직접 읽기 전략을 기록했다. 전처리 parser/fallback/text_structuring·pdf Cron 스킬을 제거했다.
- 기존 discovery floor/checkpoint와 날짜별 시도 기록은 그대로다. 새 논문 검색·추가 PDF 다운로드·모델 파싱·Wiki 컴파일은 하지 않았다. 지식 페이지 0개. 원본 8편 해시/ID 전수 확인, 변조/다른 버전/404 거부 확인, 미확보 2편 및 활성 PDF·전처리 코드/환경 부재 검증을 통과했다.
- Cron `4cff5b4f10ec`는 HTML 전용으로 재개했고 전체 prompt 해시/skills=[arxiv]/enabled=true/script 없음 read-back으로 확인했다. UTC `0 15 * * *`, 매일 KST 00:00, 최대 5편, local 전달 유지. 다음 예정 2026-09-29T00:00:00+09:00. 실제 정기 실행 전체를 이번에 다시 발화한 것은 아니다.
- 전환·삭제·수집·미제공·검증 근거: `_meta/migrations/20260928T104108Z-html-only/report.md` 및 report/downloads/cutover/validation/cron-after-resume JSON. HTML 원문만 저장했으므로 외부 자산을 포함하는 오프라인 번들이 아니며 시각·의미 검토 완료를 뜻하지 않는다.

## [2026-09-28] create | docs 논문 수집 자동화 쉬운 설명서

- 사용자 요청에 따라 `docs/README.md`와 `docs/paper-collection.md`를 작성했다. 예약 알람·책장·메모지 비유로 HTML 원본 수집과 수동 llm-wiki 컴파일을 구분했다.
- HTML 전용(없을 때 PDF 대체 없음), 일정·시도 한도·검색 범위·중복·파일 확인·HTML 미제공/전송 실패·동시 실행/안전 중단·저장 위치·제거한 전처리·외부 자산 제한·확인 방법을 담았다.
- 2026-09-28 11:07 UTC에 확인한 Cron 활성화와 HTML 8편/미제공 2편/지식 페이지 0개를 날짜가 있는 현황으로 표시했다. 실제 HTML 저장과 새 정책의 정기 실행 전체 성공을 구분했으며, 후자는 아직 확인 이력이 없다고 명시했다.
- root `README.md`와 `index.md` 운영 안내에 설명서 링크를 추가했다. 운영 설명서이므로 지식 페이지 수를 늘리지 않았다.
- 관련 문서의 로컬 링크 38개·코드 구획·정책/편수 일치와 보호 대상 파일 36개 불변을 검증했다. Cron 설정·원본·정책·상태는 변경하지 않았고 수집/파싱/Wiki 컴파일은 실행하지 않았다.

## [2026-09-28] update | AI Agent Security HTML 정기 수집 — 정상 검색 0편

- 실행 `20260928T111326Z-695dc69b`, 정책 `arxiv-html-original/v1`. 정확한 topics.api_query와 lastUpdatedDate 내림차순을 사용했다. 직접 API HTTP 406은 동일 URL의 공식 브라우저 Atom 확인으로 복구했으며, DOM pre.textContent 캡처를 HTTP 원문 바이트로 표시하지 않았다.
- Atom 100개 ID의 고유성·updated 내림차순·하한 통과를 검증했다. 범위 `2026-09-27T07:07:13.632288+00:00` ~ `2026-09-28T11:13:26.978196+00:00` 후보 0편. 검색 완료와 pending 내구 저장 후 discovery checkpoint를 상한까지 전진했다. first_window_floor는 유지했다.
- 신규 HTML 0편, 중복 처리 0편, 새 HTML 미제공 0편, 미복구 업무 실패 0건. 기존 HTML 8편의 실제 버전 URL·크기·SHA-256·제목/본문 존재·두 파일 목록을 검증했다. 미제공 2편은 7일 재확인 전이라 요청하지 않았다.
- 엄격한 제목 공백 일치 검사에서 2609.30830v1의 원본 title에 DefenseAgainst로 공백 하나가 생략된 차이를 발견했다. 원본 해시·버전·공백 외 모든 제목 문자는 일치하여 검증 오탐으로 확인했다. 실패 및 복구 근거를 보존했고 원본 HTML/source.json은 수정하지 않았다.
- 오늘의 기존 10개 ID는 승인된 일회 수집 기록이며 보존했다. 새 시도 0개, pending 없음, safety_block=false, 최종 연속 실패 0회.
- 변경: `_meta/state/4cff5b4f10ec.json`, `raw/articles/4cff5b4f10ec/index.md`, root `index.md` Raw Sources, append-only log, `_meta/runs/4cff5b4f10ec/20260928T111326Z-695dc69b/` 실제 실행 근거. PDF/LaTeX/외부 자산 다운로드·전처리·별도 모델 호출·내용 분석·도표 판독·Wiki 컴파일은 하지 않았다. 원본 8편·미제공 2편·지식 페이지 0개는 변하지 않았다.

## [2026-09-28] update | AI Agent Security HTML 정기 수집 — 정상 검색 0편

- 실행 `20260928T120230Z-12d769d4`, 정책 `arxiv-html-original/v1`. topics.api_query를 그대로 사용한 직접 API 요청이 HTTP 200으로 완료됐다. Atom HTTP 응답 본문·요청 URL·상태·길이·SHA-256을 보존했다. 브라우저 DOM 캡처는 사용하지 않았다.
- 검색 범위 `2026-09-27T07:07:13.632288+00:00` ~ `2026-09-28T12:02:30.148155+00:00`. Atom 100개 버전 ID의 고유성·updated 내림차순·하한 통과를 검증했고 범위 내 후보는 0편이다. 빈 pending을 fsync·원자 저장한 뒤 discovery checkpoint를 상한으로 전진했으며 기존 first_window_floor는 유지했다.
- 신규 HTML 저장 0편, 중복 처리 0편, 새 HTML 미제공 0편, 미복구 검색/전송/무결성 실패 0건. 기존 HTML 8편의 로컬 바이트·SHA-256·길이·버전 URL·제목/본문 컨테이너·두 파일 목록을 재검증했다. 기존 HTML의 새 HTTP 다운로드나 내용 분석은 하지 않았다. 기존 미제공 2편은 재확인 시각 전이라 요청하지 않았다.
- 기존 승인된 날짜별 10개 ID 시도 기록을 보존했고 새 시도는 0개다. pending 없음, safety_block=false. execute_code는 Cron 승인 정책으로 사용할 수 없어 허용된 네이티브 terminal 도구로 수행했으며 승인 정책·환경·프로그램을 변경하지 않았다.
- 변경: `_meta/state/4cff5b4f10ec.json`, 주제 raw index, 루트 index의 Raw Sources, append-only log, `_meta/runs/4cff5b4f10ec/20260928T120230Z-12d769d4/` 실제 실행 근거. 원본 8편·미제공 2편·지식 페이지 0개는 유지된다. PDF/LaTeX/외부 자산 다운로드·전처리·별도 모델 호출·내용 분석·도표 판독·Wiki 컴파일은 하지 않았다.

## [2026-09-28] update | Git 저장소 초기화 및 원격 이력 연결

- 사용자 요청에 따라 현재 프로젝트에서 Git을 초기화하고 `origin`을 `git@github.com:ains-lab/pkm-articles.git`으로 설정했다. 원격 `main`의 기존 커밋 `65835136dceb8ba565f544d2c8cfba547ec508ea`를 가져와 로컬 `main`의 기준으로 삼았으며 현재 프로젝트 파일은 유지했다.
- `.gitignore`에 자격증명·로컬 환경·캐시와 일시적인 `_meta/staging/`, `_meta/locks/` 제외 규칙을 추가했다. 원천 HTML·서지·state·run·migration 근거는 버전 관리 대상이다.
- `.gitattributes`에서 원본 `source.html`의 Git 줄바꿈 변환을 비활성화했다. 빈 지식 디렉터리 4개와 `raw/papers/`, `raw/transcripts/`, `raw/assets/`에 `.gitkeep`을 추가해 Git에서도 구조를 유지한다. 지식 페이지를 생성한 것은 아니다.
- 기존 프로젝트 파일 64개에 대한 자격증명 파일명·주요 비밀정보 패턴 검사에서 발견 항목이 없었고 JSON 42개의 문법을 검증했다. 이 검사는 논문 내용 검토나 모든 종류의 민감정보 부재를 보증하지 않는다.
- 전역 Git·SSH·Hermes 설정, 다른 저장소·백업·Cron은 변경하지 않았다. 원본 수집·전처리·Wiki 컴파일은 실행하지 않았다.

## [2026-09-28] create | 5주차 논문 수집 Cron 생성·현재 구성 기술문서

- 사용자 요청에 따라 `eli5` 스킬의 알람·도우미·책장·책갈피 비유로 `docs/lectures/5w/paper-collection-cron.md`를 작성했다. 현재 구성, 정확한 검색식·시간대·한도, 파일 역할, 중복·실패 처리, paused 생성→ID/정책 연결→검토→승인 후 활성화 절차와 CLI 예시를 담았다.
- 요청 문자열 `4cff5b4f10ec0`는 현재 목록에 없고 설치된 12자리 ID 형식과도 다르다. 실제 이름·정책·상태가 일치하는 `4cff5b4f10ec`를 문서화했으며 두 문자열을 같은 ID로 취급하거나 새 작업을 만들지 않았다.
- 2026-09-28 12:51 UTC 기준 등록 레코드·Gateway/ticker·실행 이력·topics/state/report를 대조했다. 최근 결과는 `last_status=ok`, 정상 검색 0편이다. 다음 KST 자정 예정, 새 다운로드, 의미·시각 검토와 구분했다. 보유 HTML 8편의 실제 SHA-256·길이·버전 URL·파일 목록 및 미제공 2편과 전체 대상 ID 집합을 재검증했다.
- 기존 `docs/lectures/5w/paper-collection.md`의 과거 상태를 갱신하고 이동된 위치 기준 상대 링크를 수정했다. `docs/README.md`, 루트 `README.md`·`index.md`에 기술문서 링크를 연결했다. 운영 문서이므로 지식 페이지 수는 0개로 유지한다.
- 관련 문서 5개의 로컬 링크 62개, 코드 구획, Bash 예시 4개의 문법, 생성 옵션의 설치 CLI 지원 여부, 검색식 문자 일치를 검증했다. 실제 생성·실행 명령을 호출한 시험은 아니다. 관측 중 별도 추가된 Git 초기화 이력을 보존했고 이 문서화 작업에서 Git 초기화·커밋·push를 수행하지 않았다.
- 대상 Cron 등록값과 원천·수집 정책·상태는 변경하지 않았다. arXiv 검색/다운로드·전처리·Wiki 컴파일·설치·알림·전역 스킬/모델/인증 변경을 수행하지 않았다. 기존 로그 뒤에 실제 문서화 내역만 추가했다.

## [2026-09-28] create | 5주차 Agent-Reach X·Reddit 수집 방법 기술문서

- 사용자 요청에 따라 `eli5` 스킬의 리모컨·출입증 비유로 `docs/lectures/5w/social-collection-agent-reach.md`를 작성했다. 키워드 기반과 계정 기반 수집의 차이, X 팔로워 2단계 조리법, Reddit 서브레딓·사용자 활동 수집, 저장·반복·예의 수칙을 담았다.
- 근거는 Agent-Reach 저장소 문서, 이 머신에 설치된 `twitter`·`rdt`·`opencli`의 실제 `--help` 출력, Reddit 공식 검색 기능 도움말이다. 사용자 요청 URL의 트리 경로 `/tree/main`은 raw 파일 경로로 바꿔 확인했다. 설치 CLI·명령 목록에 없는 하위 명령(login/run 등 오류 확인)은 문서에 실제 존재하는 것만 기술했다.
- X 팔로워·팔로잉 명령은 opencli 관측값으로, Reddit에는 팔로워 목록 명령이 없어 `author:` 연산자·사용자 활동 명령으로 대체하는 구조를 명시했다. Reddit 연산자 표는 공식 도움말 콜론 무공백 규칙을 따랐다.
- 실제 X·Reddit 요청·로그인·인증 변경·설치·제거·Cron 생성은 하지 않았다. 계정 정보나 자격증명은 다루지 않았다. 소셜 수집 자동화는 이 저장소 범위 밖이므로 별도 승인 대상임을 문서에 명시했다.
- `docs/README.md` 먼저 읽을 문서 목록에 새 문서 링크를 추가했다. 논문 수집 Cron `4cff5b4f10ec` 설정·원본·상태와 지식 페이지 수는 변하지 않았다.

## [2026-09-28] repair | 4주차 실습 경로·SNS 스키마 분리 및 커밋 전 검증

- 사용자의 오류 수정 후 commit·push 요청에 따라 기존 강의 변경분을 보존하면서 `docs/lectures/4w/README.md`, `01-pipeline-design.md`, `02-omh-and-api-setup.md`, `03-hands-on.md`, `04-cron-operations.md`, `05-analysis-with-hermes.md`, `06-sources-and-verification.md`, `07-incremental-wiki.md`의 이전 `class/4w` 경로와 잘못된 스키마 참조를 수정했다. 위 파일명은 모두 `docs/lectures/4w/` 아래 경로다.
- 경로 복구 후 SNS 실습 검증기가 논문 전용 루트 스키마의 태그·원천 계약과 호환되지 않는 추가 원인을 확인했다. 루트 계약을 바꾸지 않고 `docs/lectures/4w/lab/SCHEMA.md`에 외부 비공개 SNS 실습 전용 계약을 분리했으며 문서의 초기화 명령·테스트가 이 파일을 사용하게 했다.
- `docs/lectures/4w/lab/wiki_pipeline.py`는 태그 등록부 누락·빈 등록부를 초기화 쓰기 전에 명시적으로 거부하고 완료 검사에서도 같은 검사를 사용한다. `lab/test_materials.py`에 문서 실행 경로 검사, `lab/test_wiki_pipeline.py`에 부적합 스키마의 API·CLI 거부 및 미생성 검사를 추가했다. 이 두 테스트 경로도 `docs/lectures/4w/` 기준이다.
- 신규 경로 검사와 스키마 거부 검사가 수정 전 실패하는 것을 확인한 뒤, `python3 -B -m unittest discover -s docs/lectures/4w/lab -p 'test_*.py' -v`로 **49 tests, OK**를 확인했다. 임시 합성 fixture·mock 기반이며 실제 SNS 인증·수집·의미적 Wiki 컴파일의 성공을 뜻하지 않는다.
- 커밋 후보의 Python 9개 AST, JSON 1개 문법과 주요 자격증명 패턴을 검사했고 발견된 비밀값 패턴은 없었다. 전체 staged whitespace 검사에서는 기존 2·3·5주차/강의계획 문서의 행 끝 공백·마지막 빈 줄 경고가 남아 있어 기능 오류와 구분하며 관련 없는 재서식은 하지 않았다.
- 루트 `SCHEMA.md`, `AGENTS.md`, `_meta/`, `raw/`, 지식 디렉터리는 HEAD 대비 변경 없음을 확인했다. 실제 수집·Cron·설치·인증·프로필·외부 모델·다른 Wiki는 변경하지 않았으며 지식 페이지 수는 유지한다. 이 항목은 수정·검증 기록이며 원격 push 성공은 아직 기록하지 않는다.

### 추가 회귀 수정 및 재검증

- 독립 검토에서 재현한 두 결함을 `docs/lectures/4w/lab/pipeline.py`에서 수정했다. URL userinfo는 빈 사용자명도 거부하여 비밀번호가 저장·export되지 않게 했으며, 지원하지 않는 타입·범위의 타임스탬프는 `ValueError`로 거부한다. 잘못된 legacy payload의 observation은 생략하되 기존 version과 원본 payload는 보존한다.
- `docs/lectures/4w/lab/test_regressions.py`, `docs/lectures/4w/lab/test_incremental.py`에 mocked Reddit URL의 저장·export 차단, 타임스탬프 호환성, legacy API·CLI 마이그레이션의 보존·멱등성 회귀 검사를 추가했다. 수정 후 부모 세션에서도 전체 실습 테스트를 다시 실행해 **53 tests, OK**를 확인했다.
- Python 9개 AST·JSON 1개 문법 검사, 수정분 `git diff --check`, 운영 Wiki 보호 경로의 HEAD 대비 무변경 검사를 통과했다. 추가 행 보안 패턴 검사에서 검출된 `wiki_pipeline.py`의 `token`은 자격증명이 아닌 SNS ingest 로그의 HTML 주석 표식이었다. 이 재검증은 합성 fixture·mock에 한정하며 실제 SNS 수집·Wiki 컴파일 성공을 의미하지 않는다.
