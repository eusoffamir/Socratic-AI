"""The evaluation scripts: Cohen's kappa and the mark sheet comparison."""
import importlib.util
from pathlib import Path

EVAL = Path(__file__).parent.parent / "eval"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, EVAL / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


compare = _load("compare_marks")
run_assessor = _load("run_assessor")


def test_cohen_kappa_matches_a_hand_worked_example():
    # 3 of 4 agree (75%); chance agreement is 50% x 25% + 50% x 75% = 50%, so kappa = (0.75 - 0.5) / 0.5 = 0.5
    assert compare.cohen_kappa(["1", "1", "0", "0"], ["1", "0", "0", "0"]) == 0.5
    assert compare.cohen_kappa(["1", "0"], ["1", "0"]) == 1.0
    assert compare.cohen_kappa(["1", "1"], ["1", "1"]) is None  # both always the same: undefined


def test_compare_prints_agreement_and_consistency(tmp_path, capsys, monkeypatch):
    head = "id,run," + ",".join(compare.STANDARDS) + ",level\n"
    (tmp_path / "h.csv").write_text(head + "R1,1," + "1,0," * 4 + "1,evidence\n" + "R2,1," + "0,1," * 4 + "0,none\n")
    (tmp_path / "ai.csv").write_text(head + "R1,1," + "1,0," * 4 + "1,evidence\n" + "R2,1," + "0,1," * 4 + "1,none\n"
                                     + "R1,2," + "1,0," * 4 + "1,evidence\n" + "R2,2," + "0,1," * 4 + "0,none\n")
    monkeypatch.setattr("sys.argv", ["compare_marks.py", str(tmp_path / "h.csv"), str(tmp_path / "ai.csv")])
    compare.main()
    out = capsys.readouterr().out
    assert "clarity" in out and "100%" in out and "fairness" in out and "50%" in out
    assert "1 of 2 answers got the same 9 marks in every run" in out


def test_every_test_set_case_maps_to_a_real_case():
    import csv
    rows = list(csv.DictReader(open(EVAL / "test_set.csv", encoding="utf-8-sig")))
    assert all(r["id"] for r in rows)  # the Excel marker at the start must not hide the id column
    assert all(run_assessor.session_for(r)["concept_id"] for r in rows)


def test_compare_includes_reasoning_and_knowledge_types(tmp_path, capsys, monkeypatch):
    head = "id," + ",".join(compare.STANDARDS) + ",inductive,deductive,abductive,k_causal\n"
    std = "1," * 9
    (tmp_path / "h.csv").write_text(head + "R1," + std + "1,0,1,1\n" + "R2," + std + "0,1,0,0\n")
    (tmp_path / "ai.csv").write_text(head + "R1," + std + "1,0,0,1\n" + "R2," + std + "0,1,0,1\n")
    monkeypatch.setattr("sys.argv", ["compare_marks.py", str(tmp_path / "h.csv"), str(tmp_path / "ai.csv")])
    compare.main()
    out = capsys.readouterr().out
    assert "inductive" in out and "abductive" in out and "k_causal" in out


def test_compare_graph_uses_the_graph_columns(tmp_path, capsys, monkeypatch):
    (tmp_path / "h.csv").write_text("id,inductive,deductive,abductive\nR1,1,0,1\nR2,0,1,0\n")
    (tmp_path / "ai.csv").write_text("id,inductive,deductive,abductive,graph_inductive,graph_deductive,graph_abductive\n"
                                     "R1,0,0,0,1,0,1\nR2,0,0,0,0,1,0\n")
    monkeypatch.setattr("sys.argv", ["compare_marks.py", str(tmp_path / "h.csv"), str(tmp_path / "ai.csv"), "--graph"])
    compare.main()
    lines = [l for l in capsys.readouterr().out.splitlines() if l.split()[:1] in (["inductive"], ["deductive"], ["abductive"])]
    assert len(lines) == 3 and all("100%" in l for l in lines)  # matches the graph columns, not the agent's 0s


def test_run_assessor_writes_reasoning_and_graph_columns():
    from app.knowledge import KNOWLEDGE_TYPES
    types = {"inductive": 1, "deductive": 0, "abductive": 1}
    a = {"reasoning": {"types": types, "knowledge": {k: 0 for k in KNOWLEDGE_TYPES},
                       "graph": {"steps": [{"dir": "backward"}], "types": {"inductive": 0, "deductive": 0, "abductive": 1}}}}
    cols = run_assessor.reasoning_cols(a)
    assert cols["inductive"] == 1 and cols["k_causal"] == 0 and cols["graph_abductive"] == 1
    assert run_assessor.reasoning_cols({"reasoning": None}) == {}
    only_jumps = {"reasoning": {**a["reasoning"], "graph": {"steps": [{"dir": "jump"}], "types": types}}}
    assert "graph_inductive" not in run_assessor.reasoning_cols(only_jumps)  # no real link, no graph reading
