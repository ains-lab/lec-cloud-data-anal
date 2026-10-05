# 1. 구조와 수집 범위 — 알람, 도구, 장부를 분리하기

[목차](README.md) · 다음: [설치·인증](02-setup-and-auth.md)

## 1.1 전체 구조

**예약하는 일, 읽어 오는 일, 저장하는 일은 서로 다른 책임이다.**

```text
사람이 승인한 키워드·계정 목록과 정책
                    │
                    ▼
Hermes Cron ── 정해진 시각에 실행
                    │
                    ▼
Hermes agent 작업 또는 검증된 script-only 작업
                    │
                    ├─ X       → twitter CLI
                    ├─ Reddit  → rdt CLI
                    └─ YouTube → yt-dlp
                    │
                    ▼
응답 성공·형식·작성자·시간 범위 검사
                    │
                    ▼
비밀정보를 제거한 콘텐츠 스냅샷 + 정규화 레코드
                    │
                    ▼
대상별 상태·중복 장부 갱신 → 건수와 오류 보고
```

Agent Reach는 도구 설치·진단·backend 안내를 담당한다. 데이터베이스, 중복 제거, 예약 실행, 계정 이용 허가를 자동으로 제공하는 제품으로 이해하면 안 된다. Cron에서 스킬을 로드해도 새로운 인증이나 데이터 수집 권한이 생기지 않는다.

## 1.2 키워드와 계정 기반의 차이

| 방식 | 쉬운 비유 | 장점 | 주의점 |
| --- | --- | --- | --- |
| 키워드 검색 | 도서관에서 같은 주제의 책 찾기 | 모르는 작성자도 발견 | 동음이의어·광고·검색 순위 편향 |
| 고정 watchlist | 내가 정한 서가만 확인 | 대상이 명확하고 반복 비교가 쉬움 | 목록 밖의 중요한 글은 놓침 |
| 계정 + 키워드 | 정한 서가에서 특정 주제만 찾기 | 잡음 감소 | 지나치게 좁히면 누락 증가 |
| 관계 목록 → watchlist | 추천 목록을 받아 사람이 서가 선택 | 관심 계정 후보 발견 | 관계 자체가 관심·전문성·동의의 증거는 아님 |

**watchlist**는 수집을 허용한 계정·채널 목록이다. 계정을 실제로 팔로우하거나 구독하는 쓰기 동작이 아니다.

## 1.3 “팔로워 계정 기반”의 세 가지 뜻

X에서 A를 기준으로 보면:

- `followers A`: **A를 팔로우하는 사람들**. 화살표는 `다른 사람 → A`.
- `following A`: **A가 팔로우하는 사람들**. 화살표는 `A → 다른 사람`.
- 고정 watchlist: 관계 목록과 무관하게 사람이 직접 선정한 계정들.

“내가 팔로우하는 사람들의 글”이 목적이면 내 계정의 **following**을 기준으로 한다. “특정 계정의 팔로워들이 쓰는 글”이면 **followers**다. 추천 피드에는 목록 밖의 글이 섞일 수 있으므로 watchlist의 대체물로 사용하지 않는다.

| 플랫폼 | 키워드 단위 | 계정 기반 단위 | 관계 목록의 경계 |
| --- | --- | --- | --- |
| X | 검색어·연산자 | 사용자 글 | CLI의 followers/following 결과를 검토 후 고정 목록으로 채택 |
| Reddit | 전체 또는 subreddit 검색 | 사용자 게시글·댓글, subreddit | 여기서 확인한 rdt에는 X식 followers 열거 명령이 없음 |
| YouTube | 영상 검색 | channel ID + videos/shorts/streams | 구독 채널과 채널의 구독자는 다름. yt-dlp를 전체 구독자 열거 도구로 쓰지 않음 |

관계 목록은 매 수집마다 무한히 확장하지 않는다. 별도의 낮은 빈도로 후보를 확인하고, 사용자가 승인한 추가·제외분만 watchlist에 반영한다. 공개 관계에서 민감한 성향을 추론하거나 여러 플랫폼의 사용자를 실명으로 연결하지 않는다.

## 1.4 처음에 결정할 수집 계약

다음은 **권장 시작값**이지 서비스가 허용한 공식 호출량이 아니다. 서비스의 더 낮은 제한과 응답 지시를 우선한다.

