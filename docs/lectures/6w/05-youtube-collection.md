# 5. YouTube 수집 — 영상 목록과 자막을 구분하기

[목차](README.md) · 이전: [Reddit](04-reddit-collection.md) · 다음: [저장·증분](06-storage-and-incremental.md)

**영상 제목·작성자·날짜를 모으는 것은 영상을 내려받는 일이 아니다.** 도서관의 책 목록을 만드는 것과 책 전체를 복사하는 것이 다른 것과 같다.

> `yt-dlp 2026.08.19` help·공식 문서·옵션 파싱을 기준으로 설명한다. 실제 YouTube 검색·영상·자막 접근 성공은 검증하지 않았다. `CHANNEL_ID`, `VIDEO_ID`는 승인한 실제 ID로 바꾼다.

## 5.1 Agent Reach와 yt-dlp의 역할

Agent Reach가 YouTube용으로 안내하는 upstream 도구는 `yt-dlp`다. `agent-reach search youtube` 같은 통합 명령을 가정하지 않는다.

```bash
yt-dlp --version
yt-dlp --help
node --version
```

아래 예시는 작성 환경에서 확인한 Node runtime을 명시한다. 다른 지원 runtime을 사용할 때는 해당 버전의 help와 설치 상태에 맞춘다. JavaScript runtime 및 필요한 EJS 구성요소의 설치는 별도 승인·확인 대상이다. doctor의 정상 진단도 특정 영상의 접근 성공을 증명하지 않는다.

`--ignore-config`는 기존 개인 설정에 들어 있는 쿠키·다운로드 옵션이 예시에 섞이지 않게 한다. 따라서 필요한 JS runtime은 `--js-runtimes node`로 명시한다. 무쿠키 공개 조회가 막히면 차단 상태로 남기고, 쿠키 가져오기나 다른 경로로 자동 전환하지 않는다.

## 5.2 키워드로 후보 찾기

```bash
yt-dlp --ignore-config --js-runtimes node \
  --flat-playlist --skip-download --dump-json \
  'ytsearch20:클라우드 데이터 분석'
```

- `ytsearch20:`: 검색 결과 후보 최대 20개를 요청한다. 모든 관련 영상이나 정해진 기간 전체가 아니다.
- `--flat-playlist`: 영상마다 상세 페이지를 읽기보다 목록을 가볍게 가져온다.
- `--skip-download`: 영상·음성 파일을 내려받지 않는다.
- `--dump-json` 또는 `-j`: 영상별 JSON 한 줄, 즉 **JSONL** 출력.

검색은 제목·설명 등 YouTube의 검색 인덱스에 의존한다. 자막 전체의 키워드 검색이나 최신순 전수 수집으로 설명하지 않는다. `--flat-playlist` 결과에는 업로드 날짜·상세 설명 등이 없을 수 있으므로 이 단계는 **후보 발견**이다.

## 5.3 승인한 채널의 새 영상 후보

```bash
yt-dlp --ignore-config --js-runtimes node \
  --flat-playlist --skip-download \
  --playlist-items 1:20 --dump-json \
  'https://www.youtube.com/channel/CHANNEL_ID/videos'
```

| 탭 URL 끝부분 | 의미 |
| --- | --- |
| `/videos` | 일반 영상 탭 |
| `/shorts` | Shorts 탭 |
| `/streams` | 라이브 관련 탭. 현재 생방송 중인 영상만 뜻하지 않음 |
| 채널 루트 | 여러 업로드 탭으로 확장될 수 있어 범위가 넓어질 수 있음 |

범위를 안정적으로 유지하려면 watchlist에 **channel ID와 허용 탭**을 함께 둔다. 핸들은 바뀔 수 있으므로 승인 당시 핸들·표시 이름은 보조 정보로 기록한다. 없는 탭이나 제한된 채널의 오류를 0건 성공으로 처리하지 않는다.

여러 탭을 읽으려면 사용자가 승인한 실제 탭 URL을 한 줄에 하나씩 저장한 `approved-youtube-tabs.txt`를 먼저 준비한다. 이 파일은 강의에 제공되거나 현재 생성된 것이 아니다.

