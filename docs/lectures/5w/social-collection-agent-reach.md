# Agent-Reach로 X·Reddit 데이터 수집 — 쉬운 방법

> 확인 기준: **2026-09-28 13:22 UTC / 22:22 KST**. GitHub 저장소 문서, 이 컴퓨터에 설치된 CLI의 실제 `--help` 출력, Reddit 공식 검색 도움말을 대조했습니다.  
> 범위: 방법 설명만. 이 문서를 쓰는 동안 X·Reddit 실제 수집·로그인·인증은 하지 않았고, 어떤 계정 정보도 다루지 않았습니다. 이 저장소는 논문 Wiki이므로 여기에 소셜 수집 자동화를 새로 만들려면 별도 승인이 필요합니다([범위](../../../AGENTS.md)).

## 0. 주요기능

### 1. 다양한 주요 플랫폼 데이터 접근 및 수집

AI 에이전트가 단일 환경에서 인터넷상의 주요 플랫폼과 소셜 미디어 데이터를 수집할 수 있도록 지원합니다:

* **X (Twitter)**: 브라우저 Cookie 인증을 통해 트윗 검색, 타임라인, 트윗/아티클 읽기 지원.

* **Reddit**: 인증 기반`rdt-cli`)으로 게시글 검색, 글 전체 및 댓글 수집.

* **YouTube &amp; Bilibili**: 자막 추출 및 동영상/정보 검색.

* **GitHub**: 공식 `gh CLI`를 활용해 공개 저장소 감상, 이슈/PR 및 검색 지원.

* **웹페이지 및 기타 서비스**:

  * **일반 웹페이지**: 모든 URL을 깨끗한 Markdown으로 변환 (Jina Reader 활용).

  * **기타 지원**: RSS 피드, 샤오홍수(XiaoHongShu), LinkedIn, 위챗 공식 계정 글, 팟캐스트 음성 변환(Xiaoyuzhou) 등 지원.



### 2. 단 한 줄의 명령어로 간편한 설치 및 통합

* 여러 플랫폼의 의존성 설치나 설정을 직접 디버깅할 필요 없이, 단일 설치 명령어를 AI 에이전트에 전달하는 것만으로 환경을 구성합니다.

* Claude Code, Cursor, Windsurf, OpenClaw 등 Shell 명령어 실행이 가능한 모든 AI 에이전트 환경과 호환됩니다.



### 3. 완전 무료 및 강력한 프라이버시 보호

* 모든 내장 도구와 연결 기능은 유료 API Key 없이 무료로 작동합니다.

* 세션 인증에 사용되는 Cookie 값은 로컬 환경에만 안전하게 유지되며 외부로 업로드되지 않습니다.



### 4. 내장 진단 도구 `agent-reach doctor`

* `agent-reach doctor` 단일 명령을 실행하여 현재 작동 가능한 채널, 설정이 필요한 플랫폼, 수정 방법을 한눈에 파악할 수 있습니다.



### 5. 유연한 스캐폴딩(Scaffolding) 구조

* 복잡한 프레임워크 레이어를 씌우지 않고, 각 플랫폼에 적합한 업스트림 CLI 도구(twitter-cli, rdt-cli, yt-dlp 등)를 직접 호출하는 방식입니다.

* 필요에 따라 각 플랫폼 연결 백엔드를 원하는 도구로 자유롭게 교체 및 확장할 수 있습니다.



## 1. 한 문장으로 이해하기

**Agent-Reach는 에이전트에게 주는 "만능 리모컨 세트"라서, 설치 도우미로 리모컨을 장착하면 X와 Reddit을 터미널 명령으로 읽을 수 있습니다.**

리모컨으로는 방에 있는 TV(웹사이트)를 켜고 채널(키워드·계정)을 고를 수 있을 뿐, TV를 직접 만들거나 고치지는 않습니다. 읽어 온 내용을 어디에 어떻게 쌓을지는 여전히 사용자와 에이전트의 몫입니다.


| 쉬운 비유       | 실제 이름                        | 하는 일                              |
| ----------- | ---------------------------- | --------------------------------- |
| 리모컨 설치 도우미  | `agent-reach`                | 사이트별 리모컨을 설치·점검합니다.               |
| X용 리모컨      | `twitter`, `opencli twitter` | 트윗 검색, 계정 글, 팔로워 목록을 읽습니다.        |
| Reddit용 리모컨 | `rdt`, `opencli reddit`      | 게시물 검색, 사용자 활동, 댓글을 읽습니다.         |
| 출입증         | 브라우저 로그인(쿠키)                 | 비공개·맞춤 화면을 보려면 1회 로그인이 필요합니다.     |
| 정리된 서류 봉투   | `--json`, `-o 파일`            | 결과를 기계가 읽기 좋은 JSON으로 묶어 파일로 내줍니다. |


