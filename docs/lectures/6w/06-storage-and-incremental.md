# 6. 저장·중복 제거·증분 수집 — 다시 읽어도 장부는 정확하게

[목차](README.md) · 이전: [YouTube](05-youtube-collection.md) · 다음: [Cron](07-hermes-cron.md)

## 6.1 먼저 기억할 것

**매번 최신 글을 조회하는 것과 새 글만 저장하는 것은 다르다.** 이미 받은 편지를 다시 확인하더라도 편지 번호를 대조하면 새 편지와 중복 편지를 구분할 수 있다.

아래 파일 구조와 필드는 이 강의의 **권장 설계**다. Agent Reach가 자동으로 생성하지 않으며, 이 문서 작성으로 실제 데이터나 상태 파일을 만들지는 않았다.

```text
개인 비공개 SNS 작업 폴더/           # 강의 저장소 밖
  collection-policy.json            # 승인한 키워드·계정·예산
  RUNBOOK.md                         # 명령·인증·저장·실패 정책
  runs/<run-id>/
    manifest.json                    # 전체 실행의 대상·집계·상태
    captures/<target-id>.json         # 비밀정보 제거 후 콘텐츠 응답
    items.jsonl                      # 검증한 콘텐츠 레코드
    observations.jsonl               # 반응 수 등 이번 관측값
    errors.jsonl                     # 비밀정보를 제거한 오류 분류
  state/<target-id>.json              # 대상별 성공 경계·pending
  state/items.json                    # platform/type/id 중복 장부
  relationships/<snapshot-id>.json    # 별도 승인된 관계 후보 목록
```

`run-id`, `target-id`는 프로그램이 생성·검증한 안전한 식별자로 한다. 검색어·제목을 파일명에 그대로 넣지 않는다. 경로 이탈, 심볼릭 링크를 통한 외부 쓰기, 기존 실행 폴더 덮어쓰기를 거부한다.

`captures`는 비밀정보를 제거한 **콘텐츠 스냅샷**이지 무변경 HTTP 원본이 아니다. Reddit `modhash`, 인증 헤더, 쿠키, 세션 메타데이터, 일시적인 서명 URL 등 불필요한 필드는 저장하지 않는다. 실제 플랫폼 응답의 허용 필드를 정한 뒤 저장한다.

## 6.2 무엇을 기준으로 같은 자료라고 할까?

| 플랫폼 | 콘텐츠 식별 키 | 추가로 보존할 것 |
| --- | --- | --- |
| X | `(x, post, 게시물 ID 문자열)` | 실제 작성자 ID/handle, 원문 URL |
| Reddit 글 | `(reddit, post, t3_로 시작하는 fullname)` | subreddit, permalink, 작성자 |
| Reddit 댓글 | `(reddit, comment, t1_로 시작하는 fullname)` | parent ID, 원글 ID, permalink |
| YouTube | `(youtube, video, video ID)` | channel ID, 영상 URL, 영상 종류 |

숫자처럼 보이는 ID도 문자열로 저장한다. 제목·URL만으로 중복을 판단하면 수정·단축 링크·이름 변경 때문에 오류가 난다. 삭제된 작성자를 임의로 복원하거나 추정하지 않는다.

한 콘텐츠가 키워드 검색과 계정 조회에 모두 나오면 `matched_targets`에 두 경로를 연결한다. “검색 결과 합계”와 “고유 콘텐츠 수”는 별도로 집계한다.

## 6.3 최소 레코드 계약

