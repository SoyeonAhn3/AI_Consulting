"""
guard_output.py — output/ 폴더 쓰기 전 세션 상태 검증 Hook
PreToolUse(Write) 에서 호출됨
차단 시 exit 2 + stderr 메시지 → LLM에게 에러 전달
"""

import json
import sys
import glob
import os
import re


def main():
    hook_input = json.loads(sys.stdin.read())
    file_path = hook_input.get("tool_input", {}).get("file_path", "")
    cwd = hook_input.get("cwd", "")

    # 절대경로를 상대경로로 변환 (cwd 기준)
    normalized = file_path.replace("\\", "/")
    cwd_normalized = cwd.replace("\\", "/").rstrip("/")
    if cwd_normalized and normalized.startswith(cwd_normalized):
        normalized = normalized[len(cwd_normalized):].lstrip("/")

    # output/ 폴더 대상이 아니면 무조건 통과
    if not normalized.startswith("output/") and "/output/" not in normalized:
        sys.exit(0)

    # cwd 기준으로 세션 파일 찾기
    session_dir = os.path.join(cwd, "logs", "session") if cwd else "logs/session"
    pattern = os.path.join(session_dir, "session_*.json")
    sessions = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)

    if not sessions:
        print("세션 파일이 없습니다. STEP 1(parse-requirement)부터 진행하세요.", file=sys.stderr)
        sys.exit(2)

    with open(sessions[0], "r", encoding="utf-8") as f:
        session = json.load(f)

    # 검사 1: scope_gate
    scope_gate = session.get("scope_gate", "")
    if scope_gate == "rejected":
        print("scope_gate=rejected 상태입니다. 이 요구사항은 MS 업무자동화 범위 밖이므로 산출물을 생성할 수 없습니다.", file=sys.stderr)
        sys.exit(2)

    # 검사 2: 스텝 순서 (context_snapshot.last_step이 있는 경우만)
    snapshot = session.get("context_snapshot") or {}
    last_step = snapshot.get("last_step", "")
    if last_step:
        match = re.search(r"STEP\s+(\d+)", last_step)
        if match:
            step_num = int(match.group(1))
            if step_num < 7:
                print(f"현재 {last_step} 단계입니다. STEP 7(generate-output) 이전에는 산출물을 생성할 수 없습니다.", file=sys.stderr)
                sys.exit(2)

    # 검사 3: 필수 필드 누락
    missing = []
    if not session.get("output_mode"):
        missing.append("output_mode")
    if not session.get("output_language"):
        missing.append("output_language")

    if missing:
        fields = ", ".join(missing)
        print(f"필수 필드가 설정되지 않았습니다: {fields}. STEP 6(사용자 최종 확인)을 먼저 완료하세요.", file=sys.stderr)
        sys.exit(2)

    # 모든 검사 통과
    sys.exit(0)


if __name__ == "__main__":
    main()