| 항목 | 수업용 시작 기준 |
| --- | --- |
| 목적 | 예: AI 에이전트 도구의 공개 발표 동향 확인 |
| 활성 플랫폼 | 처음에는 하나만 |
| 키워드 또는 계정 | 승인한 대상 하나로 먼저 검사 |
| 요청 결과 상한 | 조회당 최대 20개 후보 |
| 실행 빈도 | 수동 검증 후 6시간 간격 예시 |
| 시간 범위 | 최초 최근 24시간, 이후 대상별 이전 성공 경계에서 일부 겹쳐 조회 |
| 원문 범위 | 글 제목·본문·링크 또는 영상 메타데이터. 댓글·자막은 선택 승인 |
| 제외 | DM, 비공개 계정, 제한 콘텐츠, 영상·음성 다운로드, 자동 게시·좋아요·팔로우 |
| 보관 | Git 밖 개인 비공개 경로, 보관 기한과 삭제 요청 처리 책임자 명시 |
| 성공 기준 | 응답 상태·형식·ID·시간·작성자·파일 저장·대상별 상태 모두 확인 |

키워드의 범위는 플랫폼별로 다르다. YouTube에서 “키워드 검색”을 했다고 모든 자막 본문을 검색한 것은 아니다. 댓글을 수집하지 않았으면 댓글 여론을 분석했다고 표현하지 않는다.

## 1.5 예시 입력 계약

아래 JSON은 **강의에서 제안하는 로컬 설정 형식**이다. Agent Reach나 Hermes가 기본적으로 읽는 공식 설정이 아니다. [Cron 프롬프트](07-hermes-cron.md)가 이 계약을 읽도록 명시해야 한다.

모든 플랫폼을 꺼 둔 안전한 초기값이다. 사람이 이용 정책·인증·대상을 확인한 후 필요한 플랫폼만 켠다. 빈 목록은 전체 인터넷을 뜻하지 않는다.

```json
{
  "schema_version": "sns-collection-policy/v1",
  "purpose": "공개 기술 발표 동향의 제한된 관측",
  "display_timezone": "Asia/Seoul",
  "first_run_lookback_hours": 24,
  "overlap_hours": 6,
  "max_items_per_target": 20,
  "max_targets_per_run": 5,
  "max_attempts_per_target": 2,
  "request_timeout_seconds": 90,
  "retention_days": 30,
  "x": {
    "enabled": false,
    "keywords": ["\"AI agent\""],
    "accounts": [],
    "exclude_reposts": true,
    "exclude_replies": true,
    "expand_relationships_automatically": false
  },
  "reddit": {
    "enabled": false,
    "policy_reviewed": false,
    "keywords": ["AI agent"],
    "subreddits": [],
    "users": [],
    "include_comments": false
  },
  "youtube": {
    "enabled": false,
    "keywords": ["AI agent tutorial"],
    "channel_ids": [],
    "tabs": ["videos"],
    "collect_subtitles": false
  }
}
```

`retention_days`는 삭제 승인이 아니라 검토 기준 예시다. 운영자가 플랫폼 정책과 기관 기준을 확인해 실제 보관·삭제 정책을 승인한다. `policy_reviewed: true` 또한 승인 문서의 대체물이 아니며 허가되지 않은 연구 수집을 허용하지 않는다.

키워드 목록과 계정 목록은 기본적으로 **독립된 조회 대상들의 합집합**으로 정의한다. 같은 글이 둘에 매칭되면 콘텐츠는 하나, 발견 경로는 둘로 기록한다. 교집합이 필요하면 X의 `--from`이나 Reddit의 `author:`처럼 별도 승인된 검색 조건을 만든다.

## 1.6 성공과 완전성을 구분하기

- **요청 성공**: CLI가 정상 종료했고 응답이 올바른 형식이다.
- **저장 성공**: 승인한 데이터만 실제 파일로 저장되고 다시 읽힌다.
- **관측 범위 확인**: 어떤 대상·시간·페이지 제한으로 검색했는지 남는다.
- **완전한 수집**: 그 기간의 모든 글을 확보했다는 강한 주장이다. 검색 기반 CLI만으로 일반적으로 보장하지 않는다.

따라서 “자료 0건”만 적지 않는다. `ok_empty`, `failed`, `partial`, `blocked_auth` 등을 구분하고 “조회한 범위에서 0건”이라고 말한다.

### 이해 확인

**Q. A의 following 20개를 읽었으면 A의 팔로워 20명을 수집한 것인가?**

아니다. A가 구독하는 계정 후보를 읽은 것이다. 결과가 잘렸을 수도 있고, 후보들의 게시글 수집은 별도의 단계다.

## 근거

- [Agent Reach 구조·backend 안내](https://github.com/Panniantong/agent-reach)
- [Hermes Cron 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- 세부 명령과 관계 목록 지원 범위는 [X](03-x-collection.md), [Reddit](04-reddit-collection.md), [YouTube](05-youtube-collection.md) 문서를 따른다.