| 필드 | 의미·검사 |
| --- | --- |
| `schema_version` | 이 강의의 레코드 형식 버전 |
| `platform`, `item_type`, `item_id` | 플랫폼·종류·실제 반환된 고유 ID |
| `author_id`, `author_handle`, `channel_id` | 플랫폼에 맞게 사용; 응답에 없으면 null |
| `source_url` | 원문 링크; 사용자정보·인증 쿼리가 섞인 URL 거부 |
| `title`, `text` | 실제 읽은 범위만; 영상 metadata만 수집했으면 자막 text를 만들지 않음 |
| `published_at`, `published_date` | 정확한 시각과 날짜 수준 정보를 혼동하지 않음 |
| `time_precision` | `second`, `day`, `unknown` 등 실제 정밀도 |
| `collected_at` | 이번 수집 UTC 시각, timezone offset 포함 |
| `matched_targets` | 어떤 검색·계정 목록으로 발견했는지 |
| `backend`, `backend_version` | 사용한 CLI와 버전 |
| `run_id`, `capture_path` | 실제 저장 스냅샷에 연결 |
| `content_hash` | 명시한 콘텐츠 필드만 정규화한 SHA-256 |
| `completeness` | 조회 한도·페이지 종료·누락 가능성 |

내용 버전과 관측값을 분리한다. 좋아요·조회 수는 시간이 지나며 바뀌므로 본문 해시에 넣지 않고 `observations`에 시각과 함께 기록한다. 본문 수정은 새 콘텐츠 버전으로 남기되, 개인정보·삭제 정책상 보관하면 안 되는 자료는 별도 승인된 절차로 제거한다.

## 6.4 시간 창과 checkpoint

**checkpoint**는 “여기까지 처리했다고 확인한 경계”, **overlap**은 검색 지연 때문에 일부 구간을 다시 읽는 것이다.

1. 실행 시작 시 `window_end`를 UTC로 한 번 고정한다.
2. 최초 실행은 승인한 lookback 범위까지만 조회한다.
3. 다음 실행은 **대상별** 마지막 성공 경계에서 overlap을 빼고 조회한다.
4. 반환된 항목의 작성자와 시각을 로컬에서 다시 검사한다.
5. 정확한 시각이 있으면 `window_start <= published_at < window_end`인 반열린 구간을 쓴다.
6. 검색어·대상·정책이 바뀌면 같은 checkpoint를 무비판적으로 재사용하지 않는다. 정책 버전 또는 fingerprint로 구분한다.

X 검색의 `since/until`, Reddit `-t day`, YouTube 날짜 필터는 이 검사의 대체물이 아니다. 날짜가 없으면 수집 시각으로 게시 시각을 채우지 않는다. YouTube `upload_date`만 있으면 일 단위로 표시하고 엄격한 시간 단위 결과와 분리한다. 추가 조회에도 날짜가 없으면 해당 항목은 `pending_metadata`로 남기고 유효 건수에 넣지 않는다.

오래 멈춘 작업은 “최근 하루만” 읽고 복구되었다고 하지 않는다. 마지막 성공 이후의 미확인 구간을 표시하고, 승인된 backfill(지난 구간 보충 수집) 예산 안에서 분할한다. 그 범위를 upstream이 제공하지 않으면 결측 구간을 남긴다.

## 6.5 중간에 실패하면 어디까지 저장할까?

| 상태 | 뜻 | checkpoint 처리 |
| --- | --- | --- |
| `ok` | 설정된 조회 계약 안에서 검증·저장 성공 | 조회 성공 경계 갱신 가능; 전수 확보 뜻은 아님 |
| `ok_empty` | 정상 응답·정상 파싱 후 유효 항목 없음 | 같은 조건으로 갱신 가능, 원인·필터 제외 수 기록 |
| `partial` | 상한 도달, 페이지 중단, 일부 상세 조회 실패 | 성공 항목은 보존, 미완료 구간·대상을 pending에 유지 |
| `blocked_auth` | 인증 누락·만료·권한 문제 | 전진하지 않음; 운영자 조치 필요 |
| `blocked_policy` | 허용 목적·권한 미확인 | 조회하지 않음, 경계 유지 |
| `failed` | 네트워크·형식·저장 오류 | 전진하지 않음 |
| `pending_metadata` | 시간·작성자 같은 필수 검증 정보 부족 | 해당 항목 보류, 성공 건수에서 제외 |

