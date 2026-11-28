"""The teaching study (January 2027): two groups, one topic.

STUDY_CODES lists the participant codes of the tool group (they chat with the
tutor) and STUDY_CONTROL the codes of the control group (they only read the
same material, with no AI). Both lists are empty by default, so study mode is off.

The study topic is built ONCE by the Topic Builder (eval/build_study_topic.py)
and saved as study/topic.json, so it can be checked by a person and every
student, in both groups, gets exactly the same cases. The topic is not fixed to
quant; it is whatever topic the supervisor picks.
"""
import json
import os
from pathlib import Path

TOPIC_FILE = Path(__file__).resolve().parent.parent / "study" / "topic.json"


def _codes(name):
    return {c.strip().upper() for c in os.getenv(name, "").split(",") if c.strip()}


def control_codes():
    """Read each time, so tests can switch it."""
    return _codes("STUDY_CONTROL")


def codes():
    """Every code in the study, both groups."""
    return _codes("STUDY_CODES") | control_codes()


def group(code):
    """'control', 'tool', or None for a code not on either list."""
    code = (code or "").strip().upper()
    if code in control_codes():
        return "control"
    return "tool" if code in codes() else None


def topic_file():
    return Path(os.getenv("STUDY_TOPIC_FILE") or TOPIC_FILE)


def topic():
    """The saved study topic {"id", "topic", "cases"}, or None when there is none yet."""
    path = topic_file()
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) and data.get("cases") else None


def case(case_id):
    """One case of the study topic by id, or None."""
    t = topic()
    return next((c for c in t["cases"] if c.get("id") == case_id), None) if t else None


def reading(c):
    """What the control group reads for one case: the same story, reading and
    notes the tool group's tutor works from, but no questions and no AI."""
    return {"id": c["id"], "title": c.get("title", ""), "scenario": c.get("scenario", ""),
            "reading": c.get("reading") or {}, "notes": c.get("notes") or []}
