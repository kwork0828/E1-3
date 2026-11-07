"""라벨 정규화(표준화) 모듈.

data.json 은 같은 의미를 여러 표기로 담고 있다.
  - expected 값:  '+'  또는 'x'
  - filters 의 키: 'cross' 또는 'x'
프로그램 내부에서는 "표준 라벨" 2개(Cross, X)만 쓰도록 입구에서 한 번에 바꿔 준다.
그래야 비교(PASS/FAIL), 출력, 필터 선택이 모두 같은 문자열 기준으로 동작한다.
(정규화를 안 하면 '+' 와 'Cross' 를 서로 다른 값으로 취급해 정답인데도 FAIL 이 난다.)
"""

CROSS = "Cross"   # 표준 라벨 1: 십자가
X = "X"           # 표준 라벨 2: X 모양
UNDECIDED = "UNDECIDED"  # 판정 불가 (동점) - 라벨이 아니라 '판정 결과'용 값

# 소문자로 바꾼 뒤 이 표에서 찾는다. (대소문자/앞뒤 공백 차이를 흡수)
_ALIASES = {
    "+": CROSS,
    "cross": CROSS,
    "x": X,
}


def normalize_label(raw) -> str:
    """'+', 'cross', 'x' 등 입력 표기를 표준 라벨(Cross / X)로 바꾼다.

    알 수 없는 값이면 ValueError (호출한 쪽에서 케이스 단위 FAIL 로 처리한다).
    """
    if not isinstance(raw, str):
        raise ValueError("라벨은 문자열이어야 합니다: {!r}".format(raw))
    key = raw.strip().lower()
    if key in _ALIASES:
        return _ALIASES[key]
    raise ValueError("알 수 없는 라벨: {!r} (허용: '+', 'cross', 'x')".format(raw))
