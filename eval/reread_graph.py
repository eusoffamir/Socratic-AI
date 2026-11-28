"""Reads the saved graph steps of an Assessor run again with the current
app/traverse.py, with no model call, so a change to the reading rules can be
checked against the human marks at once.

    python eval/reread_graph.py eval/ai_marks_<run>.csv          (rewrites its graph_ columns)
    python eval/compare_marks.py eval/marks_eusoff.csv eval/ai_marks_<run>.csv --graph

Only runs made after 28 November 2026 have the graph_steps column.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import traverse  # noqa: E402
from app.reasoning import REASONING_TYPES  # noqa: E402
from eval.run_assessor import CASE_IDS  # noqa: E402


def main(path):
    cases = {r["id"]: CASE_IDS.get(r["case"]) for r in csv.DictReader(open(ROOT / "eval" / "test_set.csv", encoding="utf-8-sig"))}
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    if not rows or "graph_steps" not in rows[0]:
        sys.exit("This file has no graph_steps column, so run eval/run_assessor.py again first.")
    landed = 0
    for r in rows:
        g = traverse.read(cases[r["id"]], json.loads(r["graph_steps"] or "[]")) if cases.get(r["id"]) else None
        hit = bool(g) and traverse.landed(g)
        landed += hit
        for k in REASONING_TYPES:
            r[f"graph_{k}"] = g["types"][k] if hit else ""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{landed} of {len(rows)} answers have a step on reasoning links. Saved to {path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
