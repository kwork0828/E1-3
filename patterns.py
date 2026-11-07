"""패턴 생성기 (보너스): N×N 십자가(Cross)와 X 패턴을 자동으로 만든다.

모드 3(패턴 생성기)와 성능 분석(크기별 패턴/필터)에서 재사용한다.
"""
import random

from labels import CROSS, X, normalize_label


def generate_cross(n: int):
    """가운데 행과 가운데 열이 1인 십자가(+) 패턴."""
    _check_size(n)
    mid = n // 2
    return [[1 if (i == mid or j == mid) else 0 for j in range(n)] for i in range(n)]


def generate_x(n: int):
    """두 대각선이 1인 X 패턴."""
    _check_size(n)
    return [[1 if (i == j or i + j == n - 1) else 0 for j in range(n)] for i in range(n)]


def generate(label, n: int):
    """라벨('+', 'cross', 'x' 등)에 맞는 n×n 패턴을 만든다."""
    std = normalize_label(label)
    return generate_cross(n) if std == CROSS else generate_x(n)


def add_noise(grid, flips: int, rng=None):
    """서로 다른 flips 개 칸의 값을 0↔1 로 뒤집은 복사본을 돌려준다. (원본은 바꾸지 않음)"""
    rng = rng or random.Random(0)
    n = len(grid)
    if not 0 <= flips <= n * n:
        raise ValueError("flips 는 0~{0} 사이여야 합니다.".format(n * n))
    noisy = [row[:] for row in grid]
    for pos in rng.sample(range(n * n), flips):
        i, j = divmod(pos, n)
        noisy[i][j] = 1 - noisy[i][j]
    return noisy


def _check_size(n: int) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or n < 3:
        raise ValueError("크기 N 은 3 이상의 정수여야 합니다.")


def show(grid) -> str:
    """콘솔 확인용 문자열 (1 = ■, 0 = □)."""
    return "\n".join(" ".join("■" if v else "□" for v in row) for row in grid)
