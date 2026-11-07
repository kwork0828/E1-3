"""실행 모드 구현: 모드 1(사용자 입력 3×3), 모드 2(data.json 일괄 분석)."""
import perf
from core import EPSILON, judge, judge_ab, mac
from labels import CROSS, UNDECIDED, X
from loader import (CaseError, DataError, case_sort_key, load_filters, parse_row,
                    prepare_case, read_json)

SIZE = 3


class QuitProgram(Exception):
    """Ctrl+C / 입력 종료(EOF) 시 비정상 종료 대신 안내 후 끝내기 위한 예외."""


def section(title: str) -> None:
    print()
    print("#" + "-" * 39)
    print("# " + title)
    print("#" + "-" * 39)


def fmt(value) -> str:
    """5.0 → '5', 0.9 → '0.9' (행렬을 읽기 쉽게 출력)."""
    return str(int(value)) if float(value).is_integer() else repr(value)


def read_line() -> str:
    try:
        return input()
    except (EOFError, KeyboardInterrupt):
        print("\n입력이 중단되었습니다. 프로그램을 안전하게 종료합니다.")
        raise QuitProgram


def read_matrix(name: str, n: int = SIZE):
    """n줄을 한 줄씩 입력받는다. 형식 오류면 안내 문구를 보여 주고 '그 줄'만 다시 입력받는다."""
    print("{} ({}줄 입력, 공백 구분)".format(name, n))
    rows = []
    while len(rows) < n:
        try:
            rows.append(parse_row(read_line(), n))
        except ValueError as error:
            print(error)
    return rows


def show_matrix(name: str, grid) -> None:
    print(name)
    for row in grid:
        print(" ".join(fmt(v) for v in row))


def run_user_mode() -> None:
    """모드 1: 필터 A,B 입력 → 저장 확인 → 패턴 입력 → MAC 연산 → 결과 판정 → 성능 분석(3×3)."""
    section("[1] 필터 입력")
    filter_a = read_matrix("필터 A")
    print()
    filter_b = read_matrix("필터 B")

    section("[1-2] 저장 확인")
    show_matrix("필터 A", filter_a)
    show_matrix("필터 B", filter_b)

    section("[2] 패턴 입력")
    pattern = read_matrix("패턴")

    section("[3] MAC 결과")
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    avg_ms = perf.measure_ms(lambda: (mac(pattern, filter_a), mac(pattern, filter_b)))
    print("A 점수: {}".format(score_a))
    print("B 점수: {}".format(score_b))
    print("연산 시간(평균/{}회): {:.3f} ms".format(perf.REPEAT, avg_ms))
    verdict = judge_ab(score_a, score_b)
    print("판정: {}".format(verdict if verdict != "판정 불가" else "판정 불가 (|A-B| < 1e-9)"))

    section("[4] 성능 분석 (3×3, 평균/{}회)".format(perf.REPEAT))
    print(perf.format_table(perf.benchmark(sizes=(3,))))


# ----------------------------------------------------------------------
# 모드 2: data.json 일괄 분석
# ----------------------------------------------------------------------
CAT_SCHEMA = "데이터/스키마"
CAT_NUMERIC = "수치 비교"
CAT_LOGIC = "로직(판정≠expected)"


def analyze_case(key: str, entry, filters: dict) -> dict:
    """케이스 하나를 판정하고 결과 dict 를 돌려준다. 어떤 오류가 나도 예외를 밖으로 던지지 않는다(→ FAIL)."""
    try:
        n, grid, expected = prepare_case(key, entry, filters)
        score_cross = mac(grid, filters[n][CROSS])
        score_x = mac(grid, filters[n][X])
        verdict = judge(score_cross, score_x)
        print("Cross 점수: {}".format(score_cross))
        print("X 점수: {}".format(score_x))
        if verdict == expected:
            print("판정: {} | expected: {} | PASS".format(verdict, expected))
            return {"key": key, "passed": True}
        if verdict == UNDECIDED:
            reason = "동점(UNDECIDED) 처리 규칙에 따라 FAIL (|Cross-X| < {:g})".format(EPSILON)
            category = CAT_NUMERIC
        else:
            reason = "판정 {} ≠ expected {}".format(verdict, expected)
            category = CAT_LOGIC
        print("판정: {} | expected: {} | FAIL ({})".format(verdict, expected, "동점 규칙" if category == CAT_NUMERIC else reason))
        return {"key": key, "passed": False, "category": category, "reason": reason}
    except CaseError as error:
        print("판정: FAIL | 사유: {}".format(error))
        return {"key": key, "passed": False, "category": CAT_SCHEMA, "reason": str(error)}
    except Exception as error:  # noqa: BLE001  (비정상 종료 방지: 예상 못 한 오류도 케이스 FAIL 로 기록)
        print("판정: FAIL | 사유: 예상치 못한 오류 {}: {}".format(type(error).__name__, error))
        return {"key": key, "passed": False, "category": CAT_LOGIC,
                "reason": "예상치 못한 오류 {}: {}".format(type(error).__name__, error)}


def run_json_mode(path: str) -> None:
    """모드 2: 필터 로드 → 패턴 로드/검증 → MAC/판정/PASS-FAIL → 성능 분석 → 결과 요약."""
    section("[1] 필터 로드")
    try:
        data = read_json(path)
    except DataError as error:
        print("⚠️ data.json 오류: {}".format(error))
        return
    filters, report = load_filters(data["filters"])
    for key, ok, message in report:
        print("{} {} {}".format("✓" if ok else "✗", key, message))

    section("[2] 패턴 분석 (라벨 정규화 적용)")
    results = []
    for key in sorted(data["patterns"], key=case_sort_key):
        print("--- {} ---".format(key))
        results.append(analyze_case(key, data["patterns"][key], filters))

    section("[3] 성능 분석 (평균/{}회)".format(perf.REPEAT))
    print(perf.format_table(perf.benchmark()))

    section("[4] 결과 요약")
    failed = [r for r in results if not r["passed"]]
    print("총 테스트: {}개".format(len(results)))
    print("통과: {}개".format(len(results) - len(failed)))
    print("실패: {}개".format(len(failed)))
    if failed:
        print("\n실패 케이스:")
        for r in failed:
            print("- {}: [{}] {}".format(r["key"], r["category"], r["reason"]))
    else:
        print("\n실패 0개: 라벨이 모두 표준 라벨(Cross/X)로 정규화되어 비교되고, 점수 비교에 허용오차(epsilon={:g}) "
              "정책이 적용되었기 때문입니다.".format(EPSILON))
