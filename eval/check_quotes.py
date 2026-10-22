"""Check every Wikipedia quote in the quant knowledge graphs (Goal 3, step 4).

Fetches each article in knowledge.BOOKS and checks that each quote in
knowledge.SOURCES is really in it, word for word. A failure means the article
changed since its fixed version, or the quote was typed wrong. Needs internet.

Run: python -m eval.check_quotes
"""
import sys

from app import sources
from app.knowledge import BOOKS, SOURCES


def article_text(title):
    page = sources._get({"action": "query", "titles": title, "prop": "extracts|revisions", "explaintext": 1,
                         "rvprop": "ids", "redirects": 1})["query"]["pages"][0]
    return sources.clean_text(page.get("extract") or ""), page["revisions"][0]["revid"]


def main():
    texts = {}
    for key, (title, oldid) in BOOKS.items():
        texts[key], revid = article_text(title)
        print(f"{title}: fixed version {oldid}, live version {revid}{'' if revid == oldid else ' (changed)'}")
    bad = 0
    for case_id, nodes in SOURCES.items():
        for node_id, found in nodes.items():
            if isinstance(found, tuple) and sources.locate(found[1], texts[found[0]]) is None:
                bad += 1
                print(f"NOT FOUND {case_id}/{node_id} in {BOOKS[found[0]][0]}")
    quotes = sum(isinstance(f, tuple) for nodes in SOURCES.values() for f in nodes.values())
    print(f"{quotes - bad} of {quotes} quotes found.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
