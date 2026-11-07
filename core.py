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
        raise ValueError("크기 불일치: 패턴 {0}x? 와 필터 {1}x? 의 크기가 다릅니다.".format(n, len(filt)))
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
