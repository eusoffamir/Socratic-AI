"""Two parallel test forms for the teaching study (docs/evaluation/teaching-study-plan.md).

The everyday skill check bank has 2 questions for each pair of reasoning type
(inductive, deductive, abductive) and core knowledge type (5 kinds), so 30 in all.
Form A takes question 1 of each pair and Form B takes question 2, so both forms
test the same 15 pairs and can be used as the pre and post test, with half the
students getting A first and half getting B first.

Run from the project folder (writes docs/evaluation/study-test-forms.md):
    python -m eval.study_forms
"""
from pathlib import Path

from app.skillcheck import ITEMS
from app.reasoning import CORE_KNOWLEDGE, REASONING_TYPES

OUT = Path(__file__).resolve().parent.parent / "docs" / "evaluation" / "study-test-forms.md"


def form(n):
    """The questions of form n (1 is A, 2 is B), in a fixed mixed order."""
    picked = [ITEMS[f"e-{r[:3]}-{k[:4]}-{n}"] for k in CORE_KNOWLEDGE for r in REASONING_TYPES]
    return picked


def main():
    lines = [
        "# Teaching study, test forms A and B (draft)",
        "",
        "Made by `eval/study_forms.py` from the everyday skill check bank in `app/skillcheck.py`, 27 November 2026.",
        "Draft for Dr Ho. The questions were written by Claude and still need a check that each one is sound.",
        "",
        "## How to use them",
        "",
        "1. Each form has 15 questions, 5 for each kind of reasoning, one for each kind of knowledge.",
        "2. Half the students take Form A before the session and Form B after. The other half take B first, then A.",
        "3. Students answer each question in a few sentences, by hand or in a plain form, not inside the tutor, so the control group is not at a disadvantage.",
        "4. Marking. An answer scores 1 if it uses the target kind of reasoning on the target kind of knowledge, and 0 if not, using the rules in `docs/evaluation/assessor-marking-guide.md`. Two markers mark a sample of answers to check they agree.",
        "5. Each student gets a total out of 15 and a score out of 5 for each kind of reasoning.",
        "",
        "The target is shown here for the markers only. Students see the situation and the question, not the target.",
        "",
    ]
    for name, n in (("A", 1), ("B", 2)):
        lines += [f"## Form {name}", ""]
        for i, q in enumerate(form(n), 1):
            lines += [f"{i}. {q['situation']} {q['question']}",
                      f"   (target {q['reasoning']} reasoning, {q['knowledge']} knowledge, id {q['id']})", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
