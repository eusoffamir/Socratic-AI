"""Can an AI model turn a real manual into a diagnosis rule? (28 November 2026)

The AI reads the troubleshooting tables of two real rotary screw compressor manuals
and the MetroPT-3 sensor notes, then picks which hourly readings move in an air leak,
quoting the manual for each pick. We check every quote is really in the manual, then
score the rule on the 4 real air leaks in MetroPT-3 (eval/metropt_test.py). A control
run gets the same notes without the manual, so we see what the manual adds.

Manuals (copyrighted, so their text is not kept in this public repo; pass the text
files made with `pdftotext -layout`):
  Champion D5 rotary screw air compressor manual (D5-MANS, March 2019), Troubleshooting
  Guide, pages 30 to 32
  SSR UP6 40 / 50PE / 50PEI operation manual, trouble shooting table

Unlike the first MetroPT test, the notes now say what 0 and 1 mean in this data,
so only the manual differs between the two kinds of run.

    npx.cmd dotenvx run -- python -m eval.manual_test --draft d5a.txt ssr.txt 5
    python -m eval.manual_test "MetroPT3(AirCompressor).csv" d5a.txt ssr.txt
"""
import json
import re
import sys
import time
from pathlib import Path

from eval import metropt_test as mt

SAVED = Path(__file__).parent / "data" / "manual_ai_rules.json"
MEANING = ("\nWhat 0 and 1 mean in this data (checked on the readings): COMP and MPG read 1 while the compressor "
           "rests and 0 while it loads air; DV_eletric reads 1 while it loads; LPS reads 1 under 7 bar.")

WITH_MANUAL = """You are a maintenance engineer. A metro train's air compressor is logged by the sensors in NOTES.
Using the troubleshooting tables in MANUAL, say which hourly readings in MENU move when there is an air leak in the system.
Pick 2 to 6 readings, each with +1 if it rises in a leak or -1 if it falls. For each pick, copy the exact words from MANUAL that support it (a short phrase, copied exactly).
Return only JSON: {"rule": {"reading": 1}, "quote": {"reading": "exact words from MANUAL"}, "why": {"reading": "one short reason"}}"""

WITHOUT_MANUAL = """You are a maintenance engineer. A metro train's air compressor is logged by the sensors in NOTES.
Say which hourly readings in MENU move when there is an air leak in the system.
Pick 2 to 6 readings, each with +1 if it rises in a leak or -1 if it falls.
Return only JSON: {"rule": {"reading": 1}, "why": {"reading": "one short reason"}}"""


def manual_text(d5_path, ssr_path):
    d5 = Path(d5_path).read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(i for i, l in enumerate(d5) if "Troubleshooting Guide" in l and "...." not in l)
    end = next(i for i, l in enumerate(d5) if i > start and "- 32 -" in l)
    ssr = Path(ssr_path).read_text(encoding="utf-8", errors="replace")
    return ("CHAMPION D5 ROTARY SCREW AIR COMPRESSOR, TROUBLESHOOTING GUIDE\n" + "\n".join(d5[start:end + 1])
            + "\n\nSSR UP6 ROTARY SCREW COMPRESSOR, TROUBLE SHOOTING\n" + ssr)


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def quote_ok(q, manual, window=400):
    """The quote's words appear in the manual in order, close together. Words may be
    split across lines with other table columns in between, as pdftotext gives them."""
    words, text = _norm(q or "").split(), _norm(manual)
    if not words:
        return False
    text = " " + text + " "
    start = text.find(" " + words[0] + " ")
    while start != -1:
        at, ok = start + len(words[0]) + 1, True
        for w in words[1:]:
            n = text.find(" " + w + " ", at - 1, start + window)
            if n == -1:
                ok = False
                break
            at = n + len(w) + 1
        if ok:
            return True
        start = text.find(" " + words[0] + " ", start + 1)
    return False


def items():
    return {k: next((v for s, v in mt.MENU_NOTES.items() if k == s or k.endswith(s)), k) for k in mt.menu()}


def draft(d5, ssr, n):
    from app import llm_client
    manual = manual_text(d5, ssr)
    notes = (Path(__file__).parent / "data" / "metropt_description.txt").read_text(encoding="utf-8") + MEANING
    menu = items()
    out = []
    for kind, system in (("manual", WITH_MANUAL), ("no_manual", WITHOUT_MANUAL)):
        payload = {"NOTES": notes, "MENU": menu, **({"MANUAL": manual} if kind == "manual" else {})}
        user = json.dumps(payload, ensure_ascii=False)
        for i in range(n):
            used = llm_client.track_models()
            try:
                reply = llm_client._generate(system, user, max_tokens=1500, json_mode=True)
            except Exception as e:
                reply = None
                print(kind, i + 1, "failed", e)
            data = llm_client._parse_json(reply or "") or {}
            rule = {k: (1 if v > 0 else -1) for k, v in (data.get("rule") or {}).items()
                    if k in menu and isinstance(v, (int, float)) and v}
            quotes = data.get("quote") or {}
            out.append({"kind": kind, "models": used, "chars_in": len(system) + len(user), "rule": rule,
                        "quote": quotes, "quote_ok": {k: quote_ok(quotes.get(k), manual) for k in rule} if kind == "manual" else None,
                        "why": data.get("why"), "reply": reply})
            print(kind, i + 1, rule, used)
            time.sleep(8)  # stay inside the free plan's tokens a minute
    SAVED.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


def score(csv_path, d5, ssr):
    runs = json.loads(SAVED.read_text(encoding="utf-8"))
    manual = manual_text(d5, ssr)
    rows = mt.hours(csv_path)
    stats = mt.normal_stats(rows, list(rows[0]["x"]))
    print(f"{'run':14} {'rank':>5}  caught  quotes real  rule")
    for kind in ("manual", "no_manual"):
        ranks = []
        for i, r in enumerate([x for x in runs if x["kind"] == kind], 1):
            if not r["rule"]:
                print(f"  {kind} {i}: no usable rule")
                continue
            s = mt.ai_score(r["rule"], stats)
            got = []
            for j in range(len(mt.SPANS)):
                test = mt.block(j, rows)
                ids = {id(x) for x in test}
                lim = mt.limit_for(s, [x for x in rows if id(x) not in ids])
                got.append((mt.auc(s, test), any(s(x) > lim for x in test if x["leak"] == j)))
            rank = sum(a for a, _ in got) / len(got)
            ranks.append(rank)
            q = r["quote_ok"]
            # recheck the quotes against the manual given now
            if kind == "manual":
                q = {k: quote_ok((r["quote"] or {}).get(k), manual) for k in r["rule"]}
            qtxt = f"{sum(q.values())} of {len(q)}" if q is not None else "-"
            rule = ", ".join(f"{k} {'+' if d > 0 else '-'}" for k, d in r["rule"].items())
            print(f"  {kind:10} {i} {rank:5.0%}  {sum(c for _, c in got)} of 4  {qtxt:>11}  {rule}")
        if ranks:
            print(f"  {kind} average rank {sum(ranks) / len(ranks):.0%} over {len(ranks)} runs\n")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "--draft":
        draft(a[1], a[2], int(a[3]) if len(a) > 3 else 5)
    else:
        score(a[0], a[1], a[2])
