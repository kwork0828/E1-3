"""정규화/epsilon 정책이 왜 필요한지 보여 주는 비교 실험.

같은 data.json 을 세 가지 정책으로 판정해 PASS/FAIL 수를 비교한다.
  A) 정책 없음 : expected 를 정규화하지 않고('+' 그대로), 점수는 '>' 로만 비교 (동점이면 X)
  B) 정규화만  : 라벨은 정규화, 점수는 '>' 로만 비교 (epsilon 없음)
  C) 최종      : 라벨 정규화 + epsilon 동점 처리 (이 프로젝트의 정책)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core import judge, mac  # noqa: E402
from labels import CROSS, X, normalize_label  # noqa: E402
from loader import case_sort_key, load_filters, read_json  # noqa: E402


def naive(score_cross, score_x):
    return CROSS if score_cross > score_x else X


def main():
    data = read_json(os.path.join(ROOT, "data.json"))
    filters, _ = load_filters(data["filters"])
    policies = {"A) 정책 없음": [], "B) 정규화만": [], "C) 정규화+epsilon": []}
    for key in sorted(data["patterns"], key=case_sort_key):
        n = int(key.split("_")[1])
        entry = data["patterns"][key]
        sc, sx = mac(entry["input"], filters[n][CROSS]), mac(entry["input"], filters[n][X])
        raw = entry["expected"]
        policies["A) 정책 없음"].append((key, naive(sc, sx) == raw))
        policies["B) 정규화만"].append((key, naive(sc, sx) == normalize_label(raw)))
        policies["C) 정규화+epsilon"].append((key, judge(sc, sx) == normalize_label(raw)))
    print("{:<20}{:>6}{:>6}{:>6}   FAIL 케이스".format("정책", "총", "통과", "실패"))
    print("-" * 70)
    for name, results in policies.items():
        failed = [k for k, ok in results if not ok]
        print("{:<20}{:>6}{:>6}{:>6}   {}".format(name, len(results), len(results) - len(failed), len(failed),
                                                  ", ".join(failed) if len(failed) <= 4 else "{}건 전부 (표기 '+'/'x' ≠ 표준 'Cross'/'X')".format(len(failed))))
    print("\n해석: A는 expected('+','x')와 판정('Cross','X')의 표기가 문자열로 달라 판정이 맞아도 14건 전부 FAIL. "
          "B는 FAIL 0건이지만 동점 2건(size_5_5, size_13_5)을 우연히 한쪽으로 찍어 맞춘 '가짜 통과'. "
          "C만 동점을 UNDECIDED 로 드러낸다.")


if __name__ == "__main__":
    main()