```bash
yt-dlp --ignore-config --js-runtimes node \
  --flat-playlist --skip-download \
  --playlist-items 1:20 --dump-json \
  --batch-file approved-youtube-tabs.txt
```

자동화에서는 대상별 실패를 분리하기 쉬운 **채널/탭별 호출**을 먼저 권장한다. 여러 입력을 한꺼번에 처리할 때에는 한 입력의 실패가 전체 성공으로 가려지지 않도록 출력과 상태를 매핑해야 한다.

## 5.4 날짜가 필요하면 상세 metadata 확인

다음 예시는 **영상 파일 다운로드 없이** 상세 정보를 조회하고 날짜를 제한한다.

```bash
yt-dlp --ignore-config --js-runtimes node \
  --no-flat-playlist --skip-download \
  --playlist-items 1:20 \
  --dateafter 20260901 --datebefore 20260930 \
  --match-filters 'upload_date' --dump-json \
  'https://www.youtube.com/channel/CHANNEL_ID/videos'
```

날짜 예시는 고정된 문법 예시이며 Cron에서는 실제 window에 맞게 계산한다.

- `--dateafter`와 `--datebefore`는 **양 끝 날짜를 포함**한다.
- `upload_date`는 UTC 기준 날짜다. KST 하루나 초 단위 게시 시각과 동일하지 않다.
- `--match-filters 'upload_date'`는 날짜가 없는 항목을 제외한다. 감사 가능한 수집에서는 앞 단계 후보 목록과 대조하여 이 제외를 보류 사유로 남긴다.
- `--flat-playlist`에 날짜 옵션만 붙이면 `upload_date`가 없는 후보에서 날짜 검사를 건너뛸 수 있다. 정확한 기간 필터로 취급하지 않는다.
- `--playlist-items 1:20`은 날짜 필터 이전에 읽는 후보 범위를 제한한다. 결과가 적어도 그 기간 영상이 적다고 단정하지 않는다.
- 근사 날짜 추출 옵션이 있더라도 정확한 timestamp로 승격하지 않는다.

더 엄격한 흐름은 후보 ID 수집 → 기존 ID 대조 → 승인 예산 안에서 신규 후보 상세 조회 → 실제 channel ID·시간 정밀도 확인 → 저장이다. 필수 날짜가 없는 항목은 수집 시각으로 채우지 않고 `pending_metadata`로 남긴다.

## 5.5 구독 채널과 구독자

| 말 | 실제 의미 | 이 강의의 경로 |
| --- | --- | --- |
| 내 subscriptions | 내가 구독한 채널 | 사용자가 승인한 채널 ID watchlist |
| 내 subscribers | 내 채널을 구독한 계정 | 기본 수집 범위에 넣지 않음 |
| 특정 채널의 전체 subscribers | 다른 채널을 구독한 전체 계정 | 일반 공개 목록으로 확보 가능하다고 보장하지 않음 |

YouTube 공식 API의 `subscriptions.list`에는 인증된 내 구독 목록을 읽는 `mine=true` 경로가 있다. 이는 **별도 OAuth·API·페이지 순회**가 필요한 확장이고, yt-dlp의 기본 구독 목록 명령이 아니다.

`mySubscribers`·`myRecentSubscribers`도 인증된 본인 계정 대상이며 반환 제한이 있다. 비공개 구독 등 때문에 임의 채널의 전체 구독자 목록을 만들 수 있다고 가정하지 않는다. 수업에서는 사용자가 지정한 공개 채널 ID를 직접 watchlist로 등록하는 방식을 권장한다. 구독 버튼을 누르는 쓰기 동작은 하지 않는다.

## 5.6 자막만 선택적으로 저장

자막은 기본 수집 범위 밖이다. 목적·저작권·보관·모델 전송 여부를 승인한 뒤, 필요한 영상에만 추가한다.

```bash
# 현재 위치가 승인된 개인 실행 폴더인지 확인한 뒤 사용
# 같은 실행 폴더를 재사용하지 않는다.
yt-dlp --ignore-config --js-runtimes node \
  --no-playlist --skip-download \
  --write-subs --write-auto-subs \
  --sub-langs 'ko,en' --sub-format vtt \
  -o 'subtitles/%(id)s.%(ext)s' \
  'https://www.youtube.com/watch?v=VIDEO_ID'
```

