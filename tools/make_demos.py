"""실제 프로그램을 실행해 그 '실제 출력'을 docs/demo/*.txt 로 저장하고, 터미널 모양 PNG 로 렌더링한다.

input() 을 '입력값을 그대로 다시 출력'하는 래퍼로 감싸 사용자가 타이핑한 값이 화면에 보이게 한다. (프로그램 로직은 그대로)
성능 수치는 실행할 때마다 조금씩 달라진다. README 는 이 스크립트가 만든 파일의 값을 그대로 가져와 쓴다.
"""
import html
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WRAP = (
    "import builtins\n"
    "_real = builtins.input\n"
    "def _echo(prompt=''):\n"
    "    value = _real(prompt)\n"
    "    print(value)\n"
    "    return value\n"
    "builtins.input = _echo\n"
    "import main\n"
    "main.main({argv!r})\n"
)

SPEC_FILTERS = ["0 1 0", "1 1 1", "0 1 0", "1 0 1", "0 1 0", "1 0 1"]

SCENARIOS = [
    # (이름, 화면 제목, main 인자, 입력 줄들)
    ("mode1_normal", "모드 1: 사용자 입력 (3x3) - 과제 예시 입력", [],
     ["1"] + SPEC_FILTERS + ["1 0 1", "0 1 0", "1 0 1"]),
    ("mode1_invalid", "모드 1: 잘못된 입력(열 부족/문자/빈 입력) 후 재입력 + 부동소수점 동점(판정 불가)",
     ["--mode", "1"],
     ["0 1", "0 a 0", "", "0.1 0.2 0", "0 0 0", "0 0 0",     # 필터 A (잘못된 줄을 3번 입력한 뒤 재입력)
      "0.3 0 0", "0 0 0", "0 0 0",                           # 필터 B
      "1 1 0", "0 0 0", "0 0 0"]),                           # 패턴 → A=0.1+0.2, B=0.3
    ("mode2", "모드 2: data.json 분석", ["--mode", "2"], []),
    ("mode2_invalid", "모드 2: 잘못된 데이터(스키마/크기/라벨 오류)도 중단 없이 케이스 FAIL 처리",
     ["--mode", "2", "--data", "tests/fixtures/data_invalid.json"], []),
    ("mode2_missing", "모드 2: 파일 없음 / JSON 문법 오류", None, []),
    ("mode3", "보너스 모드 3: 패턴 생성기 (N=7)", [], ["3", "4", "abc", "7"]),
    ("mode4", "보너스 모드 4: 최적화(2차원→1차원) 전/후 비교 (반복 200회)", ["--mode", "4", "--repeat", "200"], []),
]


def run(argv, lines):
    code = WRAP.format(argv=argv)
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, input="\n".join(lines) + "\n",
                         capture_output=True, text=True, encoding="utf-8").stdout
    return out.strip("\n")


def run_missing():
    parts = []
    for label, argv in (("없는 파일", ["--mode", "2", "--data", "nope.json"]),):
        parts.append("$ python main.py --mode 2 --data nope.json\n" + run(argv, []))
    bad = os.path.join(ROOT, "tests", "fixtures", "broken.json")
    with open(bad, "w", encoding="utf-8") as f:
        f.write("{bad")
    parts.append("\n$ python main.py --mode 2 --data tests/fixtures/broken.json\n"
                 + run(["--mode", "2", "--data", "tests/fixtures/broken.json"], []))
    os.remove(bad)
    return "\n".join(parts)


def render(page, name, title, text):
    with open(os.path.join(ROOT, "docs", "demo", name + ".txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    page.set_content(
        "<html><body style='margin:0;background:#1e1e1e'><div style=\"display:inline-block;min-width:680px;"
        "font-family:'Noto Sans Mono CJK KR','Noto Sans CJK HK',monospace,'Noto Color Emoji'\">"
        "<div style='background:#333;color:#ddd;padding:6px 12px;font-size:13px;font-family:sans-serif'>"
        + html.escape(title) + "</div><pre style='margin:0;padding:14px 18px;color:#e6e6e6;font-size:15px;"
        "line-height:1.45'>" + html.escape(text) + "</pre></div></body></html>")
    page.locator("div").first.screenshot(path=os.path.join(ROOT, "docs", "screenshots", name + ".png"))


def main():
    from playwright.sync_api import sync_playwright
    shots = []
    only_log = "--only-git-log" in sys.argv   # 시나리오는 다시 실행하지 않고 git 그래프만 갱신
    for name, title, argv, lines in ([] if only_log else SCENARIOS):
        text = run_missing() if argv is None else run(argv, lines)
        shots.append((name, title, text))
    if "--git-log" in sys.argv or only_log:
        log = subprocess.run(["git", "--no-pager", "log", "--oneline", "--graph", "--all"], cwd=ROOT,
                             capture_output=True, text=True, encoding="utf-8").stdout.strip()
        shots.append(("git_log", "$ git --no-pager log --oneline --graph --all", log))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=2, viewport={"width": 1100, "height": 800})
        for name, title, text in shots:
            render(page, name, title, text)
        browser.close()
    print("rendered:", ", ".join(n for n, _, _ in shots))


if __name__ == "__main__":
    main()
