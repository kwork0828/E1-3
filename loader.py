"""입력 파싱과 검증 모듈 (콘솔 입력 / data.json 공통)."""
import math

ROW_ERROR = "입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요."


def parse_row(line: str, n: int):
    """공백으로 구분된 한 줄을 n개의 float 리스트로 바꾼다. 형식이 틀리면 ValueError.

    검증: (1) 열 개수 == n  (2) 모두 숫자로 변환 가능  (3) NaN/inf 아님
    """
    parts = line.split()
    if len(parts) != n:
        raise ValueError(ROW_ERROR.format(n=n))
    values = []
    for part in parts:
        try:
            value = float(part)
        except ValueError:
            raise ValueError(ROW_ERROR.format(n=n))
        if not math.isfinite(value):
            raise ValueError(ROW_ERROR.format(n=n))
        values.append(value)
    return values
