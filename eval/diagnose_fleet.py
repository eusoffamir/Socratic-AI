"""How the diagnosis does on every failed test machine, not just the demo ones.

Follows the best check each time (value of information) until one fault is at
90 percent, as the Diagnosis page does, and counts how often the named fault is
right and how many readings it needed. The page shows the result from
app.diagnose.FLEET, so run this again and update FLEET if the method changes.

Run from the project folder (about a minute):
    python -m eval.diagnose_fleet
"""
from collections import Counter

from app import diagnose
from eval import pgm_ai4i as net


def run():
    m = diagnose.model()
    P, T = m["parents"], m["tables"]
    failed = [r for r in m["test"] if any(r[x] for x in net.MODES)]
    steps, right = [], 0
    for r in failed:
        evidence, left = {"type": r["type"], "failed": 1}, list(diagnose.CHECKS)
        while left:
            now, voi = net.value_of_information(P, T, evidence, left)
            if now >= diagnose.CONFIDENT:
                break
            best = max(left, key=voi.get)
            evidence[best] = r[best]
            left.remove(best)
        chances = net.mode_chances(P, T, evidence)
        right += r[max(chances, key=chances.get)] == 1
        steps.append(len(diagnose.CHECKS) - len(left))
    return {"machines": len(failed), "right": right, "avg_checks": round(sum(steps) / len(steps), 1),
            "spread": sorted(Counter(steps).items())}


if __name__ == "__main__":
    got = run()
    print(got)
    print("app.diagnose.FLEET says", diagnose.FLEET)
