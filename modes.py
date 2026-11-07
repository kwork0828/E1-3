"""실행 모드 구현: 모드 1(사용자 입력 3×3)."""
import perf
from core import judge_ab, mac
from loader import parse_row

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
