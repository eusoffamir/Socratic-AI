"""Export every learner answer with its marks to one spreadsheet (CSV).

One row per answered round: the question asked, the learner's answer, the 9
standards (1 = met, 0 = not met), the reasoning move and more. Use it for the
thesis Results, kappa and factor analysis.

Run from the project folder:
    python eval/export_answers.py              -> eval/exports/answers_<date>.csv
    python eval/export_answers.py my_file.csv

It reads from wherever the app saves: Supabase if .env has its keys, else the
local sessions/ folder. The exports hold real learner answers, so the
eval/exports/ folder is never uploaded to GitHub (see .gitignore).
"""
import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.content import CONCEPTS, QUANT_TOPIC, STANDARDS  # noqa: E402

COLUMNS = (["session_id", "participant_code", "last_saved", "case", "topic", "case_title", "total_rounds", "ab_only", "reading_seconds", "ended",
            "round", "level_asked", "format", "question", "hint_opened", "answer", "answer_words"]
           + list(STANDARDS)
           + ["standards_met", "reasoning_move", "confused_or_frustrated", "copied_hint", "assessor_version"])


def rows_of(sid, session, saved):
    """One row per answer. Each answer replies to the question in the turn before it."""
    if session.get("mode") == "skill_check":
        return  # skill checks have their own shape; their export comes with the statistics (Goal 1 step 5)
    turns = session.get("turns", [])
    case = session.get("case") or CONCEPTS.get(session.get("concept_id")) or {}
    topic = case.get("topic") or (QUANT_TOPIC if session.get("concept_id") in CONCEPTS else "")
    for prev, t in zip(turns, turns[1:]):
        if t.get("answer") is None:
            continue
        a = t.get("assessment") or {}
        std = a.get("standards") or {}
        question = (prev.get("parts") or {}).get("question", "")
        options = (prev.get("parts") or {}).get("options") or []
        if options:
            question += " Options: " + " / ".join(f"{l}) {o}" for l, o in zip("AB", options))
        ins = prev.get("instruction") or {}
        yield {
            "session_id": sid, "participant_code": session.get("participant_code") or "",  # blank outside study mode
            "last_saved": saved, "case": session.get("concept_id"),
            "topic": topic, "case_title": case.get("title", ""),  # what the learner typed, or the quant topic
            "total_rounds": session.get("total_rounds"),  # 0 = no limit
            "ab_only": int(bool(session.get("ab_only"))), "reading_seconds": session.get("reading_seconds", 0),
            "ended": int(bool(session.get("ended"))), "round": prev.get("round"),  # the round of the question answered
            "level_asked": ins.get("level_name"), "format": ins.get("format"), "question": question,
            "hint_opened": "" if "hint_opened" not in t else int(t["hint_opened"]),  # blank = not recorded yet
            "answer": t["answer"], "answer_words": len(t["answer"].split()),
            **{k: int(bool(std.get(k))) for k in STANDARDS},
            "standards_met": sum(int(bool(std.get(k))) for k in STANDARDS),
            "reasoning_move": a.get("reasoning_move"),
            "confused_or_frustrated": int(bool(a.get("confused_or_frustrated"))),
            "copied_hint": int(bool(a.get("copied_hint"))),
            "assessor_version": t.get("assessor_version") or "",  # blank = before 15 October 2026
        }


def export(out):
    from app import storage  # imported here, after .env is loaded, so it reads from the right place
    rows = [row for sid, s, saved in storage.all_sessions() for row in rows_of(sid, s, saved)]
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig so Excel shows % and quotes right
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return rows


if __name__ == "__main__":
    from app.env import load_env
    load_env(ROOT / ".env")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "eval" / "exports" / f"answers_{date.today()}.csv"
    rows = export(out)
    from app import storage
    print(f"Saved {len(rows)} answers from {len({r['session_id'] for r in rows})} sessions "
          f"({storage.BACKEND}) to {out}")