### 리모컨이 두 개씩 있는 이유

X와 Reddit 각각에 전용 CLI(`twitter`, `rdt`)와 브라우저 방식 CLI(`opencli ...`)가 있습니다.

- **전용 CLI** — 빠르고 가볍습니다. 일반적인 검색·계정 읽기에 먼저 씁니다.
- `**opencli**` — 실제 브라우저를 대리로 움직입니다. 전용 CLI가 막혔을 때, 팔로워 목록처럼 로그인 화면 뒤에 있는 것을 볼 때 씁니다. `--window background` 옵션으로 창을 숨겨 둘 수 있습니다.

둘 다 이 컴퓨터에 이미 설치되어 있습니다(관측: `agent-reach` 설치 기록, `~/.agent-reach/`의 `opencli 1.8.8` 수신 증빙). 새 컴퓨터에서는 아래처럼 처음부터 설치합니다.

## 2. 처음 준비하기 (이미 되어 있으면 건너뜁니다)

```text
1단계  uv tool install agent-reach   ← 설치 도우미를 설치
2단계  agent-reach install           ← 사이트별 리모컨(twitter, rdt, opencli) 설치
3단계  agent-reach doctor            ← 전체 건강 검진
```

설치 도우미가 할 수 있는 일은 `setup`, `install`, `configure`, `doctor`, `uninstall`, `skill`, `format`, `transcribe`, `check-update`, `watch`, `version`뿐입니다. 수집 자체는 도우미가 아니라 사이트별 리모컨이 합니다.

### 출입증 만들기 (로그인)

비로그인 상태로도 공개 검색은 되지만, 맞춤 피드·저장함·일부 제한 화면은 로그인된 계정만 볼 수 있습니다.

```bash
# 상태부터 확인 — 이미 출입증이 있는지 본다
twitter status          # X 세션 인증 여부 (twitter CLI)
rdt status              # Reddit 인증 여부 (rdt CLI)

# 출입증이 없을 때 — 브라우저 창이 열리고 로그인을 기다립니다
opencli twitter login
opencli reddit login
rdt login               # 브라우저 쿠키 추출 방식

# 어떤 계정으로 들어와 있는지 확인
twitter whoami
rdt whoami
```

비밀번호는 여러분이 브라우저 창에서 직접 입력합니다. CLI나 에이전트에게 비밀번호를 알려 주지 않고, 문서에도 절대 적지 않습니다.

## 3. 두 가지 수집 방식 — "누구"로 찾을까, "무엇"으로 찾을까


| 방식         | 비유                         | 이런 때 씁니다                         |
| ---------- | -------------------------- | -------------------------------- |
| **계정 기반**  | 특정 사람의 사서함을 구독해 편지를 모두 모은다 | 관심 있는 계정·사용자의 활동 전체를 놓치지 않으려 할 때 |
| **키워드 기반** | 단어가 적힌 편지를 우체국 전체에서 찾아낸다   | 주제 중심으로 여러 사람의 이야기를 한 번에 모을 때    |


둘을 섞을 수도 있습니다. "이 계정의 글 중에서 이 단어가 든 것만"처럼 좁히는 것이 가능합니다.

### "팔로워"의 차이를 먼저 알아두세요

- **X**: 팔로워 목록을 읽는 명령이 있습니다. "어떤 계정을 팔로우하는 사람들"을 뽑은 뒤, 그 사람들의 글을 이어서 읽는 2단계 조리법이 가능합니다.
- **Reddit**: rdt와 opencli reddit의 명령 목록에 팔로워 목록 명령이 없습니다(관측). 대신 `author:사용자이름` 검색 연산자나 사용자 활동 명령으로 "특정 사용자 글 모으기"를 합니다. Reddit에서는 사람보다 **서브레딧(동호회 방)**이 기준이 되는 경우가 많습니다.

## 4. X 수집 조리법

### 4.1 키워드 기반

```bash
# 기본: 단어 검색 + 최근 날짜 제한 + JSON 파일로 저장
twitter search "AI agent security" --since 2026-09-01 -n 100 --json -o x-keyword.json

# 좁히기: 언어·최소 좋아요·리트윗 제외
twitter search "AI agent" --lang en --min-likes 100 --exclude retweets -n 50 --json

# 사람 지정: 그 계정이 쓴 글만
twitter search "launch" --from elonmusk -n 50 --json

# opencli 버전 (브라우저 방식): 실시간 탭(live)에서 최신순 100개
opencli twitter search "AI agent security" --product live --limit 100 -f json > x-keyword-live.json
```

주요 재료(실제 `--help`에서 확인한 것들):


