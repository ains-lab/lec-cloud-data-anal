# 2. 설치·인증·실행 환경 — 도구와 출입증은 별개다

[목차](README.md) · 이전: [구조와 범위](01-overview-and-scope.md) · 다음: [X](03-x-collection.md)

**도구가 설치되었다고 사이트에 들어갈 수 있는 것은 아니다.** 열쇠가 있는지, 그 열쇠를 예약 작업도 사용할 수 있는지 따로 확인해야 한다.

> 이 문서의 설치·인증·조회 예시는 이후 사용자가 승인해 수행할 절차다. 작성 중에는 version/help와 공개 소스만 확인했으며 설치·인증·doctor·실제 SNS 조회를 실행하지 않았다.

## 2.1 설치 전 확인

```bash
command -v python3
command -v pipx
command -v uv
command -v agent-reach
command -v twitter
command -v rdt
command -v yt-dlp

agent-reach --version
agent-reach --help
agent-reach install --help
twitter --version
rdt --version
yt-dlp --version
```

없는 명령에서 오류가 나면 해당 도구의 설치 여부부터 해결한다. Python 시스템 환경을 강제로 변경하거나 `sudo pip`, `--break-system-packages`를 사용하지 않는다. upstream 설치 안내는 Python 3.10 이상과 격리된 pipx/uv 환경을 전제로 확인한다.

## 2.2 Agent Reach 설치와 backend 준비

아래는 공식 설치 안내의 pipx 경로다. **pipx가 이미 준비되었고 설치를 승인한 경우**에만 실행한다. `main.zip`은 계속 변하므로 재현 가능한 수업 운영에서는 검토한 tag/commit URL로 고정하고 사용한 버전을 기록한다.

```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
```

설치 후 변경 예정 범위를 먼저 확인한다.

```bash
agent-reach install --env=auto --channels=twitter,reddit --dry-run
```

Agent Reach 1.5.0의 일반 `install`은 기본적으로 check-only다. 실제 설치·설정 변경을 승인할 때 사용하는 옵션은 `--system`이다.

```bash
# 의존성·도구·config·skill 변경 범위를 확인하고 승인한 뒤에만 실행
agent-reach install --env=auto --system --channels=twitter,reddit
```

- `--system`은 단순 진단 옵션이 아니다. 시스템 의존성·전역 도구·설정·스킬 설치를 허용한다.
- `--channels`에는 선택 채널 목록을 넣는다. 확인한 help의 선택 채널 목록에 `youtube`는 없으며 YouTube용 yt-dlp/JS runtime은 공통 준비 항목과 설치 결과를 별도로 확인한다. 없는 `--channels=youtube` 예시를 만들지 않는다.
- 특정 채널만 골라도 공통 인프라 변경이 포함될 수 있다. 변경 예정 목록을 검토한다.
- 이미 운영 중인 환경은 자동 업데이트하지 않는다. 업데이트 후 CLI 옵션·응답 스키마·인증 경계를 다시 검증한다.

설치 위치는 한 가지로 고정되지 않는다. 작성 환경은 uv 도구별 가상환경을 사용했지만 pipx 환경의 경로는 다르다. `command -v`와 launcher를 보고 실제 interpreter를 확인한다. Hermes 가상환경에 backend 패키지가 모두 있다고 가정하지 않는다.

## 2.3 플랫폼별 인증

| 플랫폼 | 기본 backend | 무엇이 필요한가? | Cron에서 주의할 점 |
| --- | --- | --- | --- |
| X | `twitter` | 승인된 로그인 세션의 Cookie | Agent Reach 저장값을 twitter가 자동으로 읽지 않음 |
| Reddit | `rdt` | 현재 지원 경로에서는 인증 세션과 이용 목적에 맞는 허가 | 인증이 없거나 오래되면 브라우저 추출을 시도할 수 있음 |
| YouTube | `yt-dlp` | 공개 metadata는 무쿠키 시도 가능; 실행 가능한 JS runtime 등 | 무인증 성공을 보장하지 않음. 제한 영상·봇 차단·자막 부재 구분 |
| 선택 대안 | OpenCLI | 실제 브라우저·확장 연결·승인된 세션 | 바이너리만 설치된 서버는 연결된 브라우저가 아님 |

### X의 명시적 로컬 인증

```bash
# 사용자 로컬 터미널의 숨김 입력으로 설정; 비밀값을 인자로 붙이지 않는다
agent-reach configure twitter-cookies
```

