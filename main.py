"""Mini NPU 시뮬레이터 - 진입점.

사용법:
    python main.py                 # 모드를 메뉴에서 선택
    python main.py --mode 2        # 메뉴 없이 바로 모드 실행 (재현/자동 실행용)
    python main.py --mode 2 --data other.json
    python main.py --mode 4 --repeat 200   # 보너스: 최적화 전/후 비교 (반복 횟수 지정)
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
    print("3. (보너스) 패턴 생성기")
    print("4. (보너스) 최적화 전/후 비교")
    while True:
        raw = modes.read_line().strip()
        if raw in ("1", "2", "3", "4"):
            return int(raw)
        print("⚠️ 잘못된 입력입니다. 1~4 중에서 입력하세요.")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Mini NPU 시뮬레이터")
    parser.add_argument("--mode", type=int, choices=[1, 2, 3, 4],
                        help="1: 사용자 입력(3x3), 2: data.json 분석, 3: 패턴 생성기(보너스), 4: 최적화 비교(보너스)")
    parser.add_argument("--data", default=DEFAULT_DATA, help="data.json 경로 (기본: 프로젝트 루트)")
    parser.add_argument("--repeat", type=int, default=10, help="모드 4 반복 측정 횟수 (기본 10)")
    args = parser.parse_args(argv)
    if args.repeat < 1:
        parser.error("--repeat 는 1 이상이어야 합니다.")
    try:
        mode = args.mode or choose_mode()
        if mode == 1:
            modes.run_user_mode()
        elif mode == 2:
            modes.run_json_mode(args.data)
        elif mode == 3:
            modes.run_generator_mode()
        else:
            modes.run_optimize_mode(args.repeat)
    except modes.QuitProgram:
        pass


if __name__ == "__main__":
    main()
