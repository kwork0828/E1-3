"""입력 파싱과 검증 모듈 (콘솔 입력 / data.json 공통)."""
import json
import math
import re

from labels import CROSS, X, normalize_label

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


# ======================================================================
# data.json 로드 / 스키마 검증 (모드 2)
# ======================================================================
FILTER_KEY = re.compile(r"^size_(\d+)$")            # 필터 키: size_5, size_13, size_25
PATTERN_KEY = re.compile(r"^size_(\d+)_(\d+)$")     # 패턴 키: size_{N}_{idx}


class DataError(Exception):
    """data.json 자체를 못 읽는 치명적 문제 (파일 없음, JSON 문법 오류, 최상위 구조 오류)."""


class CaseError(ValueError):
    """케이스(패턴) 하나가 잘못된 경우. 프로그램을 멈추지 않고 그 케이스만 FAIL 로 처리한다."""


def read_json(path: str) -> dict:
    """data.json 을 읽고 최상위 구조(filters, patterns)를 확인한다."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise DataError("파일을 찾을 수 없습니다: {}".format(path))
    except json.JSONDecodeError as error:
        raise DataError("JSON 문법 오류: {} (줄 {}, 칸 {})".format(error.msg, error.lineno, error.colno))
    except OSError as error:
        raise DataError("파일을 읽을 수 없습니다: {}".format(error))
    if not isinstance(data, dict) or not isinstance(data.get("filters"), dict) \
            or not isinstance(data.get("patterns"), dict):
        raise DataError("최상위 구조 오류: 'filters'와 'patterns' 객체가 모두 있어야 합니다.")
    return data


def check_matrix(grid, n=None) -> int:
    """grid 가 숫자로 이루어진 정사각형 2차원 배열인지 검증하고 크기를 돌려준다. n 이 주어지면 크기도 일치해야 한다."""
    if not isinstance(grid, list) or not grid or not all(isinstance(row, list) for row in grid):
        raise ValueError("2차원 배열이 아닙니다.")
    size = len(grid)
    for i, row in enumerate(grid):
        if len(row) != size:
            raise ValueError("정사각형이 아닙니다: 행 {}의 열 개수 {} ≠ 행 개수 {}".format(i, len(row), size))
        for j, value in enumerate(row):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("숫자가 아닌 값이 있습니다: [{}][{}] = {!r}".format(i, j, value))
    if n is not None and size != n:
        raise ValueError("크기 불일치: 기대 {0}x{0}, 실제 {1}x{1}".format(n, size))
    return size


def load_filters(raw_filters: dict):
    """filters 를 읽어 {N: {CROSS: 2차원배열, X: 2차원배열}} 로 만든다. (라벨 정규화 적용)

    반환: (filters, report)  report = [(키, 성공여부, 메시지), ...]  → 한 필터가 틀려도 나머지는 계속 처리.
    """
    filters = {}
    report = []
    for key, entry in raw_filters.items():
        match = FILTER_KEY.match(key)
        if not match:
            report.append((key, False, "필터 키 형식 오류: size_N 형태여야 합니다."))
            continue
        n = int(match.group(1))
        try:
            if not isinstance(entry, dict):
                raise ValueError("필터는 {'cross': [[...]], 'x': [[...]]} 형태여야 합니다.")
            normalized = {}
            for raw_label, grid in entry.items():
                label = normalize_label(raw_label)       # 'cross' → Cross, 'x' → X
                check_matrix(grid, n)
                normalized[label] = grid
            if CROSS not in normalized or X not in normalized:
                raise ValueError("Cross 와 X 필터가 모두 필요합니다.")
        except ValueError as error:
            report.append((key, False, str(error)))
            continue
        filters[n] = normalized
        report.append((key, True, "필터 로드 완료 (Cross, X)"))
    return filters, report


def case_sort_key(key: str):
    """size_5_2 < size_5_10 < size_13_1 처럼 숫자 기준으로 정렬. 형식이 틀린 키는 맨 뒤."""
    match = PATTERN_KEY.match(key)
    return (0, int(match.group(1)), int(match.group(2)), key) if match else (1, 0, 0, key)


def prepare_case(key: str, entry, filters: dict):
    """패턴 케이스 하나를 검증해 (N, 입력 배열, 표준 expected 라벨)을 돌려준다. 문제가 있으면 CaseError."""
    match = PATTERN_KEY.match(key)
    if not match:
        raise CaseError("패턴 키 형식 오류: size_{N}_{idx} 형태여야 합니다.")
    n = int(match.group(1))                              # 키에서 N 을 추출 → size_N 필터 선택에 사용
    if not isinstance(entry, dict) or "input" not in entry or "expected" not in entry:
        raise CaseError("패턴 항목에는 'input'과 'expected'가 필요합니다.")
    if n not in filters:
        raise CaseError("size_{} 필터가 없거나 로드에 실패했습니다.".format(n))
    try:
        check_matrix(entry["input"], n)                  # 필터와 패턴의 크기가 일치하는지 검증
        expected = normalize_label(entry["expected"])    # '+' → Cross, 'x' → X
    except ValueError as error:
        raise CaseError(str(error))
    return n, entry["input"], expected
