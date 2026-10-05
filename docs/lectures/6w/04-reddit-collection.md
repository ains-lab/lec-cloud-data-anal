# 4. Reddit 수집 — 키워드, 커뮤니티, 작성자

[목차](README.md) · 이전: [X](03-x-collection.md) · 다음: [YouTube](05-youtube-collection.md)

**Reddit은 사람별 글뿐 아니라 주제별 방을 기준으로 읽는 것이 중요하다.** `subreddit`은 특정 주제의 커뮤니티 방, `post`는 그 안의 게시글, `comment`는 댓글이다.

> 명령은 `rdt-cli 0.4.2`의 help·공개 소스 기준이다. 실제 Reddit 조회를 수행하지 않았다. 이 장은 기술적 기능 설명이며 아래 정책 조건을 만족하기 전에는 수집 예시를 실행하지 않는다.

## 4.1 실행 전에 이용 목적과 허가 확인

Reddit의 현재 **Responsible Builder Policy**는 API 접근에 명시적 승인을 요구하며, 연구에는 **Reddit for Researchers(RFR)** 경로를 요구한다. RFR 밖에서 수집한 Reddit 데이터의 연구 이용은 해당 정책을 위반한다고 명시되어 있다.

- 학술 연구 목적이라면 일반 rdt 예제를 연구 수집기로 곧바로 돌리지 않는다. RFR 승인과 실제 허용된 접근 방식을 먼저 확인한다.
- “수업용”, “공개 게시물”, “내 계정으로 로그인”만으로 예외를 가정하지 않는다. 목적·방법이 불명확하면 담당자/플랫폼의 허가를 확인할 때까지 정지한다.
- 쿠키 기반 제3자 CLI도 정책 적용을 피하는 수단이 아니다. 이 도구가 설치되었다는 사실은 해당 이용이 허용되었다는 증거가 아니다.
- 허가가 없다면 help·문서·출력 구조 설명까지만 학습한다. 대체 자료는 합성임을 명시한 로컬 fixture 또는 별도 사용 허가를 받은 데이터로 정한다.

승인된 목적·방법·범위를 `RUNBOOK.md`에 기록한다. `policy_reviewed: true` 같은 설정만으로 실제 허가를 만들어 내지 않는다.

## 4.2 키워드 검색

```bash
# Reddit 검색 결과를 최신순으로 조회
rdt search "machine learning" --sort new --time day -n 20 --json

# 특정 subreddit 안에서 조회
rdt search "python" -r learnpython --sort new --time week -n 20 --json

# 작성자 조건과 제목 조건의 조합
rdt search "author:USERNAME title:benchmark" --sort new --time week -n 20 --json
```

`USERNAME`은 승인한 실제 작성자 이름으로 바꾼다. `learnpython`은 명령 문법을 설명하는 커뮤니티 예시이지 수집을 승인한 실제 대상이 아니다.

- `--sort new`: 최신순. relevance/top과 목적이 다르다.
- `--time day/week/month/...`: 서버의 상대적 검색 기간. 정확한 UTC 시작·끝 경계를 대체하지 않는다.
- `-r`: subreddit 범위 제한.
- `-n`: 요청 개수 상한.
- `author:`, `title:`, `subreddit:` 같은 검색 연산자는 콜론 뒤 공백 없이 쓴다.

검색은 게시물 중심이다. 게시물 검색에 성공했다고 전체 댓글에서 같은 키워드를 검색한 것이 아니다.

## 4.3 커뮤니티 또는 작성자 기반

```bash
# 커뮤니티의 최근 글
rdt sub learnpython --sort new -n 20 --json

# 특정 사용자의 게시물
rdt user-posts USERNAME -n 20 --json

# 특정 사용자의 댓글 — 별도로 허용한 경우에만
rdt user-comments USERNAME -n 20 --json
```

확인한 `rdt 0.4.2`에는 X식 사용자 `followers`/`following` 열거 명령이 없다. 이 강의에서는 승인한 `users` 또는 `subreddits`를 watchlist로 사용한다. 이를 “Reddit 전체에서 영구적으로 팔로워 조회 불가능”이라는 주장으로 확대하지 않는다.

로그인 계정의 구독 커뮤니티를 읽는 `rdt feed --subs-only`는 **subreddit 구독** 기준이지 특정 사용자의 팔로워 목록이 아니다. 수업에서는 개인 맞춤 피드를 자동으로 범위에 넣지 않고 명시적인 커뮤니티 목록을 권장한다.

## 4.4 페이지를 이어서 읽기

**pagination**은 다음 페이지를 넘기는 것이다. **cursor**는 다음 페이지 위치를 나타내는 반환값이다.

일반 검색·목록의 다음 페이지 값은 `data.data.after`에 있다. 값이 있으면 승인된 페이지/총 결과 예산 안에서 같은 조건에 `--after`를 추가한다.

```bash
rdt search "python" --sort new --time week -n 20 \
  --after CURSOR --json
```

`CURSOR`는 실제 응답값으로 바꾸며 추측해서 만들지 않는다. 검색어·sort·time·subreddit 조건을 첫 페이지와 동일하게 유지한다. subprocess 인자 배열로 전달하고 셸 문자열에 원문을 삽입하지 않는다.

- cursor가 반복되면 무한 순회를 중단한다.
- 다음 페이지가 남아 있는데 예산으로 멈추면 `partial`로 기록한다.
- 결과가 요청 상한보다 적다고 검색 전체를 다 읽었다고 단정하지 않는다.
- `--compact`는 pagination 정보를 없애거나 구조를 바꿀 수 있으므로 수집 경로에서 사용하지 않는다.

