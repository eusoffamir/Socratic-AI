"""Write the Explainer bank: every reasoning type with 1 or 2 knowledge types
(108 mixes), explained once on everyday life by the Explainer agent. The
Overall status page shows these, because it mixes topics and so has no one
topic to explain with.

It saves after each mix and skips the ones already in app/explain_bank.json,
so it can be stopped and run again (for example the next day, if the free
Gemini limit is reached). Read the file and fix any weak text by hand before
the pilot.

Run from the project folder (needs PROVIDER=gemini or anthropic in .env):
    python eval/build_explain_bank.py
    python eval/build_explain_bank.py --redo "inductive|factual"
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from app import explainer, llm_client  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--redo", action="append", default=[], help='a key to write again, like "inductive|factual"')
    ap.add_argument("--pause", type=float, default=6, help="seconds between calls, to stay under the free rate limit")
    args = ap.parse_args()
    if llm_client.PROVIDER == "mock":
        sys.exit("PROVIDER is mock, so there is no agent to write with. Set PROVIDER=gemini in .env.")
    bank = explainer.load_bank()
    for key in args.redo:
        bank.pop(key, None)
    todo = [(r, ks) for r, ks in explainer.all_mixes() if explainer.bank_key(r, ks) not in bank]
    print(f"{len(bank)} saved, {len(todo)} to write.")
    failed = 0
    for i, (r, ks) in enumerate(todo, 1):
        key = explainer.bank_key(r, ks)
        out = explainer.write(r, ks, explainer.GENERAL_TOPIC)
        if out is None:
            failed += 1
            print(f"{i}/{len(todo)} {key}: failed")
            if failed >= 5:
                print("5 failures, so the daily limit is probably reached. Run again later.")
                break
        else:
            out.pop("source", None)
            bank[key] = out
            # sorted, so a rerun gives a small, readable git diff
            explainer.BANK_PATH.write_text(json.dumps(dict(sorted(bank.items())), indent=1, ensure_ascii=False) + "\n",
                                           encoding="utf-8")
            print(f"{i}/{len(todo)} {key}: saved")
        time.sleep(args.pause)
    print(f"Done. {len(bank)} of {len(explainer.all_mixes())} in the bank.")


if __name__ == "__main__":
    main()
