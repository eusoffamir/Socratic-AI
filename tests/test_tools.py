from app import tools


def test_each_tool_gives_summary_and_chart():
    for name in tools.TOOLS:
        r = tools.run_tool(name)
        assert r["tool"] == name
        assert r["summary"]
        assert len(r["chart"]["bars"]) == 2


def test_tools_are_repeatable():
    assert tools.run_tool("simulate_streaks", {"stocks": 300}) == tools.run_tool("simulate_streaks", {"stocks": 300})


def test_streaks_close_to_theory():
    # 1 in 32 chance of 5 ups in a row, so about 156 of 5000 stocks
    hits = tools.run_tool("simulate_streaks", {"stocks": 5000, "days": 5})["chart"]["bars"][0]["value"]
    assert 110 < hits < 200


def test_bad_arguments_are_clamped_or_ignored():
    r = tools.run_tool("simulate_streaks", {"stocks": 10 ** 9, "days": "lots", "evil": 1})
    assert r["args"] == {"stocks": 5000, "days": 5}


def test_unknown_tool_does_not_crash():
    r = tools.run_tool("delete_everything", {})
    assert "No tool" in r["summary"] and r["chart"] is None
