"""Mini NPU 시뮬레이터 - 진입점.

사용법:
    python main.py                 # 모드를 메뉴에서 선택
    python main.py --mode 2        # 메뉴 없이 바로 모드 실행 (재현/자동 실행용)
    python main.py --mode 2 --data other.json
"""
import argparse
import os

import modes

DEFAULT_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def choose_mode() -> int:
    print("=== Mini NPU Simulator ===\n")
    print("[모드 선택]\n")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    while True:
        raw = modes.read_line().strip()
        if raw in ("1", "2"):
            return int(raw)
        print("⚠️ 잘못된 입력입니다. 1 또는 2를 입력하세요.")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Mini NPU 시뮬레이터")
    parser.add_argument("--mode", type=int, choices=[1, 2], help="1: 사용자 입력(3x3), 2: data.json 분석")
    parser.add_argument("--data", default=DEFAULT_DATA, help="data.json 경로 (기본: 프로젝트 루트)")
    args = parser.parse_args(argv)
    try:
        mode = args.mode or choose_mode()
        if mode == 1:
            modes.run_user_mode()
        else:
            print("모드 2는 아직 준비 중입니다.")
    except modes.QuitProgram:
        pass


if __name__ == "__main__":
    main()