쿠키는 비밀번호와 비슷하게 세션 권한을 가진다. 채팅, 강의 파일, Git, 명령 인자, 스크린샷에 붙이지 않는다. 에이전트가 브라우저 로그인을 보조할 때에는 지원되는 보안 입력 경로를 사용하고 비밀번호·인증 코드를 채팅으로 받지 않는다.

`twitter` 실행에는 `TWITTER_AUTH_TOKEN`, `TWITTER_CT0`가 **해당 자식 프로세스 환경에** 필요할 수 있다. Agent Reach의 `Config(read_only=True)`와 `twitter_cli_child_env(config)`는 승인된 저장값을 프로세스 내부에서 전달하는 경로다. 설정 파일을 출력하거나 모델에게 값을 읽어 주는 경로가 아니다.

### Reddit의 초기 인증

`rdt login`은 무해한 상태 조회가 아니라 **브라우저 쿠키 추출을 수행하는 인증 명령**이다. 실제 수집 목적과 접근 허가를 검토한 후, 사용자가 명시적으로 승인한 로컬 초기 설정에서만 수행한다. 예약 작업 안에서 실행하지 않는다.

저장된 세션이 만료되면 `blocked_auth`로 멈춘다. CLI의 로컬 갱신 주기와 플랫폼 서버의 쿠키 유효기간은 다르므로 특정 일수 동안 반드시 작동한다고 보장하지 않는다.

## 2.4 자동 쿠키 탐색을 막는 무인 실행 경계

일반 `twitter search`나 `rdt search`도 인증이 없거나 갱신이 필요하면 브라우저 접근을 시도할 수 있다. **읽기 명령이라는 사실만으로 비대화형·무브라우저 실행이 보장되지 않는다.**

본 강의의 플랫폼별 Bash 예시는 CLI 기능과 옵션을 설명한다. 승인된 수동 환경에서만 직접 실행하고, Cron에서는 다음 경계를 적용한 호출을 사용한다.

1. 현재 사용자의 승인된 저장소/secret 공급 방식만 사용한다.
2. X는 두 인증 환경변수가 없으면 CLI를 시작하기 전에 실패한다.
3. X와 Reddit의 브라우저 쿠키 추출·자동 갱신 함수를 자식 프로세스 안에서 차단한다.
4. 실행 경로·옵션을 allowlist로 제한하고 요청 시간·출력 크기를 제한한다.
5. 인증 오류는 비밀값 없는 코드로만 보고한다. stderr·환경·응답 envelope 전체를 그대로 출력하지 않는다.
6. 명령·응답 schema가 바뀌면 무인 실행을 보류하고 경계를 재검토한다.

다음은 확인한 CLI 버전에 대한 **호출 경계 예시**다. 완성된 수집기·재시도기·저장기는 아니며 이 문서 작성 중 설치하거나 실행하지 않았다. 실제 경로는 RUNBOOK에 기록한 interpreter로 바꾼다.

```python
import json
import os
import subprocess

X_BOOTSTRAP = """
import twitter_cli.auth as auth
if not hasattr(auth, 'extract_from_browser'):
    raise SystemExit('Unsupported authentication interface')
auth.extract_from_browser = lambda: (None, ['Browser extraction disabled'])
from twitter_cli.cli import cli
cli()
"""

REDDIT_BOOTSTRAP = """
import rdt_cli.auth as auth
if not hasattr(auth, 'extract_browser_credential'):
    raise SystemExit('Unsupported authentication interface')
auth.extract_browser_credential = lambda: None
from rdt_cli.cli import cli
cli()
"""


def guarded_read(python_path, platform, args, x_credentials=None):
    allowed = {
        'x': {'search', 'user', 'user-posts', 'tweet', 'followers', 'following'},
        'reddit': {'search', 'sub', 'user-posts', 'user-comments', 'read'},
    }
    if platform not in allowed or not args or args[0] not in allowed[platform]:
        raise ValueError('Read command not approved')
    # argv 형태로 전달하고 shell=True를 사용하지 않는다.
    env = {k: os.environ[k] for k in ('HOME', 'PATH', 'LANG', 'LC_ALL') if k in os.environ}
    if platform == 'x':
        for key in ('TWITTER_AUTH_TOKEN', 'TWITTER_CT0'):
            value = (x_credentials or {}).get(key)
            if not value:
                raise RuntimeError('blocked_auth')
            env[key] = value
    bootstrap = X_BOOTSTRAP if platform == 'x' else REDDIT_BOOTSTRAP
    result = subprocess.run(
        [python_path, '-c', bootstrap, *args, '--json'],
        env=env, capture_output=True, text=True, timeout=90,
    )
    # stderr에는 세션 관련 값이 있을 수 있으므로 오류 메시지에 복사하지 않는다.
    if result.returncode != 0:
        raise RuntimeError('backend_failed: inspect redacted local diagnostics')
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError('invalid_json') from None
    if payload.get('ok') is not True:
        raise RuntimeError('backend_not_ok')
    return payload  # 허용 콘텐츠만 추출한다. 전체를 로그/모델 문맥에 출력하지 않는다.
```

