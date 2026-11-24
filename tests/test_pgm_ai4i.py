"""Checks for the AI4I proof of concept (eval/pgm_ai4i.py, Meeting 3 task 8)."""
import itertools
import math

import pytest

from eval import pgm_ai4i as poc


@pytest.fixture(scope="module")
def data():
    rows = poc.load()
    train, test = poc.split(rows)
    return rows, train, test


def test_load_matches_the_dataset(data):
    rows, train, test = data
    assert len(rows) == 10000 and len(train) == 7000 and len(test) == 3000
    assert sum(r["HDF"] for r in rows) == 115 and sum(r["OSF"] for r in rows) == 98
    assert all(r[x] in poc.VALUES[x] for r in rows[:200] for x in poc.RAW + poc.ENGINEER)


def test_engineer_network_finds_the_true_causes(data):
    _, train, _ = data
    parents = poc.learn_structure(train, poc.ENGINEER)
    assert {m: set(parents[m]) for m in poc.MODES} == poc.TRUE_PARENTS
    # knowledge rule: no failure mode points to a reading or to another mode
    assert all(p in poc.ENGINEER for ps in parents.values() for p in ps)


def test_tables_add_up_and_have_no_zeros(data):
    _, train, _ = data
    parents = {"type": (), "wear": ("type",), "TWF": ("wear",)}
    tables = poc.learn_tables(parents, train)
    for x, ps in parents.items():
        for key in itertools.product(*(poc.VALUES[p] for p in ps)):
            row = [tables[x][key + (v,)] for v in poc.VALUES[x]]
            assert math.isclose(sum(row), 1) and min(row) > 0


def test_variable_elimination_matches_adding_up_every_case(data):
    _, train, _ = data
    parents = {"type": (), "wear": ("type",), "torque": (), "strain": ("torque", "wear"),
               "TWF": ("wear",), "HDF": (), "PWF": ("torque",), "OSF": ("strain", "type"), "RNF": ()}
    tables = poc.learn_tables(parents, train)
    evidence = {"type": "L", "failed": 1}
    fast = poc.mode_chances(parents, tables, evidence)

    names = list(parents)
    total, hits = 0.0, {m: 0.0 for m in poc.MODES}
    for values in itertools.product(*(poc.VALUES[v] for v in names)):
        a = dict(zip(names, values))
        if a["type"] != "L" or not any(a[m] for m in poc.MODES):
            continue
        p = math.prod(tables[x][tuple(a[q] for q in parents[x]) + (a[x],)] for x in names)
        total += p
        for m in poc.MODES:
            hits[m] += p * a[m]
    for m in poc.MODES:
        assert math.isclose(fast[m], hits[m] / total, rel_tol=1e-9)


def test_value_of_information_is_never_negative(data):
    _, train, _ = data
    parents = poc.learn_structure(train, poc.ENGINEER)
    tables = poc.learn_tables(parents, train)
    _, voi = poc.value_of_information(parents, tables, {"type": "M", "failed": 1}, ["gap", "power", "wear"])
    assert all(v >= -1e-12 for v in voi.values())
