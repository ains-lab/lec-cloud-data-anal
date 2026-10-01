# AI Agent Security — HTML 원본 색인

- Cron ID: `4cff5b4f10ec`; 매일 KST 00:00(UTC `0 15 * * *`), KST 날짜당 최대 5편.
- 원본 수집만 수행한다. 전처리·자동 Wiki 컴파일은 하지 않는다.
- [설정](../../../_meta/topics.json) · [수집 규칙](../../../_meta/COLLECTION.md) · [직접 컴파일 전략](../../../_meta/COMPILATION.md).
- 보유 대상 **10편** 중 HTML 저장 **8편**, 공식 HTML 미제공 **2편**. 원본 8편의 실제 파일·버전·크기·SHA-256을 이번 실행에서 재검증했다.
- 최근 정기 수집 실행: `20260928T120230Z-12d769d4`. `2026-09-27T07:07:13.632288+00:00`부터 `2026-09-28T12:02:30.148155+00:00`까지 실제 Atom updated 기준 신규 후보 **0편**. 직접 API HTTP 200 응답 본문을 저장하고 검색식·100개 버전 ID의 고유성·updated 내림차순·검색 하한 통과를 확인했다.
- 이번 실행: 신규 HTML **0편**, 중복 처리 **0편**, 새 HTML 미제공 **0편**, 미복구 업무 실패 **0건**. 기존 미제공 2편은 7일 재확인 시각 전이므로 요청하지 않았다. [실행 근거](../../../_meta/runs/4cff5b4f10ec/20260928T120230Z-12d769d4/report.json).
- 각 완료 폴더에는 **source.html + source.json**만 있다. HTTP 원문 바이트·버전·크기·해시를 검증했고 외부 그림/CSS는 별도 다운로드하지 않았다.
- 미제공 2편은 사용자 승인으로 PDF도 삭제했다. 초록 페이지를 전문 HTML로 대체하지 않았으며 로컬 전문은 없다.

## 기존 대상 전체

| 버전 ID | 제목 | 원본 상태 |
| --- | --- | --- |
| 2609.31562v1 | Agentic Economies for Autonomous Scientific Discovery | [원본 HTML](arxiv-2609.31562v1/source.html) · [서지·해시](arxiv-2609.31562v1/source.json) |
| 2609.31358v1 | A Safety-Bounded SDC-to-MCP Gateway for Medical AI Agents | [원본 HTML](arxiv-2609.31358v1/source.html) · [서지·해시](arxiv-2609.31358v1/source.json) |
| 2609.31318v1 | AgentXploit: Autonomous Repository-to-Runtime Red-Teaming for AI Agents | [원본 HTML](arxiv-2609.31318v1/source.html) · [서지·해시](arxiv-2609.31318v1/source.json) |
| 2609.31039v1 | MetaPermit: Scalable and Auditable Access Control for AI Agents via LLM-Inferred Meta-Attributes | [원본 HTML](arxiv-2609.31039v1/source.html) · [서지·해시](arxiv-2609.31039v1/source.json) |
| 2609.30940v1 | Financial Fragility in Societies of LLM Agents: Coordination Failures and Stabilizing Mechanisms | [원본 HTML](arxiv-2609.30940v1/source.html) · [서지·해시](arxiv-2609.30940v1/source.json) |
| 2609.30830v1 | AGATE: Provenance-Based Runtime Defense Against Compositional Attacks on LLM Agents | [원본 HTML](arxiv-2609.30830v1/source.html) · [서지·해시](arxiv-2609.30830v1/source.json) |
| 2609.30824v1 | Crypto-bound identity-verified capability tokens for coordinating distributed AI agents: A proposal | **HTML 미제공 · 전문 없음** — [arXiv](https://arxiv.org/abs/2609.30824v1) |
| 2609.30614v1 | Subjects, Not Authors: The Authorship Hazard in Agentic Dataspaces | **HTML 미제공 · 전문 없음** — [arXiv](https://arxiv.org/abs/2609.30614v1) |
| 2609.30266v1 | LLM Agents Can Easily Tamper With Their Own Traces | [원본 HTML](arxiv-2609.30266v1/source.html) · [서지·해시](arxiv-2609.30266v1/source.json) |
| 2609.30217v1 | Instrumental Monitor Evasion Emerges Under Ordinary Task Pressure | [원본 HTML](arxiv-2609.30217v1/source.html) · [서지·해시](arxiv-2609.30217v1/source.json) |

## 완료·미확보의 의미

- 저장 완료는 arXiv HTML 원본 확보와 무결성 확인이다. 논문 내용 분석·도표 판독·실험 재현 완료가 아니다.
- HTML은 원본 그대로여서 일부 외부 자산·상대 링크의 로컬 표시에는 제약이 있다. 원래 URL은 source.json에 있으며 원문을 수정해 링크를 고치지 않았다.
- HTML 미제공은 state.html_unavailable에 확인시각·7일 후 재확인 시각·공식 링크 증거를 남긴다. 수집 성공 편수에 포함하지 않는다.
- 동일 source+version_id는 해시 검증 후 재사용한다. 다른 주제와 공유할 때는 reference만 저장한다.

## 전환 근거

- [실행 보고서](../../../_meta/migrations/20260928T104108Z-html-only/report.md)
- [원본 다운로드 기록](../../../_meta/migrations/20260928T104108Z-html-only/downloads.json)
- [HTML 미제공 확인](../../../_meta/migrations/20260928T104108Z-html-only/html-unavailable-evidence.json)
- [영구 삭제·원본 게시 기록](../../../_meta/migrations/20260928T104108Z-html-only/cutover.json)

이전 PDF·추출·시각 검토 상태는 폐기된 전처리 이력이다. 이전 active 파일은 삭제되었으며 log의 과거 경로가 더 이상 존재하지 않을 수 있다. 새 백업은 만들지 않았고 이전 백업은 접근·변경하지 않았다.
