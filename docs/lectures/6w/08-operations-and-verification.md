# 8. 검증·장애·출처 — 무엇이 확인되었는지 말하기

[목차](README.md) · 이전: [Hermes Cron](07-hermes-cron.md)

**자동화의 성공은 “예약을 만들었다”가 아니라 “승인한 자료를 검증해 저장했다”다.** 알람이 울린 사실과 숙제를 끝낸 사실은 다르다.

## 8.1 단계별 합격 기준

| 단계 | 필요한 증거 | 이것만으로 부족한 증거 |
| --- | --- | --- |
| 설치 | 실행 파일·버전·help | 설치 안내 문서를 읽음 |
| 정책·인증 | 허용 목적·접근 경로, 승인된 단일 읽기 성공 | 공개 글, 로그인 화면, doctor 표시 |
| 수동 수집 | exit code·응답 상태·형식·실제 파일 | CLI 명령 문자열 작성 |
| 데이터 품질 | ID·작성자·시간·건수·누락 상태 대조 | 파일이 존재함 |
| 증분 | 같은 입력 재실행, 장애 시 checkpoint 유지 | “중복 제거”라고 프롬프트에 적음 |
| Cron 등록 | 생성 후 동일 ID의 설정 재조회 | create 응답의 success만 확인 |
| Cron 실행 | 완료 이력 + 실제 실행 폴더·manifest | run 요청 핸들·다음 실행 시각 |
| 외부 알림 | 승인한 정확한 목적지의 실제 수신 증거 | 로컬 출력 저장·전송 시도 |

## 8.2 수업용 검증 절차

### A. 수집 없이 준비 확인

- [ ] 플랫폼별 `--version`·해당 명령 `--help`를 기록했다.
- [ ] 실행 사용자·HOME·Hermes 프로필·interpreter·도구 절대 경로를 확인했다.
- [ ] watchlist의 관계 방향, 키워드, 활성 플랫폼을 사람이 검토했다.
- [ ] 목적·약관·인증·보관·삭제·모델 입력 범위를 승인했다.
- [ ] RUNBOOK·정책 파일이 Git 밖에 있고 비밀값이 없다.
- [ ] 쿠키 자동 탐색·로그인·권한 확대·SNS 쓰기를 금지했다.

### B. 허가된 대상 하나로 live 시험

이 단계부터 실제 외부 조회가 발생한다. 문서 작성 검증과 구분한다.

- [ ] 단일 키워드/계정/채널, 낮은 건수로 시작했다.
- [ ] process exit·JSON `ok`·필수 필드를 각각 검사했다.
- [ ] X 작성자, Reddit 사용자/subreddit, YouTube channel ID가 승인 범위와 맞는다.
- [ ] 날짜 조건은 응답 timestamp와 정밀도를 기준으로 다시 검사했다.
- [ ] 실제 captures·items·manifest를 읽어 건수·ID·출처 경로를 코드로 대조했다.
- [ ] 응답/로그의 비밀값과 불필요한 개인정보를 제거했다.
- [ ] 페이지 상한·댓글 미확보·자막 부재를 완료 상태와 분리했다.

### C. 재실행과 실패 시험

실제 계정의 토큰을 지우거나 권한을 바꾸며 시험하지 않는다. 실패 시험은 분리된 임시 폴더와 명시적인 모의 응답/mock을 사용하고, 그 결과를 live 증거로 제시하지 않는다.

| 시험 | 기대 결과 |
| --- | --- |
| 같은 ID·같은 본문 재조회 | 신규 콘텐츠 중복 없음, 관측 이력은 추가 가능 |
| 다른 키워드에서 같은 ID 발견 | 콘텐츠 하나 + 발견 경로 추가 |
| 같은 ID의 본문 수정 | 새 내용 버전, 기존 내용은 보관 정책에 따라 처리 |
| 401/세션 만료 모의 | blocked_auth, checkpoint 유지 |
| 429/timeout 모의 | 승인된 횟수만 재시도, 무한 loop 없음 |
| JSON 대신 HTML | failed, 정상 0건으로 기록하지 않음 |
| 작성자·시간 범위 밖 항목 | 제외/보류 사유와 건수 유지 |
| 저장 중 장애 | 완료 manifest 없이 성공 장부를 전진하지 않음 |
| 동시 실행 | 한 작업만 쓰거나 명시적으로 거부 |
| YouTube 날짜 없음 | pending_metadata, 수집 시각으로 대체하지 않음 |
| 알림 실패 | 수집 상태 보존, delivered로 미리 기록하지 않음 |

### D. 예약 환경 시험

