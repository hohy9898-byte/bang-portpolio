"""
챗봇 평가 스크립트

    python eval/run_eval.py               # 전체 1회
    python eval/run_eval.py --runs 3      # 전체 3회 (4B 모델은 답변이 매번 달라서 평균을 보는 것을 권장)
    python eval/run_eval.py --only topic  # id 가 topic 으로 시작하는 케이스만
    python eval/run_eval.py --label "검색어 지시문 추가"  # 결과 파일에 메모 남기기

답변에 등장한 도서 제목을 보유 도서 100권과 대조해 정답 도서 목록과 비교한다.
match 기준
  - all    : 정답 도서를 빠짐없이, 다른 도서 없이 답변해야 통과
  - any    : 정답 도서 중 1권 이상 포함하면 통과 (주제 추천처럼 정답이 여러 개인 경우)
  - none   : 도서를 언급하지 않아야 통과 (일반 대화)
  - ignore : 도서 목록은 보지 않음 (must_include_any 만 확인)
보유 도서에 없는 제목을 **굵게** 쓴 답변은 별도로 집계한다 (지어낸 도서일 가능성).
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from uuid import uuid4

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(EVAL_DIR)

# main.py 가 ./books.txt, ./chroma_store 를 상대 경로로 읽으므로 프로젝트 폴더에서 실행
os.chdir(PROJECT_DIR)
sys.path.insert(0, PROJECT_DIR)

from books import find_books  # noqa: E402
from main import BOOKS, TITLE_ALIASES, ask, find_unverified_titles  # noqa: E402


def find_titles(answer: str) -> set[str]:
    return {book["title"] for book in find_books(answer, TITLE_ALIASES)}


def score(case: dict, answer: str) -> dict:
    expected = set(case["expected"])
    predicted = find_titles(answer)
    # 상세 화면 케이스: 보고 있는 도서 자체를 언급하는 것은 채점에서 제외
    if case.get("book_title"):
        predicted.discard(case["book_title"])

    hit = predicted & expected
    match = case["match"]
    if match == "all":
        passed = predicted == expected
    elif match == "any":
        passed = bool(hit)
    elif match == "none":
        passed = not predicted
    else:
        passed = True

    keywords = case.get("must_include_any")
    if keywords and not any(k in answer for k in keywords):
        passed = False

    return {
        "passed": passed,
        "precision": len(hit) / len(predicted) if predicted else None,
        "recall": len(hit) / len(expected) if expected else None,
        "missing": sorted(expected - predicted) if match == "all" else [],
        "extra": sorted(predicted - expected) if match in ("all", "none") else [],
        # 굵게 표시됐지만 보유 도서에 없는 제목 (지어낸 도서일 가능성, 통과 여부와는 별개로 집계)
        "unverified": find_unverified_titles(answer),
    }


def run_case(case: dict) -> dict:
    session_id = f"eval-{uuid4()}"
    start = time.time()
    tools = []
    for prompt in case["turns"]:
        messages = ask(prompt, session_id, case.get("book_title"))
        for msg in messages:
            for call in getattr(msg, "tool_calls", None) or []:
                tools.append({"name": call["name"], "args": call["args"]})
    answer = messages[-1].content
    return {
        "id": case["id"],
        "type": case["type"],
        "answer": answer,
        # 마지막 턴뿐 아니라 전체 대화에서 호출된 툴
        "tools": tools,
        "seconds": round(time.time() - start, 1),
        **score(case, answer),
    }


def validate(cases: list[dict]) -> None:
    titles = {b["title"] for b in BOOKS}
    for case in cases:
        unknown = [t for t in case["expected"] if t not in titles]
        if unknown:
            raise ValueError(f"{case['id']}: 보유 도서에 없는 정답 {unknown}")


def mean(values: list) -> str:
    values = [v for v in values if v is not None]
    return f"{sum(values) / len(values):.2f}" if values else "-"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--only", default="", help="이 문자열로 시작하는 id 만 실행")
    parser.add_argument("--label", default="", help="결과 파일에 남길 메모")
    args = parser.parse_args()

    with open(os.path.join(EVAL_DIR, "cases.json"), encoding="utf-8") as f:
        cases = [c for c in json.load(f) if c["id"].startswith(args.only)]
    validate(cases)

    results = []
    for run in range(1, args.runs + 1):
        for case in cases:
            result = run_case(case)
            result["run"] = run
            results.append(result)
            mark = "PASS" if result["passed"] else "FAIL"
            print(f"[{run}/{args.runs}] {mark} {case['id']:<12} {result['seconds']:>5}s")

    # ===== 요약 =====
    by_type = defaultdict(list)
    for r in results:
        by_type[r["type"]].append(r)

    print("\n" + "=" * 64)
    print(f"{'유형':<8}{'통과율':>10}{'정밀도':>10}{'재현율':>10}{'평균 시간':>12}")
    print("-" * 64)
    for type_, rs in by_type.items():
        passed = sum(r["passed"] for r in rs)
        print(
            f"{type_:<8}{passed:>5}/{len(rs):<4}"
            f"{mean([r['precision'] for r in rs]):>10}"
            f"{mean([r['recall'] for r in rs]):>10}"
            f"{mean([r['seconds'] for r in rs]):>11}s"
        )
    print("-" * 64)
    total = sum(r["passed"] for r in results)
    print(f"{'전체':<8}{total:>5}/{len(results):<4} ({total / len(results):.0%})")
    suspicious = [r for r in results if r["unverified"]]
    print(f"보유 도서에 없는 제목이 나온 답변: {len(suspicious)}개")
    for r in suspicious:
        print(f"  - {r['id']} (run {r['run']}): {r['unverified']}")

    failures = [r for r in results if not r["passed"]]
    if failures:
        print("\n[실패 케이스]")
        for r in failures:
            tools = ", ".join(f"{t['name']}({t['args']})" for t in r["tools"]) or "툴 호출 없음"
            print(f"- {r['id']} (run {r['run']})")
            print(f"  툴: {tools}")
            if r["missing"]:
                print(f"  누락: {r['missing']}")
            if r["extra"]:
                print(f"  초과: {r['extra']}")
            print(f"  답변: {r['answer'][:150]!r}")

    os.makedirs(os.path.join(EVAL_DIR, "results"), exist_ok=True)
    path = os.path.join(EVAL_DIR, "results", f"{datetime.now():%Y%m%d-%H%M%S}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"label": args.label, "runs": args.runs, "passed": total, "total": len(results), "results": results},
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\n결과 저장: {os.path.relpath(path, PROJECT_DIR)}")


if __name__ == "__main__":
    main()
