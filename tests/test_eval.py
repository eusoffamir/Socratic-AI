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