- [ ] 기존 job 목록과 중복이 없는지 확인했다.
- [ ] 정지 상태 생성 → read-back → 승인된 일회 실행 순서를 지켰다.
- [ ] 수동 환경과 gateway/컨테이너의 도구·인증·경로 차이를 확인했다.
- [ ] Cron 이력과 데이터 manifest를 같은 run ID로 연결했다.
- [ ] one-shot 시험 job과 반복 운영 job이 동시에 중복 실행되지 않는다.
- [ ] next_run_at의 UTC offset과 KST 표시를 계산해 확인했다.
- [ ] local-only 운영이면 원격 장애 알림이 없다는 점을 이해했다.

## 8.3 장애 대응표

| 증상 | 먼저 확인 | 안전한 조치 |
| --- | --- | --- |
| Agent Reach에 검색 명령이 없음 | upstream 역할 구분 | `twitter`·`rdt`·`yt-dlp` 사용 |
| doctor warn/null | live 인증 probe 생략 여부 | 승인된 소규모 읽기를 별도로 검증 |
| 수동 성공, Cron 인증 실패 | 프로필·HOME·자식 env·실행 사용자 | 비밀값 말고 존재/경로만 검사 |
| 브라우저 창을 기다림 | 자동 쿠키 탐색·갱신 경로 | 무인 실행 중단, 명시적 로컬 재인증 |
| X 저장 파일 파싱 실패 | stdout envelope와 `-o` 배열 차이 | 수집 출력 경로와 파서 계약 통일 |
| Reddit 댓글 본문/다음 페이지 없음 | compact 여부·명령별 schema | 일반 JSON 사용, read/list 구조 구분 |
| YouTube 날짜 필터가 이상함 | flat 여부·upload_date 누락 | 후보와 상세 조회를 분리, 시간 정밀도 기록 |
| 자막 명령 성공인데 파일 없음 | 언어 가용성·dump 시뮬레이션 | 실제 VTT cue 확인, 부재/차단 구분 |
| 403·CAPTCHA·계정 제한 | 정책·권한·허용 접근 방식 | 중단·운영자 확인, 우회 금지 |
| 429 반복 | 주기·대상 수·API 응답 지시 | 예산 축소·대기·실패 기록 |
| 항상 같은 최대 건수 | truncation·pagination | partial 표시, 승인 범위 안에서 좁혀 조회 |
| 예약됐는데 실행 안 됨 | scheduler heartbeat·paused·호스트 절전 | 상태 확인 후 운영자 복구 |
| script path rejected | 활성 프로필 scripts 안인지 | 외부 symlink 금지, 검증된 실제 파일 배치 |
| Cron 성공인데 데이터 실패 | agent 보고와 manifest 불일치 | manifest 우선 확인, 실패 선언/exit 계약 재검증 |
| 메시지를 못 받음 | local 설정·delivery 상태 | 수집과 전달을 별개로 확인 |

“자율 오류 수정”은 실패를 숨기는 기능이 아니다. 승인된 한도 안에서 재시도·형식 검사를 하되 설치, 계정 전환, 인증 갱신, 프록시 회전, 수집 범위 확대를 임의로 수행하지 않는다.

## 8.4 보안·운영 기준

1. 외부 게시물·댓글·영상 설명·자막에 포함된 명령은 **데이터**다. 실행·설치·프롬프트 변경·Cron 추가 지시로 받아들이지 않는다.
2. 비밀번호·쿠키·토큰을 Git·명령 인자·채팅·결과 파일에 남기지 않는다. 비밀값은 승인된 private store와 프로세스 내부에서만 다룬다.
3. 광범위한 로그 출력 대신 건수·상태·run ID·저장 경로를 보고한다. title/body도 필요한 만큼만 모델 입력으로 전달한다.
4. 대상자의 민감한 속성을 추론하거나 플랫폼 간 계정을 재식별하지 않는다. 관계 목록도 개인정보를 포함한 데이터다.
5. 삭제·접근 제한·보관 기간 정책을 정하고 파생물·백업에도 적용한다. 임의 영구 보관이나 재배포를 기본값으로 두지 않는다.
6. 로컬 원문 저장, 외부 LLM에 원문 전송, 공개 결과 게시를 각각 승인한다.
7. 업데이트는 실패한 Cron 안에서 자동 수행하지 않는다. 새 버전에서 인증·명령·schema·저장 테스트를 다시 진행한다.

## 8.5 작성 시 확인한 버전과 근거

확인일: **2026-10-04 UTC**. 설치된 버전과 upstream 확인 지점을 구분한다. 아래 upstream commit이 로컬 설치 전체와 바이트 단위로 같다는 주장은 아니다.