- X의 `x_credentials` 인자는 승인된 launcher 내부에서만 `twitter_cli_child_env(Config(read_only=True))`로 공급한다. 이를 만드는 launcher는 Agent Reach 패키지가 있는 interpreter에서 실행해야 한다. 자격증명 딕셔너리는 출력·파일 복제하지 않는다.
- 예시는 프로세스 내부 함수 교체이므로 upstream 파일을 수정하지 않는다. 내부 API에 의존하므로 영구 호환성을 보장하지 않는다.
- Reddit은 승인된 사용자의 기존 인증 저장소를 backend가 읽는다. 브라우저 갱신이 차단되어 실패하면 사람이 재인증한다.
- 이 최소 예시는 호출 경계 설명이다. 운영 버전에는 옵션·경로 allowlist, 제한된 stdout 수집, timeout 분류, 원자 저장, 잠금, 상태 테스트가 더 필요하다. TLS·프록시·XDG 경로 등 환경 전달도 실제 배포에 맞춰 필요한 값만 검토한다.
- payload를 정상 파싱한 뒤의 필드 검사는 [X](03-x-collection.md)·[Reddit](04-reddit-collection.md)·[저장 계약](06-storage-and-incremental.md)을 따른다.

## 2.5 doctor는 무엇을 증명할까?

사용자가 진단 실행을 승인했다면:

```bash
agent-reach doctor --json
```

Agent Reach 1.5.0은 X·Reddit의 의도하지 않은 브라우저 쿠키 접근을 피하려고 로그인 기반 live probe를 생략할 수 있다. 저장된 인증이 있어도 `warn`, `active_backend: null`이 가능하다. YouTube 진단도 실행 파일·JS runtime 점검이지 특정 영상 자막 접근 검증이 아니다.

| 관측 | 말할 수 있는 것 | 아직 말할 수 없는 것 |
| --- | --- | --- |
| version/help 성공 | 명령이 설치되어 실행됨 | 계정 접근 성공 |
| doctor 결과 | 설치·설정 진단 결과 | 목표 게시물·자막 확보 |
| 승인된 단일 조회 성공 | 그 시점 그 대상의 읽기 성공 | 지속적인 무인 수집 성공 |
| Cron 실행 + 저장 검사 성공 | 해당 예약 환경에서 처리 완료 | 전수 수집·영구 인증·알림 성공 |

## 2.6 수동에서 예약으로 옮기기 전

- 실행 사용자·HOME·활성 프로필·backend·절대 경로를 맞춘다.
- 실제 데이터를 저장할 위치는 강의 저장소 밖이다.
- 파일 권한, 로그 노출, 보관 기간을 검토한다.
- 인증·정책 실패가 나면 조회를 멈추고 성공 checkpoint를 유지한다.
- Cron이 비대화형이므로 로그인창·2FA·인증 갱신 질문을 기다리게 만들지 않는다.
- 계정 제한·CAPTCHA·403을 프록시 회전·다중 계정으로 우회하지 않는다.

## 근거

- [Agent Reach 설치 안내 — 확인한 commit](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/docs/install.md)
- [Agent Reach X 채널·인증 전달 코드](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/channels/twitter.py)
- [Agent Reach Reddit 채널](https://github.com/Panniantong/Agent-Reach/blob/a19a171fa980a0785849596492e0af4db800c82f/agent_reach/channels/reddit.py)
- [twitter-cli 인증 코드](https://github.com/public-clis/twitter-cli/blob/7c634e0d396b1e7af9f63315b414925fe4f29ae7/twitter_cli/auth.py)
- [rdt-cli 인증 코드](https://github.com/public-clis/rdt-cli/blob/5e4fb3720d5c174e976cd425ccc3b879d52cac66/rdt_cli/auth.py)
