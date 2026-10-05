# 3. X 수집 — 키워드, 계정, followers/following

[목차](README.md) · 이전: [설치·인증](02-setup-and-auth.md) · 다음: [Reddit](04-reddit-collection.md)

**처음에는 관심 계정 하나 또는 검색어 하나로 시작한다.** 친구 목록을 모으는 것과 친구가 쓴 글을 모으는 것은 서로 다른 요청이다.

> 명령은 `twitter-cli 0.8.6`의 help·공개 소스 기준이다. 실제 X 조회는 수행하지 않았다. `HANDLE`, `TWEET_ID`는 승인한 실제 값으로 바꾼다. Cron에서는 [자동 쿠키 추출 차단 경계](02-setup-and-auth.md)를 적용한다.

## 3.1 키워드 검색

```bash
# 한국어 키워드를 최신순으로 최대 20개 요청
twitter search "인공지능" --type latest --lang ko -n 20 --json

# 정확한 문구 검색
twitter search '"AI agent"' --type latest -n 20 --json

# 승인된 작성자의 글 중 AI 관련 글, 고정 날짜 예시
twitter search "AI" --from HANDLE --type latest \
  --since 2026-10-01 --until 2026-10-02 -n 20 --json
```

| 옵션 | 의미 | 자동화 시 주의 |
| --- | --- | --- |
| `--type latest` | 최신 검색 탭 선택 | 기본 Top 검색과 다르므로 명시 |
| `--from HANDLE` | 특정 작성자 조건 | 반환된 실제 작성자도 다시 검사 |
| `--lang ko` | 언어 조건 | 언어 판정 오류 가능 |
| `--since`, `--until` | 검색 날짜 제약 | 응답의 UTC 시각을 별도 검증 |
| `-n 20` | 요청 결과 상한 | 정확히 20개나 전체 기간 확보를 보장하지 않음 |
| `--json` | 기계 처리용 표준출력 | 명시하지 않으면 비대화형에서 YAML일 수 있음 |

날짜 예시는 명령 문법을 설명하는 고정값이다. 반복 작업에 그대로 넣으면 같은 과거 구간만 읽는다. [증분 수집](06-storage-and-incremental.md)의 대상별 window에서 매번 계산해야 한다.

## 3.2 고정 계정 watchlist

```bash
# 프로필의 실제 ID·handle 확인
twitter user HANDLE --json

# 최근 계정 글 후보
twitter user-posts HANDLE -n 20 --json

# 승인된 글 하나와 대화 문맥
twitter tweet TWEET_ID -n 20 --json
```

`user-posts`는 확인한 버전에서 `--since`, `--until`, 외부 `--cursor` 옵션을 제공하지 않는다. 최근 글을 가져온 다음 시각을 검증하거나, 기간 조건이 필요한 경우 `search --from`을 조합한다.

계정 글에는 repost 등이 섞일 수 있다. watchlist 대상·실제 작성자·`isRetweet`·`retweetedBy`를 구분하고 정책의 repost/답글 제외를 적용한다. 필요한 제외 판단 정보가 없으면 추정하지 말고 상세 확인 또는 보류한다.

`tweet` 응답은 대화의 여러 글을 담을 수 있다. 작은 `-n`에서 앞선 글만 나오고 요청한 답글이 빠질 수 있으므로 **요청 ID가 실제 응답에 있는지** 확인한다. 스레드 전체를 읽었다고 자동으로 주장하지 않는다.

## 3.3 관계 목록을 기준으로 수집하기

```bash
# HANDLE을 팔로우하는 사람들
twitter followers HANDLE -n 20 --json

# HANDLE이 팔로우하는 사람들
twitter following HANDLE -n 20 --json
```

이 응답은 **사용자 목록**이다. 수집 흐름은 다음과 같다.

```text
관계 방향·기준 계정·요청 상한 승인
→ followers 또는 following 조회
→ 사용자 ID·screenName을 후보 스냅샷으로 보존
→ 중복·정책·범위 검토
→ 사람이 승인한 watchlist 확정
→ watchlist 계정별 user-posts 또는 search --from
→ 작성자·시각 검사 후 콘텐츠 저장
```

관계 목록과 콘텐츠 수집을 같은 주기로 실행할 필요는 없다. 관계 후보 갱신은 낮은 빈도·별도 승인, 글 조회는 고정 watchlist 기준으로 반복하면 예산과 범위가 안정적이다. 후보의 후보를 연쇄적으로 펼치지 않는다.

- 계정명은 실제 응답의 `screenName`을 사용한다. 다른 도구 예제의 `screen_name`을 이 CLI에 그대로 적용하지 않는다.
- 표시 이름으로 계정을 추정하지 않는다. ID와 당시 handle을 함께 보관한다.
- 프로필의 `followers`와 `following` **숫자 필드**는 관계 목록 자체가 아니다.
- 팔로워 수가 많다는 이유로 정보의 진실성·전문성을 확정하지 않는다.