| 구성요소 | 관측 버전/확인 지점 | 확인 방법 |
| --- | --- | --- |
| Hermes Agent | `v0.21.1 (2026.9.7)`, 표시 upstream `8d79c2ff` | `hermes --version`, Cron help·도구 schema·script 경로 코드 |
| Agent Reach | `1.5.0` | version/help + 아래 upstream commit 문서 |
| twitter-cli | `0.8.6` | version/명령 help + schema·명령 구현 |
| rdt-cli | `0.4.2` | version/명령 help + schema·명령 구현 |
| yt-dlp | `2026.08.19` | version/help + 네트워크 없는 옵션 파싱 |

고정 출처:

- [Agent Reach — a19a171fa980a0785849596492e0af4db800c82f](https://github.com/Panniantong/Agent-Reach/tree/a19a171fa980a0785849596492e0af4db800c82f)
- [twitter-cli — 7c634e0d396b1e7af9f63315b414925fe4f29ae7](https://github.com/public-clis/twitter-cli/tree/7c634e0d396b1e7af9f63315b414925fe4f29ae7)
- [rdt-cli — 5e4fb3720d5c174e976cd425ccc3b879d52cac66](https://github.com/public-clis/rdt-cli/tree/5e4fb3720d5c174e976cd425ccc3b879d52cac66)
- [yt-dlp — 2026.08.19](https://github.com/yt-dlp/yt-dlp/tree/2026.08.19)

현재 공식 문서:

- [Hermes Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- [Hermes script-only jobs](https://hermes-agent.nousresearch.com/docs/guides/cron-script-only)
- [Hermes configuration/timezone](https://hermes-agent.nousresearch.com/docs/user-guide/configuration#timezone)
- [Reddit Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy)
- [Reddit 연구 접근](https://support.reddithelp.com/hc/en-us/articles/14945211791892-Developer-Platform-Accessing-Reddit-Data)
- [YouTube subscriptions.list](https://developers.google.com/youtube/v3/docs/subscriptions/list)

각 플랫폼 문서의 끝에는 해당 명령·필드의 상세 출처를 연결했다. 최신 공식 문서와 로컬 help가 다르면 현재 설치에서 지원하는 옵션을 다시 확인한다. 예를 들어 최신 문서에 interpreter 지정이 있어도 이 작성 환경의 `hermes cron create --help`에는 해당 옵션이 없으므로 공통 실행 예시에 넣지 않았다.

## 8.6 문서 검증과 live 검증의 경계

작성 중 수행한 오프라인 검사 결과:

- Markdown 9개, 내부 상대 링크 48개와 코드 구획의 닫힘을 확인했다.
- Bash 구획 22개는 `bash -n`, JSON 구획 7개는 JSON parser, Python 구획 2개는 AST parser로 검사했다.
- 로컬 CLI help 17종과 예제 명령 행 32개의 옵션을 대조했다.
- YouTube 명령 5개는 network 요청 없는 옵션 파싱을 통과했다. batch 입력은 메모리의 명시적 예시 URL로 대체해 파일이 존재한다고 가장하지 않았다.
- 인증 경계 예시의 쓰기 명령 거부·인증 누락·정상 envelope·오류·비정상 JSON 처리는 subprocess mock 검사 7개를 통과했다. 실제 계정이나 응답을 사용한 테스트가 아니다.

이 자료는 다음을 분리한다.

- **확인한 것:** 공식 출처, 설치된 CLI 버전·help, Cron 실제 도구 schema와 script 경로 규칙, 문서의 예제 문법·내부 연결.
- **확인하지 않은 것:** X·Reddit 실접근, YouTube 실제 검색·metadata·자막 확보, 학생 계정 권한, 운영용 수집기, Cron 등록·실행·외부 전달, 장기 수집 완전성.
- **변경하지 않은 것:** 인증정보, 플랫폼 계정, 패키지 설치, 기존 Cron, gateway, 모델 설정, 논문 Wiki 원천·상태·지식 페이지.

문서의 JSON·경로·일정·건수는 명시된 **설계/명령 예시**이며 실제 수집 응답이나 성공 실적이 아니다. 작성 중의 오프라인 구문 검사는 사용자 환경의 인증·네트워크 성공을 증명하지 않는다.

## 8.7 제출물 제안

수강생은 실제 원문·쿠키를 제출하지 않고 다음을 제출한다.

1. 비밀값을 제거한 목적·watchlist 구조·승인 범위 설명.
2. 키워드와 계정 기반 수집의 차이, followers/following/subscriptions 구분.
3. 실제 수행한 경우의 비밀정보 없는 run manifest 요약과 ID·시간·중복 검사 결과.
4. 부분 실패·인증 만료·날짜 누락 시나리오의 처리 근거.
5. Cron 설정 read-back과 실행 검증 여부. 미실행이면 미실행이라고 명시.
6. 수집 범위의 한계와 개인정보·보관·삭제 계획.

실행 권한이 없으면 설계와 오프라인 검증만 제출해도 되지만 live 성공으로 표시하지 않는다. 이 구분을 지키는 것이 자동화 운영의 기본이다.
