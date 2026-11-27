"""Checks for the diagnosis demo (app/diagnose.py) on the AI4I open data."""
import pytest
from fastapi.testclient import TestClient

from app import diagnose, llm_client, main

# docs/supervisor/relation-classes.md
CLASSES = {"part_of", "causes", "prevents", "tests", "rules_out", "supports", "weakens",
           "fixed_by", "then", "defines", "leads_to"}


@pytest.fixture(autouse=True)
def _mock(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")


def walk(udi, pick="best"):
    """Follow the suggested check each time until the system is sure."""
    done = []
    while True:
        s = diagnose.step(udi, done)
        if s["finished"]:
            return s, done
        done.append(s["best"] if pick == "best" else s["checks"][-1]["check"])


def test_machine_list():
    got = diagnose.machine_list()
    assert 8 <= len(got["machines"]) <= 11
    assert got["accuracy"] == 100 and got["tested"] == 114
    assert {e[1] for e in got["graph"]["edges"]} <= CLASSES
    ids = {n["id"] for n in got["graph"]["nodes"]}
    assert all(a in ids and b in ids for a, _, b in got["graph"]["edges"])


def test_learned_causes_match_the_published_rules():
    edges = {(a, b) for a, rel, b in diagnose.graph()["edges"] if rel == "causes"}
    assert ("power", "PWF") in edges and ("strain", "OSF") in edges and ("wear", "TWF") in edges
    assert not any(b == "RNF" for _, b in edges)


def test_first_step_suggests_the_best_check():
    udi = diagnose.machine_list()["machines"][0]["udi"]
    s = diagnose.step(udi, [])
    assert not s["finished"] and s["done"] == []
    assert s["best"] == s["checks"][0]["check"] and len(s["checks"]) == len(diagnose.CHECKS)
    assert all(0 <= f["percent"] <= 100 for f in s["faults"])


def test_every_demo_machine_is_found_by_following_the_advice():
    for m in diagnose.machine_list()["machines"]:
        s, done = walk(m["udi"])
        assert s["right"], (m, done, s["named"])
        assert s["fix"] and s["rule"] and s["explanation"]["source"] == "fallback"
        assert s["rule_check"]["holds"], (m, s["rule_check"])  # the expert rule agrees with the network


def test_a_reading_has_its_number_and_band():
    r = next(iter(diagnose.machines().values()))
    got = diagnose.reading(r, "power")
    assert got["value"].endswith(" W") and got["band"] in ("low", "normal", "high")


def test_unknown_machine_and_bad_checks():
    with pytest.raises(KeyError):
        diagnose.step(-1, [])
    udi = diagnose.machine_list()["machines"][0]["udi"]
    s = diagnose.step(udi, ["power", "power", "nonsense"])
    assert [d["check"] for d in s["done"]] == ["power"]


def test_fallback_and_guard():
    s, _ = walk(diagnose.machine_list()["machines"][0]["udi"])
    text = diagnose.fallback(s)
    assert ":" not in text and s["named_name"] in text and "%" in text
    short = f"The power was low, so {s['named_name']} is the best explanation."
    assert diagnose.clean(short, s) == short
    assert diagnose.clean("The cause is clear: " + short, s) is None  # no colons
    assert diagnose.clean(short + " word" * 100, s) is None  # too long
    assert diagnose.clean("The machine is fine and nothing failed.", s) is None  # names another fault or none


def test_api():
    c = TestClient(main.app)
    got = c.get("/api/diagnose").json()
    udi = got["machines"][0]["udi"]
    step = c.post("/api/diagnose/step", json={"machine": udi, "done": ["strain"]}).json()
    assert step["done"][0]["check"] == "strain"
    assert c.post("/api/diagnose/step", json={"machine": -1, "done": []}).status_code == 404


def test_expert_rule_fits_every_failed_test_machine():
    from eval import pgm_ai4i as net
    failed = [r for r in diagnose.model()["test"] if any(r[m] for m in net.MODES)]
    assert all(any(diagnose.rule_check(r, m)["holds"] for m in net.MODES if r[m]) for r in failed)
    assert diagnose._down(8.595, 2) == 8.59


def test_machine_knowledge_three_parts():
    k = diagnose.knowledge()
    assert [b["id"] for b in k["book"]] == ["TWF", "HDF", "PWF", "OSF", "RNF"]
    assert k["agree"] and k["learned"]["OSF"] == ["strain", "type"]
    assert ["strain", "wear"] in k["links"]
    ids = {n["id"] for n in k["tree"]["nodes"]}
    assert all(a in ids and b in ids for a, _, b in k["tree"]["edges"])
    assert {n["fault"] for n in k["tree"]["nodes"] if n["kind"] == "decision"} == set(diagnose.FAULTS)


def test_what_if_moves_the_chances():
    base = {f["id"]: f["percent"] for f in diagnose.what_if({})["faults"]}
    got = diagnose.what_if({"type": "L", "strain": "high", "bogus": "x", "wear": "nonsense"})
    assert got["evidence"] == {"type": "L", "strain": "high"}
    now = {f["id"]: f["percent"] for f in got["faults"]}
    assert now["OSF"] > 90 > base["OSF"]


def test_machine_knowledge_api():
    from fastapi.testclient import TestClient
    from app.main import app
    c = TestClient(app)
    assert c.get("/api/machine-knowledge").json()["records"] == 7000
    r = c.post("/api/machine-knowledge/what-if", json={"evidence": {"wear": "old"}}).json()
    assert len(r["faults"]) == 5