| 재료                                         | 뜻                       |
| ------------------------------------------ | ----------------------- |
| `--from 계정` / `--to 계정`                    | 그 계정이 쓴 글 / 그 계정에게 답한 글 |
| `--lang en`                                | 언어 제한                   |
| `--since` / `--until`                      | 날짜 범위 (`YYYY-MM-DD`)    |
| `--min-likes 100` / `--min-retweets 10`    | 반응 수 하한                 |
| `--has links` / `--has videos`             | 링크·영상 포함 글만             |
| `--exclude retweets` / `--exclude replies` | 리트윗·답글 제외               |
| `-n 100`                                   | 최대 개수                   |
| `--json -o 파일`                             | JSON 파일로 저장             |


`opencli twitter search`는 X의 원래 검색 연산자(`"정확한 문구"`, `#태그`, `OR`, `lang:en`, `since:`, `from:`)를 그대로 통과시킵니다. 복잡한 조건은 이 쪽이 편합니다.

### 4.2 특정 계정의 글 모으기

```bash
# 프로필 확인 (팔로워 수 등)
twitter user karpathy --json

# 최근 글 목록
twitter user-posts karpathy -n 100 --json -o x-user-karpathy.json

# opencli 버전: 최대 10,000개까지 페이지 넘겨서 수집, 요청 사이 쉬는 간격 지정
opencli twitter tweets karpathy --limit 500 --page-delay 2 -f json > x-user-karpathy.json
```

`--page-delay 2`(기본값)는 페이지 사이에 2초 쉬는 것입니다. 너무 빠르게 계속 요청하면 일반 사용자처럼 보이지 않아 제한을 받을 수 있으니 기본값을 유지하세요.

### 4.3 팔로워 기반 (2단계 조리법)

```bash
# 1단계: 어떤 계정을 팔로우하는 사람들 목록을 뽑는다
opencli twitter followers karpathy --limit 200 -f json > x-followers.json

# (반대 방향: 그 계정이 팔로우하는 사람들)
opencli twitter following karpathy --limit 200 -f json > x-following.json

# 2단계: 뽑아낸 팔로워 각각의 최근 글을 읽는다 (계정 이름을 하나씩 넣어 반복)
opencli twitter tweets <팔로워계정> --limit 20 -f json > x-follower-posts.json
```

1단계 결과 JSON의 `screen_name` 값을 2단계에 넣는 흐름입니다. 반복 작업이므로 에이전트에게 "followers.json에서 계정 목록을 꺼내 각각 최근 글 20개씩 모아 줘"라고 맡기면 편합니다. 전용 `twitter` CLI에도 `followers`, `following` 명령이 있습니다만, 옵션이 가장 잘 확인된 것은 `opencli` 쪽입니다.

## 5. Reddit 수집 조리법

### 5.1 키워드 기반

```bash
# 전체 Reddit에서 검색 + 기간 제한 + JSON 저장
rdt search "AI agent security" -t week -n 100 --json -o reddit-keyword.json

# 서브레딧 안에서만, 인기순으로
rdt search "LLM" -r MachineLearning -s top -t month -n 50 --json

# 서브레딗 방 자체를 최신순으로 훑기
rdt sub MachineLearning -s new -n 100 --json -o reddit-sub-new.json

# opencli 버전
opencli reddit search "AI agent security" --subreddit MachineLearning --sort new --time week --limit 100 -f json > reddit-keyword.json
```


| 재료                         | 뜻                                      |
| -------------------------- | -------------------------------------- |
| `-r 서브레딧` / `--subreddit`  | 그 방 안에서만 검색                            |
| `-s top` (`--sort`)        | 정렬: relevance, hot, top, new, comments |
| `-t week` (`--time`)       | 기간: hour, day, week, month, year, all  |
| `-n 100` / `--limit`       | 최대 개수                                  |
| `--json -o 파일` / `-f json` | JSON 저장                                |


### 5.2 검색창 비밀 문구 (Reddit 공식 연산자)

검색어 안에 특별한 단어를 넣으면 조건을 좁힐 수 있습니다. Reddit 공식 도움말 기준이며, **콜론 뒤에 공백 없이** 붙입니다.


| 문구                          | 뜻           | 예                            |
| --------------------------- | ----------- | ---------------------------- |
| `author:이름`                 | 그 사용자가 쓴 글만 | `author:reddit`              |
| `subreddit:방이름`             | 그 서브레딧만     | `subreddit:pics`             |
| `title:단어`                  | 제목에 포함      | `title:benchmark`            |
| `selftext:단어`               | 본문 텍스트에 포함  | `selftext:latency`           |
| `site:도메인`                  | 링크 도메인 지정   | `site:arxiv.org`             |
| `url:단어`                    | 링크 주소에 포함   | `url:github`                 |
| `flair:단어`                  | 플레어 텍스트 지정  | `flair:paper`                |
| `self:true`                 | 글만(링크 제외)   | `self:true`                  |
| `AND` / `OR` / `NOT`, `( )` | 여러 조합       | `cats NOT (sonic OR shadow)` |


