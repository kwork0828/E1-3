"""docs/README.template.md 의 {{...}} 자리에 실제 실행 결과 파일의 값을 채워 README.md 를 만든다.

성능 수치/요약/ablation 은 docs/demo, docs/logs 의 '실제 출력'에서 가져오므로 문서와 결과가 어긋나지 않는다.
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return re.sub(r"\n{3,}", "\n\n", f.read()).strip("\n")


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout.strip()


def main():
    tpl = read("docs", "README.template.md")
    mode2 = read("docs", "demo", "mode2.txt")

    perf_block = re.search(r"크기\s+평균 시간\(ms\).*?\n-+\n((?:\d+×\d+.*\n?)+)", mode2 + "\n")
    rows = re.findall(r"^(\d+)×\d+\s+([\d.]+)\s+(\d+)\s*$", perf_block.group(1), flags=re.M)
    data = {int(n): (float(ms), int(ops)) for n, ms, ops in rows}
    perf_text = "크기           평균 시간(ms)     연산 횟수(N²)\n" + "-" * 38 + "\n" + "\n".join(
        "{:<8}{:>14.4f}{:>14}".format("{0}×{0}".format(n), data[n][0], data[n][1]) for n in sorted(data))

    derived = ["| 크기 | 평균 시간(ms) | 연산 횟수(N²) | 연산 1번당 시간(ns) |", "|---|---|---|---|"]
    ns = {}
    for n in sorted(data):
        ms, ops = data[n]
        ns[n] = ms * 1e6 / ops
        derived.append("| {0}×{0} | {1:.4f} | {2} | {3:.1f} |".format(n, ms, ops, ns[n]))

    t3, t13, t25 = data[3][0], data[13][0], data[25][0]
    values = {
        "PYVER": sh("python3 --version").replace("Python ", ""),
        "OS": sh(". /etc/os-release; echo $PRETTY_NAME") + " 컨테이너",
        "TESTS": re.search(r"Ran (\d+) tests", read("docs", "logs", "unittest.log")).group(1),
        "COMMITS": str(int(sh("git rev-list --count HEAD")) + 1),   # + 이 README 를 올리는 커밋
        "BRANCHES": str(len([b for b in sh("git branch --list").splitlines() if b.strip()])),
        "SUMMARY": mode2[mode2.index("총 테스트"):],
        "ABLATION": read("docs", "logs", "ablation.log").split("\n\n")[0],
        "PERF": perf_text,
        "PERF_DERIVED": "\n".join(derived),
        "OPT": read("docs", "demo", "mode4.txt").split("\n\n※")[0].split("-" * 39 + "\n", 1)[1],
        "OPS_3_25": "{:.1f}".format(625 / 9),
        "TIME_3_25": "{:.1f}".format(t25 / t3),
        "OPS_13_25": "{:.2f}".format(625 / 169),
        "TIME_13_25": "{:.2f}".format(t25 / t13),
        "LIN_13_25": "{:.2f}".format(25 / 13),
        "CUB_13_25": "{:.2f}".format((25 / 13) ** 3),
        "NS_3": "{:.0f}".format(ns[3]),
        "NS_25": "{:.0f}".format(ns[25]),
    }
    for key, value in values.items():
        tpl = tpl.replace("{{" + key + "}}", value)
    left = re.findall(r"\{\{[A-Z_0-9]+\}\}", tpl)
    assert not left, "채워지지 않은 자리표시자: {}".format(left)
    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write(tpl + "\n")
    print("README.md written;", len(tpl.splitlines()), "lines")


if __name__ == "__main__":
    main()
