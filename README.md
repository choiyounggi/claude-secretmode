# claude-secretmode

**흔적을 남기지 않는** 일회용 Claude Code 세션 — macOS RAM 디스크 위에서 Claude Code를 실행해, 대화 기록·프롬프트 히스토리·파일 스냅샷이 디스크에 **애초에 쓰이지 않고** 종료 시 통째로 증발합니다.

평소 쓰던 `claude` 자리에 `claude-secretmode`(또는 `csm`)를 치면 끝. 인증·MCP·CLAUDE.md·플러그인은 그대로 쓰면서, 그 세션의 흔적만 남지 않습니다. 본래의 `~/.claude`는 단 한 글자도 건드리지 않습니다.

## 빠른 시작 (1분)

### 1. 사전 요구사항

- macOS (Apple Silicon / Intel)
- [Claude Code](https://github.com/anthropics/claude-code) 설치 + **로그인된 상태**
  - `npm install -g @anthropic-ai/claude-code` 후 `claude` 로 한 번 로그인
  - 인증은 macOS 키체인(`Claude Code-credentials`)에서 상속받습니다

### 2. 설치

```bash
# npm
npm install -g @younggichoi/claude-secretmode

# 또는 bun
bun add -g @younggichoi/claude-secretmode
```

### 3. 사용

```bash
# 평소 claude 대신 — 이 세션은 기록이 디스크에 안 남음
claude-secretmode

# 짧은 별칭
csm

# claude 에 넘기는 인자는 그대로 전달
claude-secretmode --model opus
```

종료하면(Ctrl-D, `/exit`, 또는 터미널 닫기) RAM 디스크가 detach되며 그 세션의 모든 흔적이 사라집니다.

## 동작 원리

```
claude-secretmode 실행
 └ RAM 디스크 생성 → CLAUDE_CONFIG_DIR 로 지정
    ├ 키체인 토큰 → <ramdisk>/.credentials.json (인증 상속)
    ├ .claude.json (과거 프로젝트 흔적 제거), settings.json (기록 훅 비활성)
    ├ CLAUDE.md·hooks·skills·plugins → 심링크 (코드·정책은 그대로 공유)
    └ transcript / history / snapshot → 전부 RAM 에만 기록
 └ claude 실행 (평소처럼 interactive)
[종료] → RAM 디스크 detach → 세션 흔적 증발. 본래 ~/.claude 는 무침해.
```

- **처음부터 디스크에 안 쌓입니다.** "종료 시 삭제(scrub)"가 아니라, 기록이 RAM 위에만 있다가 메모리째 사라지는 구조입니다.
- 종료/재부팅하면 흔적이 남지 않고, 비정상 종료(터미널 닫힘 등) 시 남은 RAM 디스크는 다음 실행 때 자동 정리됩니다.

## 주요 기능

### 1. 기록 격리

대화 transcript, 프롬프트 히스토리, 파일 스냅샷이 본래 `~/.claude` 가 아니라 RAM 디스크에만 쓰입니다.

### 2. 기록·관찰 훅 비활성

`claude-mem` 등 세션을 영구 DB로 캡처하는 플러그인/훅을 그 세션에 한해 끕니다. 보안·품질 가드 훅은 유지합니다.

### 3. 인증 상속

macOS 키체인의 로그인을 그대로 물려받아 별도 재로그인이 필요 없습니다. MCP OAuth(슬랙·Figma 등)도 함께 상속됩니다.

### 4. 동시 세션 토큰 동기화

평소 `claude` 세션을 동시에 띄워도 로그인이 풀리지 않도록, 키체인의 최신 토큰을 RAM 세션에 따라 동기화합니다.

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `CLAUDE_SECRETMODE_RAM_MB` | `1024` | RAM 디스크 크기(MB). 긴 세션·큰 작업이면 키우세요. |
| `CLAUDE_SECRETMODE_DROP_HOOKS` | (없음) | 추가로 끌 훅 스크립트 이름(콤마 구분). 예: `"my-logger.sh,audit.sh"` |

## 보안

- 키체인 토큰은 **RAM 디스크 위 파일**(`600`)로만 두고 화면에 출력하지 않으며, 디스크 플래터에 닿지 않습니다.
- RAM 디스크 마운트가 실제로 살아있는지 검증한 뒤에만 토큰을 씁니다(silent mount 실패 시 디스크 기록 방지).
- 세션이 **살아있는 동안**에는 그 기록이 RAM에 존재하므로, 같은 사용자 권한의 프로세스는 접근할 수 있습니다. 종료/재부팅 시 사라집니다.

## 한계

- **macOS 전용** — `hdiutil` RAM 디스크와 키체인(`security`)에 의존합니다. Linux/Windows는 미지원입니다.
- 키체인 기반으로 로그인된 Claude Code 를 전제합니다.

## 라이선스

MIT
