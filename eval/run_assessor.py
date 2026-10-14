"""Run the real Assessor on the test set and save its marks, in the same
columns as the human marking sheet (eval/marks_template.csv).

Run from the project folder:
    python eval/run_assessor.py                  all 61 answers, once
    python eval/run_assessor.py --repeats 3      3 runs, to check consistency
    python eval/run_assessor.py --limit 5        only the first 5 answers (a quick try)
    python eval/run_assessor.py --split test     only the "test" rows

Output: eval/ai_marks_<assessor version>.csv (one row per answer per run).
Then compare with human marks:  python eval/compare_marks.py eval/marks_<name>.csv eval/ai_marks_<version>.csv

Each answer is one free-tier Gemini call, and the free tier allows 15 calls a
minute and 500 a day shared with the live app, so the script waits between
calls. 61 answers take about 5 minutes. Run --repeats 3 on a quiet day.
"""
import argparse
import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.content import CONCEPTS, STANDARDS  # noqa: E402

CASE_IDS = {c["title"]: cid for cid, c in CONCEPTS.items()}  # the test set names cases by title
SECONDS_BETWEEN_CALLS = 4.5  # stays under 15 calls a minute


def session_for(row):
    """What the Assessor sees in the app: the question asked (with its options) and the case."""
    question = row["question"] + (f" Options: {row['options']}" if row["options"] else "")
    return {"concept_id": CASE_IDS.get(row["case"]), "last_tutor": question}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0, help="only the first N answers (0 = all)")
    ap.add_argument("--split", choices=["tune", "test"], help="only rows of this split")
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    from app import llm_client, prompts
    if llm_client.PROVIDER == "mock":
        sys.exit("No AI key found in .env, so this would only mark with fake mock replies. Set GOOGLE_API_KEY first.")

    rows = list(csv.DictReader(open(ROOT / "eval" / "test_set.csv", encoding="utf-8-sig")))  # -sig: the file starts with an Excel marker
    if args.split:
        rows = [r for r in rows if r["split"] == args.split]
    if args.limit:
        rows = rows[:args.limit]

    out = ROOT / "eval" / f"ai_marks_{prompts.ASSESSOR_VERSION}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "run", *STANDARDS, "level", "evidence_quote"])
        w.writeheader()
        for run in range(1, args.repeats + 1):
            for i, row in enumerate(rows, 1):
                try:
                    a = llm_client.call_assessor(session_for(row), row["answer"])
                except llm_client.LLMError as e:
                    print(f"  run {run}, {row['id']}: failed ({e}), so it is left out")
                    continue
                w.writerow({"id": row["id"], "run": run, **a["standards"], "level": a["reasoning_move"],
                            "evidence_quote": a["evidence_quote"]})
                f.flush()
                print(f"  run {run}, {i}/{len(rows)}: {row['id']} met {sum(a['standards'].values())} of 9")
                time.sleep(SECONDS_BETWEEN_CALLS)
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