```bash
# 조합 예: 특정 사용자의 글 중 제목에 단어가 든 것
rdt search "author:사용자이름 title:benchmark" -n 100 --json
```

### 5.3 특정 사용자 활동 모으기 (Reddit식 "계정 기반")

```bash
# 프로필 보기
rdt user 사용자이름

# 올린 글 / 댓글 따로 모으기
rdt user-posts 사용자이름 -n 100 --json -o reddit-user-posts.json
rdt user-comments 사용자이름 -n 100 --json -o reddit-user-comments.json

# opencli 버전 (댓글: --limit)
opencli reddit user-posts 사용자이름 --limit 100 -f json > reddit-user-posts.json
opencli reddit user-comments 사용자이름 --limit 100 -f json > reddit-user-comments.json

# 글 하나를 댓글까지 통째로 읽기
rdt read <게시물ID> --json -o reddit-thread.json
```

## 6. 저장과 반복

- **한 번 뽑기**: 위처럼 `-o 파일` 또는 `-f json > 파일`로 JSON을 남깁니다. 다음에 같은 조건으로 다시 실행하면 새 결과로 덮어쓰므로, 날짜를 파일 이름에 넣는 습관이 안전합니다.
- **정기 반복**: Hermes의 터미널 도구로 이 명령들을 실행하도록 맡기거나, Cron으로 예약할 수도 있습니다. 다만 **이 논문 저장소에 새 자동화를 만드는 것은 별도 승인 대상**입니다. 이미 승인된 논문 수집 Cron([해당 문서](paper-collection-cron.md))과는 무관합니다.
- **에이전트에게 시킬 때**: "followers.json에서 screen_name을 꺼내 각각 opencli twitter tweets로 최근 글 20개씩 모아 kst 날짜 폴더에 저장"처럼 파일 입출력까지 정확히 지정하면 실수가 줄어듭니다.

## 7. 예의와 안전 수칙

1. **속도 조절**: `--page-delay` 기본값을 유지하고, 수백 계정을 연달아 긁지 않습니다. 사이트 보호 장치는 사람보다 빠른 요청을 차단합니다.
2. **계정 보호**: 비밀번호는 브라우저 로그인 창에서만 입력하고, 어떤 문서·명령·대화에도 옮겨 적지 않습니다.
3. **공개된 것만**: 로그인하면 보이는 것도 결국 계정 약관 아래에 있습니다. 대량 재가공·재게시는 각 사이트 규칙을 먼저 확인하세요.
4. **개인정보 인식**: 팔로워 목록·사용자 활동은 사람에 대한 정보입니다. 저장 위치와 공개 범위를 미리 정해 둡니다.
5. **수집은 읽기**: 이 문서의 명령은 읽기용입니다. `post`, `follow`, `upvote` 같은 쓰기 명령도 리모컨에 있지만, 실행은 신중히 결정해야 합니다.

## 8. 이 문서를 쓰면서 하지 않은 것

- X·Reddit에 대한 실제 검색·계정·팔로워 요청을 실행하지 않았습니다. 확인한 것은 설치된 CLI의 `--help`와 공식 문서입니다.
- 어떤 계정에도 로그인하지 않았고, 인증 상태를 변경하지 않았습니다.
- 소셜 수집 Cron이나 반복 작업을 만들지 않았습니다. 논문 수집 Cron `4cff5b4f10ec`과 원본·수집 상태도 그대로입니다.
- Agent-Reach 구성요소를 설치·제거·변경하지 않았습니다.

## 9. 한 장 요약 (복사해서 쓰는 명령들)

```bash
# 준비 점검
agent-reach doctor && twitter status && rdt status

# X — 키워드
twitter search "키워드" --since 2026-09-01 -n 100 --json -o x.json
# X — 계정 글
twitter user-posts 계정 -n 100 --json -o x-user.json
# X — 팔로워 → 각 계정 글 (2단계)
opencli twitter followers 계정 --limit 200 -f json > x-followers.json
opencli twitter tweets 팔로워계정 --limit 20 -f json > x-fp.json

# Reddit — 키워드
rdt search "키워드" -t week -n 100 --json -o r.json
# Reddit — 서브레딧
rdt sub 서브레딧 -s new -n 100 --json -o r-sub.json
# Reddit — 사용자 활동
rdt user-posts 사용자 -n 100 --json -o r-user.json
rdt search "author:사용자 title:단어" -n 100 --json
```

관련 문서: [논문 수집 자동화 — 쉬운 안내](paper-collection.md) · [논문 수집 Cron — 생성 방법과 현재 구성](paper-collection-cron.md) · [Agent-Reach 저장소](https://github.com/Panniantong/Agent-Reach/tree/main)