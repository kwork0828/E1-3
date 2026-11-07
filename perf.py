"""성능 분석 모듈: 크기별 MAC 연산 시간을 반복 측정해 평균(ms)을 구한다.

- 시간 측정은 '연산 함수 호출 구간'만 감싼다. (입력/출력/파일 읽기 시간은 제외)
- 같은 크기를 REPEAT 번 측정한 뒤 평균을 낸다. (한 번만 재면 OS/캐시 영향으로 값이 흔들림)
"""
import time

from core import flatten, mac, mac_flat
from labels import CROSS, X
from patterns import generate

REPEAT = 10
DEFAULT_SIZES = (3, 5, 13, 25)


def measure_ms(func, repeat: int = REPEAT) -> float:
    """func() 를 repeat 번 실행해 1회당 평균 시간을 ms 로 돌려준다."""
    total = 0.0
    for _ in range(repeat):
        start = time.perf_counter()
        func()
        total += time.perf_counter() - start
    return total / repeat * 1000.0


def benchmark(sizes=DEFAULT_SIZES, repeat: int = REPEAT, mac_fn=mac):
    """크기별로 (패턴=십자가, 필터=X) MAC 1회의 평균 시간과 연산 횟수(N²)를 측정한다."""
    rows = []
    for n in sizes:
        pattern = generate(CROSS, n)
        filt = generate(X, n)
        avg_ms = measure_ms(lambda: mac_fn(pattern, filt), repeat)
        rows.append({"n": n, "avg_ms": avg_ms, "ops": n * n})
    return rows


def format_table(rows) -> str:
    """크기(N×N) / 평균 시간(ms) / 연산 횟수(N²) 표 문자열."""
    lines = ["{:<8}{:>14}{:>14}".format("크기", "평균 시간(ms)", "연산 횟수(N²)"), "-" * 38]
    for r in rows:
        lines.append("{:<8}{:>14.4f}{:>14}".format("{0}×{0}".format(r["n"]), r["avg_ms"], r["ops"]))
    return "\n".join(lines)


def compare_flat(sizes=DEFAULT_SIZES, repeat: int = REPEAT):
    """최적화 전(2차원 이중 반복문) / 후(1차원 단일 반복문) 를 같은 입력, 같은 반복 횟수로 비교한다.

    1차원 변환(flatten) 비용은 측정에서 제외한다. (변환은 한 번만 하고 여러 번 연산에 재사용하는 상황을 가정)
    """
    rows = []
    for n in sizes:
        pattern, filt = generate(CROSS, n), generate(X, n)
        flat_p, flat_f = flatten(pattern), flatten(filt)
        ms_2d = measure_ms(lambda: mac(pattern, filt), repeat)
        ms_1d = measure_ms(lambda: mac_flat(flat_p, flat_f), repeat)
        rows.append({"n": n, "ms_2d": ms_2d, "ms_1d": ms_1d,
                     "speedup": ms_2d / ms_1d if ms_1d else float("inf"),
                     "same": mac(pattern, filt) == mac_flat(flat_p, flat_f)})
    return rows


def format_compare(rows) -> str:
    lines = ["{:<8}{:>12}{:>12}{:>10}{:>10}".format("크기", "2차원(ms)", "1차원(ms)", "배율", "결과동일"), "-" * 52]
    for r in rows:
        lines.append("{:<8}{:>12.4f}{:>12.4f}{:>9.2f}x{:>10}".format(
            "{0}×{0}".format(r["n"]), r["ms_2d"], r["ms_1d"], r["speedup"], "O" if r["same"] else "X"))
    return "\n".join(lines)
