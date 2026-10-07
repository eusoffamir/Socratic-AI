"""Small quant simulations the Tutor agent can run. Plain Python, no LLM.

Each tool is seeded, so the same arguments always give the same result. That
keeps sessions repeatable for the thesis. Each returns a dict with:
  summary: one short sentence the Tutor can quote to the learner
  chart:   simple bar data the page draws in the case file panel
  args:    the arguments actually used, after clamping to safe ranges
"""
import random
import statistics

SEED = 26005


def _clamp(value, low, high, default):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, value))


def simulate_streaks(stocks=500, days=5):
    stocks = _clamp(stocks, 10, 5000, 500)
    days = _clamp(days, 2, 15, 5)
    rng = random.Random(SEED)
    hits = 0
    for _ in range(stocks):
        ups = [rng.random() < 0.5 for _ in range(days)]  # each day is a coin flip
        hits += all(ups)
    return {
        "args": {"stocks": stocks, "days": days},
        "summary": f"{stocks} stocks × {days} days → {hits} went up every day. Pure luck.",
        "chart": {"title": f"{days} up days in a row, by luck",
                  "bars": [{"label": "Streak", "value": hits}, {"label": "No streak", "value": stocks - hits}]},
    }


def test_many_rules(rules=200, days=100):
    rules = _clamp(rules, 5, 2000, 200)
    days = _clamp(days, 20, 500, 100)
    rng = random.Random(SEED)
    # Every rule is pure noise: its daily return is random with an average of zero.
    results = []
    for _ in range(rules):
        old = sum(rng.gauss(0, 1) for _ in range(days))
        new = sum(rng.gauss(0, 1) for _ in range(days))
        results.append((old, new))
    best_old, best_new = max(results)
    return {
        "args": {"rules": rules, "days": days},
        "summary": f"{rules} random rules → best one: {best_old:+.0f}% on old data, {best_new:+.0f}% on new data.",
        "chart": {"title": "Best random rule",
                  "bars": [{"label": "Old data", "value": round(best_old)}, {"label": "New data", "value": round(best_new)}],
                  "unit": "%"},
    }


def random_pairs_correlation(pairs=100, length=12):
    pairs = _clamp(pairs, 5, 1000, 100)
    length = _clamp(length, 5, 250, 12)
    rng = random.Random(SEED)

    def walk():
        x, path = 0.0, []
        for _ in range(length):
            x += rng.gauss(0, 1)
            path.append(x)
        return path

    strong = 0
    for _ in range(pairs):
        try:
            if abs(statistics.correlation(walk(), walk())) > 0.7:
                strong += 1
        except statistics.StatisticsError:
            pass  # a flat series has no correlation; count it as weak
    return {
        "args": {"pairs": pairs, "length": length},
        "summary": f"{pairs} unrelated random pairs → {strong} moved together strongly. Pure luck.",
        "chart": {"title": "Unrelated pairs that moved together",
                  "bars": [{"label": "Strong link", "value": strong}, {"label": "Weak link", "value": pairs - strong}]},
    }


TOOLS = {
    "simulate_streaks": (simulate_streaks,
                         "simulate_streaks(stocks, days): flips a coin for each stock each day. "
                         "Counts how many went up every day by luck."),
    "test_many_rules": (test_many_rules,
                        "test_many_rules(rules, days): makes random trading rules, picks the best on old data, "
                        "then checks it on new data."),
    "random_pairs_correlation": (random_pairs_correlation,
                                 "random_pairs_correlation(pairs, length): makes pairs of unrelated random prices. "
                                 "Counts how many move together strongly by luck."),
}


def run_tool(name, args=None):
    """Run a tool by name. Unknown names or bad arguments never raise."""
    if name not in TOOLS:
        return {"tool": name, "args": {}, "summary": f"No tool called {name!r}.", "chart": None}
    func = TOOLS[name][0]
    args = args if isinstance(args, dict) else {}
    allowed = func.__code__.co_varnames[:func.__code__.co_argcount]
    result = func(**{k: v for k, v in args.items() if k in allowed})
    return {"tool": name, **result}