## 4.5 게시글과 댓글 읽기

```bash
rdt read POST_ID --sort new -n 20 --json
```

`POST_ID`는 실제 게시물 ID다. `read`의 출력은 검색 목록과 다르게 정규화되어 있다.

| 응답 | 읽을 위치 |
| --- | --- |
| 검색·sub·user-posts·user-comments | `data.data.children[]` |
| 각 목록 항목의 종류와 본문 | `children[].kind`, `children[].data` |
| 목록 다음 페이지 | `data.data.after` |
| `read`의 게시물 | `data.post` |
| `read`의 댓글 | `data.comments[]` |
| 아직 펼치지 않은 댓글 정보 | `data.more_count`, `data.more_children` |

`read`를 Reddit 원시 API의 `[게시물 목록, 댓글 목록]` 배열로 파싱하면 틀린다. 댓글은 `replies[]` 안에 더 있을 수 있다. `more_count`가 남거나 깊이·개수 제한을 적용했다면 “전체 댓글”로 표시하지 않는다.

댓글 수집은 초기 설정에서 꺼 둔다. 필요하면 게시물·댓글 상한, 깊이, 보관 목적을 추가로 승인한다. 사용자 댓글에는 개인정보나 민감한 경험이 포함될 수 있으므로 분석 필요성 없이 광범위하게 보관하지 않는다.

## 4.6 JSON 계약과 비밀정보 제거

일반 `--json`은 최상위 `ok`, `schema_version`, `data` envelope를 사용한다. 비대화형 기본 형식은 YAML일 수 있으므로 `--json`을 명시한다.

- 글: `id`, `name`(예: `t3_...`), `title`, `author`, `subreddit`, `created_utc`, `permalink`, `selftext` 등.
- 댓글 목록: `name`(예: `t1_...`), `body`, `author`, `created_utc`, `parent_id`, `link_id` 등.
- `read`의 정규화 댓글은 `fullname`, `parent_fullname`, `replies` 등 다른 필드명을 사용할 수 있다.
- `created_utc`는 UTC Unix timestamp다. 코드로 timezone-aware UTC 시각으로 변환한다.
- 상대 `permalink`를 공개 Reddit 원문 URL로 바꿀 때 호스트와 경로를 검증한다. 외부 `url`은 게시물이 링크한 다른 사이트일 수 있다.

응답 전체에는 `modhash`·세션 메타데이터 등이 포함될 수 있다. 이 강의의 captures에는 허용한 콘텐츠 필드만 남긴다. 응답 전체를 채팅·모델 입력·공유 로그에 복사하지 않는다.

`--compact`의 댓글 변환에서는 본문이 보존되지 않을 수 있다. 원문 보존을 원하면 일반 `--json` 경로를 사용하고 실제 `body`가 있는지 검증한다.

## 4.7 오류 처리와 완료 기준

1. 이용 목적과 접근 방법의 허가가 확인되어야 한다.
2. 비대화형 인증 경계가 적용되고 subprocess 정상 종료·`ok: true`를 확인한다.
3. 예상 응답 구조·각 fullname·작성자/subreddit·시각을 검사한다.
4. cursor 종료/예산 중단과 댓글 미확보를 구분한다.
5. 삭제된 글·삭제된 작성자를 추정 복원하지 않는다.
6. 검증 후 파일 저장과 상태 갱신을 따로 확인한다.

| 실패 | 대응 |
| --- | --- |
| 인증 누락·만료 | `blocked_auth`, 사람이 승인된 절차로 재인증 |
| 403/접근 제한 | 목적·정책·권한 확인, 우회하지 않음 |
| 429 | 응답의 대기 지시 우선, 제한된 재시도·주기 조정 |
| HTML/로그가 JSON 대신 출력 | `invalid_response`, 0건 성공으로 처리하지 않음 |
| 일부 페이지만 저장 | `partial`, 미완료 cursor/구간 보존 |

### 이해 확인

**Q. `rdt user-posts`가 성공하면 해당 사용자의 댓글도 수집한 것인가?**

아니다. 제출한 게시물과 댓글은 별도 데이터다. 댓글을 읽으려면 별도 허가·명령·출력 검증이 필요하다.

## 근거

- [Reddit Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy)
- [Reddit 연구·개발 도구 이용 안내](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data)
- [Reddit for Researchers](https://support.reddithelp.com/hc/en-us/articles/49381918834964-Reddit-for-Researchers-Program)
- [Reddit 검색 도움말](https://support.reddithelp.com/hc/en-us/articles/19696541895316-Available-search-features)
- [rdt 검색 구현](https://github.com/public-clis/rdt-cli/blob/5e4fb3720d5c174e976cd425ccc3b879d52cac66/rdt_cli/commands/search.py)
- [rdt 목록 조회 구현](https://github.com/public-clis/rdt-cli/blob/5e4fb3720d5c174e976cd425ccc3b879d52cac66/rdt_cli/commands/browse.py)
- [rdt 게시물 읽기 구현](https://github.com/public-clis/rdt-cli/blob/5e4fb3720d5c174e976cd425ccc3b879d52cac66/rdt_cli/commands/post.py)
- [rdt 구조화 출력](https://github.com/public-clis/rdt-cli/blob/5e4fb3720d5c174e976cd425ccc3b879d52cac66/SCHEMA.md)
