"""Compare two mark sheets: percent agreement and Cohen's kappa per standard.

Works for human vs human (are the rules clear?) and human vs AI (is the
Assessor a good marker?). Both files need an "id" column and the 9 standard
columns (1 or 0), like eval/marks_template.csv. A "level" column is compared
too if both files have it.

Run from the project folder:
    python eval/compare_marks.py eval/marks_amir.csv eval/marks_drho.csv
    python eval/compare_marks.py eval/marks_amir.csv eval/ai_marks_2026-10-15.csv --split test

If a file has several runs (a "run" column from run_assessor.py --repeats),
run 1 is compared, and the script also shows how often all runs agreed.

Kappa is undefined when one marker gives the same mark to every answer
(shown as n/a). With 61 answers, treat kappa as a rough guide, not a precise number.
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.content import STANDARDS  # noqa: E402


def cohen_kappa(a, b):
    """Cohen's kappa for two equal-length lists of labels. None if undefined."""
    n = len(a)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] / n * cb[k] / n for k in set(ca) | set(cb))
    return None if pe == 1 else (po - pe) / (1 - pe)


def load(path, keep_ids=None):
    """{id: {column: value}} using run 1, plus {id: [runs]} for consistency."""
    runs = defaultdict(list)
    for row in csv.DictReader(open(path, encoding="utf-8-sig")):
        if keep_ids is not None and row["id"] not in keep_ids:
            continue
        runs[row["id"]].append(row)
    first = {i: sorted(rs, key=lambda r: int(r.get("run") or 1))[0] for i, rs in runs.items()}
    return first, runs


def filled(row, col):
    return (row.get(col) or "").strip() != ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("first")
    ap.add_argument("second")
    ap.add_argument("--split", choices=["tune", "test"], help="only rows of this split (from eval/test_set.csv)")
    args = ap.parse_args()

    keep = None
    if args.split:
        keep = {r["id"] for r in csv.DictReader(open(ROOT / "eval" / "test_set.csv", encoding="utf-8-sig"))
                if r["split"] == args.split}
    a, _ = load(args.first, keep)
    b, b_runs = load(args.second, keep)
    _, a_runs = load(args.first, keep)

    print(f"{'standard':13s} {'answers':>7s} {'agree':>6s} {'kappa':>6s} {'1s first':>9s} {'1s second':>10s}")
    for col in [*STANDARDS, "level"]:
        ids = [i for i in a if i in b and filled(a[i], col) and filled(b[i], col)]
        if not ids:
            continue
        x = [a[i][col].strip().lower() for i in ids]
        y = [b[i][col].strip().lower() for i in ids]
        agree = sum(p == q for p, q in zip(x, y)) / len(ids)
        k = cohen_kappa(x, y)
        ones = (f"{x.count('1'):>9d} {y.count('1'):>10d}" if col != "level" else f"{'':>9s} {'':>10s}")
        print(f"{col:13s} {len(ids):>7d} {agree:>6.0%} {('n/a' if k is None else f'{k:.2f}'):>6s} {ones}")

    for name, runs in [("first", a_runs), ("second", b_runs)]:
        multi = {i: rs for i, rs in runs.items() if len(rs) > 1}
        if multi:
            same = sum(all(all(r[c] == rs[0][c] for c in STANDARDS) for r in rs) for rs in multi.values())
            print(f"\nConsistency of the {name} file: {same} of {len(multi)} answers got the same 9 marks in every run.")


if __name__ == "__main__":
    main()
