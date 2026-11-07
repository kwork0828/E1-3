"""표준 라이브러리 unittest 로 핵심 규칙을 검증한다.   실행:  python -m unittest -v"""
import io
import os
import sys
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import modes  # noqa: E402
from core import EPSILON, flatten, is_tie, judge, judge_ab, mac, mac_flat  # noqa: E402
from labels import CROSS, UNDECIDED, X, normalize_label  # noqa: E402
from loader import (CaseError, DataError, check_matrix, load_filters, parse_row,  # noqa: E402
                    prepare_case, read_json)
from patterns import add_noise, generate_cross, generate_x  # noqa: E402

DATA = os.path.join(ROOT, "data.json")
INVALID = os.path.join(ROOT, "tests", "fixtures", "data_invalid.json")


class LabelTest(unittest.TestCase):
    def test_expected_and_filter_keys_are_normalized(self):
        self.assertEqual(normalize_label("+"), CROSS)
        self.assertEqual(normalize_label("cross"), CROSS)
        self.assertEqual(normalize_label(" Cross "), CROSS)
        self.assertEqual(normalize_label("x"), X)
        self.assertEqual(normalize_label("X"), X)

    def test_unknown_label_raises(self):
        for bad in ("o", "", None, 1):
            with self.assertRaises(ValueError):
                normalize_label(bad)


class MacTest(unittest.TestCase):
    def test_spec_example_scores(self):
        cross, x = generate_cross(3), generate_x(3)
        self.assertEqual(mac(cross, cross), 5.0)   # 과제 설명의 Case 1
        self.assertEqual(mac(cross, x), 1.0)       # 과제 설명의 Case 2

    def test_score_is_float(self):
        self.assertIsInstance(mac([[1]], [[1]]), float)

    def test_size_mismatch_raises(self):
        with self.assertRaises(ValueError):
            mac([[1, 2], [3, 4]], generate_cross(3))

    def test_flat_version_matches_2d(self):
        for n in (3, 5, 13, 25):
            p, f = add_noise(generate_cross(n), 3), generate_x(n)
            self.assertEqual(mac(p, f), mac_flat(flatten(p), flatten(f)))


class EpsilonTest(unittest.TestCase):
    def test_float_noise_is_a_tie(self):
        a, b = 0.1 + 0.2, 0.3
        self.assertNotEqual(a, b)                  # == 로 비교하면 서로 다르다고 나온다
        self.assertTrue(is_tie(a, b))
        self.assertEqual(judge(a, b), UNDECIDED)

    def test_clear_difference_is_decided(self):
        self.assertEqual(judge(5.0, 1.0), CROSS)
        self.assertEqual(judge(1.0, 5.0), X)
        self.assertEqual(judge_ab(1.0, 5.0), "B")
        self.assertEqual(judge_ab(5.0, 1.0), "A")

    def test_difference_just_above_epsilon_is_decided(self):
        self.assertEqual(judge(1.0 + 2 * EPSILON, 1.0), CROSS)


class InputParseTest(unittest.TestCase):
    def test_valid_row_with_extra_spaces(self):
        self.assertEqual(parse_row("  0   1 0 ", 3), [0.0, 1.0, 0.0])

    def test_invalid_rows(self):
        for bad in ("0 1", "0 1 0 1", "a b c", "", "nan 1 0", "inf 1 0"):
            with self.assertRaises(ValueError, msg=bad):
                parse_row(bad, 3)


class LoaderTest(unittest.TestCase):
    def test_data_json_loads_all_filters(self):
        filters, report = load_filters(read_json(DATA)["filters"])
        self.assertEqual(sorted(filters), [5, 13, 25])
        self.assertTrue(all(ok for _, ok, _ in report))

    def test_prepare_case_extracts_n_and_normalizes_expected(self):
        filters, _ = load_filters(read_json(DATA)["filters"])
        entry = {"input": generate_x(5), "expected": "x"}
        n, _, expected = prepare_case("size_5_2", entry, filters)
        self.assertEqual((n, expected), (5, X))

    def test_size_mismatch_is_case_error(self):
        filters, _ = load_filters(read_json(DATA)["filters"])
        with self.assertRaises(CaseError):
            prepare_case("size_5_9", {"input": generate_cross(3), "expected": "+"}, filters)

    def test_check_matrix_rejects_bad_shapes(self):
        for bad in ([], [[1, 2], [3]], [[1, "a"], [2, 3]], [[True, 0], [0, 1]], "abc"):
            with self.assertRaises(ValueError):
                check_matrix(bad)

    def test_missing_and_broken_files_raise_data_error(self):
        with self.assertRaises(DataError):
            read_json(os.path.join(ROOT, "no_such_file.json"))


def run_mode2(path):
    buf = io.StringIO()
    with redirect_stdout(buf):
        modes.run_json_mode(path)
    return buf.getvalue()


class Mode2IntegrationTest(unittest.TestCase):
    def test_data_json_summary(self):
        out = run_mode2(DATA)
        self.assertIn("총 테스트: 14개", out)
        self.assertIn("통과: 12개", out)
        self.assertIn("실패: 2개", out)
        self.assertIn("size_5_5", out)    # 부동소수점 동점 사례
        self.assertIn("size_13_5", out)   # 정확한 동점 사례

    def test_invalid_data_does_not_crash_and_each_case_fails(self):
        out = run_mode2(INVALID)
        self.assertIn("총 테스트: 9개", out)
        self.assertIn("통과: 1개", out)
        self.assertIn("실패: 8개", out)

    def test_missing_file_is_reported_not_raised(self):
        self.assertIn("파일을 찾을 수 없습니다", run_mode2("nope.json"))


if __name__ == "__main__":
    unittest.main()
