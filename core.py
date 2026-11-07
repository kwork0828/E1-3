"""핵심 연산 모듈: MAC 연산, 허용오차(epsilon) 비교, 판정.

외부 라이브러리(NumPy 등) 없이 반복문만으로 구현한다.
"""
from labels import CROSS, UNDECIDED, X

# 부동소수점 오차 때문에 '같은 값'이 미세하게 달라질 수 있어 == 로 비교하지 않고,
# 두 값의 차이가 이 값보다 작으면 같은 값(동점)으로 간주한다.
EPSILON = 1e-9


def mac(pattern, filt) -> float:
    """MAC(Multiply-Accumulate): 같은 위치끼리 곱(Multiply)하고 모두 더한다(Accumulate).

    pattern, filt 는 n×n 2차원 리스트. 곱셈 n² 번, 덧셈 n² 번 → 연산 횟수는 n².
    """
    n = len(pattern)
    if len(filt) != n:
        raise ValueError("크기 불일치: 패턴은 {0}x{0}, 필터는 {1}x{1} 입니다.".format(n, len(filt)))
    total = 0.0
    for i in range(n):
        if len(pattern[i]) != n or len(filt[i]) != n:
            raise ValueError("행/열 개수 불일치: {0}번째 행의 길이가 {1}이(가) 아닙니다.".format(i, n))
        for j in range(n):
            total += pattern[i][j] * filt[i][j]   # 곱하고(Multiply) 누적(Accumulate)
    return total


def is_tie(score_a: float, score_b: float, epsilon: float = EPSILON) -> bool:
    """두 점수가 허용오차 안에서 같은지(동점) 판단한다."""
    return abs(score_a - score_b) < epsilon


def judge(score_cross: float, score_x: float, epsilon: float = EPSILON) -> str:
    """Cross 점수와 X 점수를 비교해 Cross / X / UNDECIDED 를 돌려준다."""
    if is_tie(score_cross, score_x, epsilon):
        return UNDECIDED
    return CROSS if score_cross > score_x else X


def judge_ab(score_a: float, score_b: float, epsilon: float = EPSILON) -> str:
    """사용자 입력 모드용: 필터 A / B 중 어느 쪽에 더 가까운지 A / B / 판정 불가 로 돌려준다."""
    if is_tie(score_a, score_b, epsilon):
        return "판정 불가"
    return "A" if score_a > score_b else "B"


# ----------------------------------------------------------------------
# 보너스: 2차원 → 1차원(길이 N²) 변환으로 메모리 접근 패턴 단순화
# ----------------------------------------------------------------------
def flatten(grid):
    """n×n 2차원 리스트를 길이 n² 의 1차원 리스트로 펼친다 (행 우선)."""
    return [value for row in grid for value in row]


def mac_flat(flat_pattern, flat_filter) -> float:
    """1차원으로 펼친 패턴/필터의 MAC. 이중 반복문 + pattern[i][j] 두 번 인덱싱 대신 단일 반복문 + 한 번 인덱싱.

    결과는 mac() 과 같고(합산 순서도 행 우선으로 동일), 연산 횟수도 N² 로 같다. 바뀌는 것은 접근 방식뿐이다.
    """
    size = len(flat_pattern)
    if len(flat_filter) != size:
        raise ValueError("길이 불일치: 패턴 {} 와 필터 {}".format(size, len(flat_filter)))
    total = 0.0
    for k in range(size):
        total += flat_pattern[k] * flat_filter[k]
    return total