이 명령에는 `-j`/`-J`를 섞지 않는다. dump 옵션의 시뮬레이션으로 자막 파일 쓰기가 생략될 수 있기 때문이다.

확인할 것:

1. 실제로 한국어/영어 자막이 제공되는가? 없으면 다른 언어가 있다고 추정하지 않는다.
2. VTT 파일이 생성되었고 실제 cue(시각과 텍스트)가 있는가? 헤더만 있으면 성공이 아니다.
3. 수동 자막인지 자동 생성 자막인지 기록했는가?
4. 언어·원본 영상 ID·수집 시각·해시가 연결되는가?
5. 반복 cue나 자동 자막 오류를 정제했다면 원본 자막과 정제본을 분리했는가?

자막이 없거나 접근이 막히면 각각 `subtitle_unavailable`, `blocked`처럼 이유를 남긴다. **영상/음성 다운로드, `agent-reach transcribe`, 외부 음성인식 모델 호출로 자동 전환하지 않는다.** upstream에 fallback 예시가 있어도 이 강의의 승인 범위를 넓혀 주지 않는다.

## 5.7 JSON과 중복 제거의 함정

- `-j`/`--dump-json`: 한 영상당 JSON 한 줄. 파일 전체를 단일 `json.load` 객체로 읽지 않는다.
- `-J`/`--dump-single-json`: 입력 URL당 JSON 한 줄. 검색·플레이리스트는 보통 `entries` 배열을 포함한다. 입력이 여러 개라면 출력도 여러 줄일 수 있다.
- 주요 필드 후보는 `id`, `title`, `webpage_url`, `channel_id`, `channel`, `upload_date`, `timestamp`, `description`이다. 모든 모드에서 모두 존재한다고 가정하지 않는다.
- 안전한 저장 필드만 추린다. 다운로드용 `formats`, 서명된 자막 URL, 세션 정보 등 필요 없는 값을 저장·공유하지 않는다.
- **metadata-only 수집에 `--download-archive`만 붙여 영구 중복 방지가 완성된다고 설명하지 않는다.** 시뮬레이션/skip-download의 archive 기록 동작은 다운로드와 다르다.
- `--force-write-archive`도 downstream 파일 저장 성공을 보장하지 않는다. `(youtube, video_id)`와 콘텐츠 저장 완료 상태를 [별도 장부](06-storage-and-incremental.md)로 관리한다.

## 5.8 성공 기준

CLI 종료 코드뿐 아니라 JSONL 각 행, 실제 ID, 승인된 channel ID, 시간 정밀도, 저장 파일을 검사한다. 원래 20개 후보가 있었는데 상세 조회는 일부만 성공했다면 나머지는 pending/partial로 남긴다.

`--ignore-errors`로 일부 실패를 건너뛰고 전체 성공처럼 보이게 만들지 않는다. 접근 제한·429·봇 확인은 중단 또는 허용된 제한적 재시도 사유다. 쿠키 자동 추출·차단 우회는 해결책으로 사용하지 않는다.

### 이해 확인

**Q. 영상 제목 20개를 저장했으면 영상 내용 20개를 읽었다고 말할 수 있는가?**

아니다. 저장한 것은 metadata다. 자막을 실제로 확보해 읽었는지, 영상 화면·음성을 검토했는지는 별도로 밝혀야 한다.

## 근거

- [Agent Reach YouTube 레시피 — 확인한 commit](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/skill/references/video.md)
- [yt-dlp 2026.08.19 README·옵션](https://github.com/yt-dlp/yt-dlp/blob/2026.08.19/README.md)
- [yt-dlp 날짜·archive 처리 구현](https://github.com/yt-dlp/yt-dlp/blob/2026.08.19/yt_dlp/YoutubeDL.py)
- [YouTube 채널 URL 이해](https://support.google.com/youtube/answer/6180214)
- [YouTube subscriptions.list](https://developers.google.com/youtube/v3/docs/subscriptions/list)
- [YouTube 공개/비공개 구독자 범위](https://support.google.com/youtube/answer/7280745)
