"""Export every skill check answer (Goal 1) to one spreadsheet (CSV).

One row per answer: the question's tags (reasoning type and knowledge type),
the answer, attained (1 or 0), the 9 standards and the Reasoning agent's marks.
Use it for the statistics, or to check the marks by hand.

Run from the project folder:
    python eval/export_checks.py          -> eval/exports/checks_<date>.csv
    python eval/export_checks.py my.csv

The exports hold real learner answers, so eval/exports/ is never uploaded to GitHub.
"""
import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import storage  # noqa: E402
from app.content import STANDARDS  # noqa: E402
from app.knowledge import KNOWLEDGE_TYPES  # noqa: E402
from app.reasoning import REASONING_TYPES  # noqa: E402

COLUMNS = (["check_id", "participant_code", "last_saved", "item", "reasoning", "knowledge", "answer", "attained"]
           + list(STANDARDS) + [f"shows_{r}" for r in REASONING_TYPES] + [f"uses_{k}" for k in KNOWLEDGE_TYPES]
           + ["copied_hint", "assessor_version"])


def rows_of(sid, check, saved):
    if check.get("mode") != "skill_check":
        return
    for t in check.get("turns", []):
        a = t.get("assessment") or {}
        rs = a.get("reasoning") or {}
        yield {"check_id": sid, "participant_code": check.get("participant_code") or "", "last_saved": saved,
               "item": t["item"], "reasoning": t["reasoning"], "knowledge": t["knowledge"],
               "answer": t["answer"], "attained": t["attained"],
               **{k: int(bool((a.get("standards") or {}).get(k))) for k in STANDARDS},
               **{f"shows_{r}": int(bool((rs.get("types") or {}).get(r))) for r in REASONING_TYPES},
               **{f"uses_{k}": int(bool((rs.get("knowledge") or {}).get(k))) for k in KNOWLEDGE_TYPES},
               "copied_hint": int(bool(a.get("copied_hint"))), "assessor_version": t.get("assessor_version") or ""}


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "eval" / "exports" / f"checks_{date.today()}.csv")
    rows = [r for sid, s, saved in storage.all_sessions() for r in rows_of(sid, s, saved)]
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} skill check answers written to {out}.")


if __name__ == "__main__":
    main()