## 3.4 following 피드와 목록은 다르다

```bash
twitter feed --type following -n 20 --json
```

이것은 **로그인한 계정 기준의 글 피드**다. `twitter following HANDLE`은 **지정 계정의 계정 목록**이다. 어떤 계정의 following 목록을 넘겼다고 그 사람의 개인 피드를 읽는 기능이 되는 것은 아니다.

정해진 계정군을 일관되게 관측하려면 피드보다 고정 watchlist를 권장한다. 피드 순서·범위·누락은 계정별 최신 글 조회와 다를 수 있다.

## 3.5 JSON의 모양과 저장 주의

일반 `--json` 표준출력의 조회 결과:

| 항목 | 위치 |
| --- | --- |
| 성공 여부 | `ok` |
| 형식 버전 | `schema_version` |
| 검색·계정 글·관계 목록 | `data[]` |
| 프로필 | `data` 객체 |
| 글 ID·본문 | `data[].id`, `data[].text` |
| 작성자 | `data[].author.id`, `data[].author.screenName` |
| 시각 | `createdAtISO`; 필요하면 검증된 `createdAt` 파서 |
| 반응 수 | `metrics.likes`, `metrics.retweets` 등 |
| 오류 | `error.code`, `error.message` |

**출력 파일 옵션과 stdout 형식은 같지 않을 수 있다.** 확인한 버전에서 `twitter ... -o file.json`은 bare 배열이고, `twitter ... --json`의 stdout은 `ok/data` envelope다. 파서를 하나로 작성해 양쪽에 그대로 쓰지 않는다. 이 강의에서는 `--json` stdout을 subprocess로 받고 검증 후 저장하는 방식을 기준으로 한다.

`-c`/compact 출력은 본문·필드가 축약될 수 있으므로 원문 수집 경로에서 사용하지 않는다. 응답을 통째로 에이전트에게 출력하지 말고 필요한 콘텐츠와 건수만 넘긴다.

## 3.6 성공 검사

1. subprocess가 시간 제한 안에 정상 종료했는가?
2. JSON 파싱 성공, `ok: true`, 예상한 `data` 자료형인가?
3. 각 글 ID·작성자·시각을 확인했는가?
4. account 조회라면 승인한 작성자만 포함되는가? repost·답글 정책도 적용했는가?
5. 응답 시각이 고정한 `[start, end)` UTC 범위에 있는가?
6. 범위 밖·중복·보류 건수와 유효 건수를 따로 기록했는가?
7. 실제 저장 파일과 중복 장부를 검사했는가?

`ok: true`에 빈 배열이 올 수 있다. 인증·형식이 정상인 0건과 실패로 인한 0건을 구분한다. 넓은 다중 계정 검색의 0건만 보고 각 계정이 비활동 상태라고 판단하지 않는다.

## 3.7 한계와 중단 조건

- 검색·타임라인·관계 목록에는 내부 페이지 제한이 있다. 확인한 검색/계정/관계 명령은 사용자가 이어받을 cursor를 모두 제공하는 것이 아니다.
- `-n`을 크게 올린다고 누락이 사라지지 않는다. 상한 도달·의심스러운 동일 건수·예상보다 좁은 범위는 `partial`/`possibly_truncated`로 기록한다.
- 보호 계정·삭제·검색 인덱싱 지연·권한 문제를 다른 경로로 강제 우회하지 않는다.
- 401/인증 만료는 운영자 재인증, 403은 권한·정책 확인, 429는 서버의 대기 지시와 승인된 예산에 따른 제한된 재시도 후 중단한다.
- 특정 warning이 있었더라도 실제 응답 검증에 성공한 경우만 nonfatal로 분류한다. warning을 모두 숨기거나 성공 데이터를 발명하지 않는다.

### 이해 확인

**Q. `followers` 결과 20명을 곧바로 Cron의 수집 목록에 넣어도 되는가?**

아니다. 목록 조회 범위와 그 계정들의 지속적 콘텐츠 수집 범위는 다르다. 후보를 검토하고 승인된 watchlist로 확정한 뒤 적용한다.

## 근거

- [twitter CLI 명령 구현](https://github.com/public-clis/twitter-cli/blob/7c634e0d396b1e7af9f63315b414925fe4f29ae7/twitter_cli/cli.py)
- [구조화 출력 schema](https://github.com/public-clis/twitter-cli/blob/7c634e0d396b1e7af9f63315b414925fe4f29ae7/SCHEMA.md)
- [JSON serialization](https://github.com/public-clis/twitter-cli/blob/7c634e0d396b1e7af9f63315b414925fe4f29ae7/twitter_cli/serialization.py)
- [페이지 조회 구현](https://github.com/public-clis/twitter-cli/blob/7c634e0d396b1e7af9f63315b414925fe4f29ae7/twitter_cli/client.py)
