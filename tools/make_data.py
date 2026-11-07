"""data.json 과 테스트용 잘못된 데이터(tests/fixtures/data_invalid.json)를 만든다.

과제 PDF 에는 data.json 파일이 포함돼 있지 않고 '구조 설명'만 있다. 그래서 그 구조를 그대로 따르는 데이터를
생성기(patterns.py)로 만든다. (시드를 고정해 몇 번을 실행해도 같은 파일이 나온다)

data.json 구조
{
  "filters":  { "size_5": {"cross": [[...]], "x": [[...]]}, "size_13": {...}, "size_25": {...} },
  "patterns": { "size_5_1": {"input": [[...]], "expected": "+"}, ... }      # expected: '+' 또는 'x'
}
"""
import json
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from patterns import add_noise, generate_cross, generate_x  # noqa: E402

SIZES = (5, 13, 25)


def dump(obj) -> str:
    """JSON 문자열. 숫자 한 행은 한 줄에 모아 사람이 읽기 좋게 만든다."""
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    return re.sub(r"\[\s+(-?[\d.]+(?:,\s+-?[\d.]+)*)\s+\]",
                  lambda m: "[" + re.sub(r"\s+", " ", m.group(1)) + "]", text) + "\n"


def build_valid() -> dict:
    rng = random.Random(2026)
    filters = {}
    patterns = {}
    for n in SIZES:
        filters["size_{}".format(n)] = {"cross": generate_cross(n), "x": generate_x(n)}
        cross, x = generate_cross(n), generate_x(n)
        patterns["size_{}_1".format(n)] = {"input": cross, "expected": "+"}                      # 깨끗한 십자가
        patterns["size_{}_2".format(n)] = {"input": x, "expected": "x"}                          # 깨끗한 X
        patterns["size_{}_3".format(n)] = {"input": add_noise(cross, 2, rng), "expected": "+"}   # 노이즈 2칸 십자가
        patterns["size_{}_4".format(n)] = {"input": add_noise(x, 2, rng), "expected": "x"}       # 노이즈 2칸 X

    # 경계 사례 1) 부동소수점 오차: 십자가 전용 칸 0.1 + 0.2, X 전용 칸 0.3
    #   Cross 점수 = 0.1 + 0.2 = 0.30000000000000004, X 점수 = 0.3  → 실제로는 같은 값(동점)
    noise = [[0.0] * 5 for _ in range(5)]
    noise[2][0], noise[2][1], noise[0][0] = 0.1, 0.2, 0.3
    patterns["size_5_5"] = {"input": noise, "expected": "+"}
    # 경계 사례 2) 모두 1인 패턴: Cross 필터와 X 필터의 1 개수가 25개로 같아 정확히 동점
    patterns["size_13_5"] = {"input": [[1] * 13 for _ in range(13)], "expected": "x"}
    return {"filters": filters, "patterns": patterns}


def build_invalid() -> dict:
    """스키마/데이터 오류를 일부러 모은 파일. 프로그램이 중단되지 않고 케이스 단위로 FAIL 처리하는지 확인용."""
    c5, x5 = generate_cross(5), generate_x(5)
    return {
        "filters": {
            "size_5": {"cross": c5, "x": x5},
            "size_7": {"cross": generate_cross(7)},          # x 필터 누락
            "size_x": {"cross": c5, "x": x5},                # 필터 키 형식 오류
        },
        "patterns": {
            "size_5_1": {"input": c5, "expected": "+"},                     # 정상(PASS)
            "size_5_2": {"input": [[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]], "expected": "x"},  # 4x4 → 크기 불일치
            "size_7_1": {"input": generate_cross(7), "expected": "+"},      # size_7 필터 로드 실패
            "size_9_1": {"input": generate_cross(9), "expected": "+"},      # size_9 필터 없음
            "size_5_3": {"input": c5, "expected": "o"},                     # 알 수 없는 라벨
            "size_5_4": {"input": [[1, 0, 1, 0, "a"]] + c5[1:], "expected": "x"},   # 숫자가 아닌 값
            "size_5_5": {"input": [[1, 0, 1, 0, 1]] * 4, "expected": "x"},  # 정사각형 아님(4행 5열)
            "pattern_1": {"input": c5, "expected": "+"},                    # 키 형식 오류
            "size_5_6": {"expected": "+"},                                  # input 누락
        },
    }


def main() -> None:
    with open(os.path.join(ROOT, "data.json"), "w", encoding="utf-8") as f:
        f.write(dump(build_valid()))
    with open(os.path.join(ROOT, "tests", "fixtures", "data_invalid.json"), "w", encoding="utf-8") as f:
        f.write(dump(build_invalid()))
    print("written: data.json, tests/fixtures/data_invalid.json")


if __name__ == "__main__":
    main()
