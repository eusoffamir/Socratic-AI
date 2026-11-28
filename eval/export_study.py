"""Export the teaching study, one row per participant code, both groups.

For the main analysis (posttest by group, pretest as covariate) the test
scores come from the paper or form tests. This export adds what the app saw,
so the two groups' time can be compared and the dose of each student is known.

    control group  cases read, minutes reading (from /api/study/read)
    tool group     cases chatted, answers given, minutes (first start to last save)

Run from the project folder:
    python eval/export_study.py                -> eval/exports/study_<date>.csv
Each student's answers are in eval/export_answers.py, by participant code.
"""
import csv
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

COLUMNS = ["participant_code", "group", "cases", "answers", "minutes", "first", "last"]


def _time(x):
    try:
        return datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except ValueError:
        return None


def rows_of(sessions):
    """sessions: (id, session, saved) as from storage.all_sessions()."""
    by = {}
    for _, s, saved in sessions:
        code = s.get("participant_code")
        if not code or s.get("mode") == "skill_check":
            continue
        p = by.setdefault(code, {"group": set(), "cases": set(), "answers": 0, "seconds": 0, "times": []})
        start, end = _time(s.get("consent_at")), _time(saved)
        if s.get("mode") == "control_reading":
            p["group"].add("control")
            p["seconds"] += s.get("reading_seconds") or 0
        else:
            p["group"].add("tool")
            p["answers"] += sum(1 for t in s.get("turns", []) if t.get("answer") is not None)
            if start and end:
                p["seconds"] += max(0, (end - start).total_seconds())
        p["cases"].add(s.get("concept_id"))
        p["times"] += [t for t in (start, end) if t]
    for code, p in sorted(by.items()):
        times = sorted(p["times"])
        yield {"participant_code": code,
               "group": "/".join(sorted(p["group"])),  # "control/tool" would mean a mix-up, so check it
               "cases": len(p["cases"]), "answers": p["answers"] if "tool" in p["group"] else "",
               "minutes": round(p["seconds"] / 60, 1),
               "first": times[0].isoformat(timespec="minutes") if times else "",
               "last": times[-1].isoformat(timespec="minutes") if times else ""}


def export(out):
    from app import storage
    rows = list(rows_of(storage.all_sessions()))
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return rows


if __name__ == "__main__":
    from app.env import load_env
    load_env(ROOT / ".env")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "eval" / "exports" / f"study_{date.today()}.csv"
    rows = export(out)
    print(f"Saved {len(rows)} participants to {out}")
