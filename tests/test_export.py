"""The data export: one row per answer, with the question it replied to."""
import csv
import importlib.util
from pathlib import Path

from app import graph, llm_client, orchestrator, storage

_spec = importlib.util.spec_from_file_location("export_answers", Path(__file__).parent.parent / "eval" / "export_answers.py")
export_answers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export_answers)


def test_export_writes_one_row_per_answer(monkeypatch, tmp_path):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(storage, "SESSION_DIR", tmp_path / "sessions")
    s = graph.run_turn(orchestrator.new_session("pattern_or_luck", 3), None)["session"]
    first_question = s["turns"][0]["parts"]["question"]
    s = graph.run_turn(s, "It could be luck, because many stocks rise 5 days in a row.")["session"]
    s["turns"][-1]["hint_opened"] = True
    s = graph.run_turn(s, "I would test it on new days.")["session"]
    storage.save_session("6f1c2c1e-3f0a-4a8e-9c55-0d6f1d9b2a11", s)

    out = tmp_path / "answers.csv"
    export_answers.export(out)
    rows = list(csv.DictReader(open(out, encoding="utf-8-sig")))
    assert len(rows) == 2
    assert rows[0]["question"] == first_question and rows[0]["hint_opened"] == "1"
    assert rows[0]["level_asked"] == "Clarify" and rows[0]["assessor_version"]
    assert [r["round"] for r in rows] == ["1", "2"]
    assert int(rows[0]["standards_met"]) == sum(int(rows[0][k]) for k in export_answers.STANDARDS)