`ok`의 의미는 “제한된 관측 작업의 성공”이다. `completeness=unknown`을 함께 둘 수 있다. 상한에 닿았거나 다음 페이지가 있는데 처리하지 않았다면 `partial` 또는 `possibly_truncated`를 명시한다. 요청 건수보다 적다고 완전성을 확정하지 않는다.

전체 실행이 성공해도 개별 대상 실패를 지우지 않는다. X 성공·Reddit 인증 실패라면 두 상태가 그대로 남아야 한다. 인증 실패를 빈 배열로 바꾸는 것은 잘못된 성공 처리다.

## 6.6 안전한 저장 순서

다음은 구현·검토용 순서이며, 이 자료에 완성된 트랜잭션 엔진이 포함된 것은 아니다.

```text
같은 데이터 폴더의 실행 잠금 획득
→ 고유 run-id 생성, 대상·UTC 창·정책 버전 고정
→ 제한된 요청 수행
→ exit code + JSON 상태 + 필수 필드 검사
→ 허용 콘텐츠만 추출, 비밀정보 제거
→ 임시 실행 폴더에 스냅샷·레코드·manifest 작성
→ 파일 재읽기·건수·ID·해시·출처 연결 검사
→ 완료된 실행 폴더 게시
→ 대상별 checkpoint와 중복 장부를 원자적으로 갱신
→ 잠금 해제, 건수·실패·저장 위치 보고
```

파일은 같은 파일시스템의 임시 파일에 완전히 쓴 뒤 교체한다. 기존 성공 결과를 빈 실패 파일로 덮어쓰지 않는다. 여러 상태 파일의 원자성은 자동 보장되지 않으므로 커밋된 run manifest를 기준으로 장부를 복구할 수 있게 한다. 상태 갱신 전 장애가 나도 다음 실행에서 커밋된 ID를 다시 확인해 중복 저장을 피한다.

Cron의 중복 tick 방지는 동일 저장소를 쓰는 수동 실행·다른 job까지 완전히 직렬화하지 않는다. 파일 잠금 등 데이터 폴더 단위 보호가 필요하다. 프롬프트에 “동시에 실행하지 마”라고 적는 것만으로 운영급 잠금이 구현되지 않는다.

## 6.7 수집과 요약·알림을 분리하기

- 수집은 원문 콘텐츠와 조회 범위를 남기는 단계다.
- 요약은 실제 저장한 입력을 읽고 출처를 붙이는 별도 단계다.
- 알림은 메시지 시스템이 실제로 전달했는지 확인하는 또 다른 단계다.

수집 장부의 `seen`과 알림 장부의 `delivered`를 합치지 않는다. 저장 후 알림이 실패했으면 재수집 없이 재전송할 수 있어야 한다. 반대로 메시지 전송을 시도했다는 이유로 전달 완료로 기록해서는 안 된다.

`continuity`나 `context_from`으로 이전 Cron 출력을 받더라도, 이것이 고유 ID 장부·트랜잭션·앞 단계 완료 대기를 대신하지는 않는다.

### 이해 확인

**Q. 이전 실행이 20건을 저장했고 이번 실행도 같은 20건을 읽었다면 신규 콘텐츠는?**

ID와 내용 버전이 모두 같으면 신규 콘텐츠는 없다. 이번에 조회했다는 관측 이력만 추가된다. 실제 수는 파일의 고유 키를 코드로 집계해야 한다.

## 근거와 성격

- 상태·스키마·저장 순서: 이 강의의 설계 제안이며 Agent Reach의 내장 기능 주장 아님.
- [Hermes Cron의 실행 이력·중복 방지·context_from 경계](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- [yt-dlp 출력·archive 옵션](https://github.com/yt-dlp/yt-dlp#usage-and-options): metadata-only 조회의 영구 중복 장부로 가정하지 않는다.
