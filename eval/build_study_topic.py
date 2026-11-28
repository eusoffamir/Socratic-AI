"""Builds the teaching study topic once and saves it as study/topic.json.

Both groups then get exactly these cases: the tool group chats through them,
the control group reads the same story, reading and notes (app/study.py).
The topic is whatever the supervisor picks, it does not have to be quant.

Run (one Gemini call):
    npx.cmd dotenvx run -- python -m eval.build_study_topic "the topic, a question or a short reading"
Then read study/topic.json (or study/topic.md) and check every case by hand
before the study. Run it again to replace it.
"""
import json
import sys

from app import builder, study


def to_markdown(t):
    lines = [f"# Study topic, {t['topic']}", "", "Draft built by the Topic Builder. Check every line before the study.", ""]
    for c in t["cases"]:
        r = c.get("reading") or {}
        lines += [f"## {c['title']} ({c['id']})", "", c.get("scenario", ""), "",
                  "Reading", ""] + [f"- {i}" for i in r.get("idea") or []] + [
                  "", f"Example. {r.get('example', '')}", ""] + [
                  f"- {w} means {m}" for w, m in r.get("key_words") or []] + [
                  "", f"Think. {r.get('think', '')}", "", "Notes", ""]
        lines += [f"{i}. {n}" for i, n in enumerate(c.get("notes") or [], 1)]
        lines.append("")
    return "\n".join(lines)


def main(request):
    t = builder.build(request)
    path = study.topic_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
    path.with_suffix(".md").write_text(to_markdown(t), encoding="utf-8")
    print(f"Saved {len(t['cases'])} cases on '{t['topic']}' to {path} and {path.with_suffix('.md')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(" ".join(sys.argv[1:]))
