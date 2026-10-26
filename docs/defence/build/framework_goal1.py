"""Goal 1 framework figure for the defence (slide "Goal 1: Reasoning and Knowledge Layer"). Run: python framework_goal1.py out.png
Solid navy boxes are built, dashed gold boxes are planned."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = sys.argv[1]
TEAL, TEAL_L, GREY, GREY_L, AMBER, AMBER_L, INK = "#07517A", "#DCEAF2", "#475569", "#F5F7F9", "#8A6D1F", "#F3EEDC", "#0f172a"
plt.rcParams.update({"font.family": "Arial"})

fig, ax = plt.subplots(figsize=(16, 9))
fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")


def box(x, y, w, h, title, sub="", kind="built", tsize=17, ssize=13):
    fc, ec, ls = {"built": (TEAL_L, TEAL, "-"), "plan": (AMBER_L, AMBER, "--"), "user": ("#ffffff", INK, "-"),
                  "frame": (GREY_L, "#94A3B8", "-")}[kind]
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                fc=fc, ec=ec, lw=2.4, ls=ls))
    if title:
        ax.text(x, y + (0.15 if sub else 0), title, ha="center", va="center", fontsize=tsize, weight="bold", color=INK)
    if sub:
        ax.text(x, y - 0.2, sub, ha="center", va="center", fontsize=ssize, color=GREY)


def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.8, mutation_scale=16))


box(8, 8.4, 14.72, 0.88, "Paul's 6 Socratic question levels (built), the ladder the Tutor climbs",
    "clarify, assumptions, evidence, viewpoints, implications, question the question")
arrow(8, 7.96, 8, 7.36)
box(8, 5.33, 15.36, 4.06, "", kind="frame")
ax.text(0.72, 6.97, "Each answer is checked on 4 things (Assessor and Reasoning agent, in one shared call)",
        fontsize=13.5, weight="bold", color=TEAL, va="center")

cols = [
    (2.24, "1. Prerequisites", "8 elements of thought", ["Purpose", "Question at issue", "Information"], "plan"),
    (6.08, "2. Reasoning", "modes of reasoning", ["Inductive", "Deductive", "Abductive", "later, analogic and", "counterfactual"], "built"),
    (9.92, "3. Knowledge", "types of knowledge used", ["Factual", "Conceptual", "Procedural", "Causal", "Relational",
                                                         "later, strategic,", "metacognitive, epistemic"], "built"),
    (13.76, "4. Quality", "Paul-Elder standards", ["Clarity, accuracy,", "precision, relevance,", "depth, breadth, logic,",
                                                     "significance, fairness"], "built"),
]
for x, t, s, items, k in cols:
    box(x, 6.08, 3.36, 0.83, t, s, k)
    for i, it in enumerate(items):
        grey = it.startswith(("later", "metacog", "counterf"))
        ax.text(x, 5.42 - i * 0.256, it, ha="center", va="center", fontsize=13, color=GREY if grey else INK)
for x1, x2 in [(3.92, 4.4), (7.76, 8.24), (11.6, 12.08)]:
    arrow(x1, 6.08, x2, 6.08)

arrow(4.24, 3.30, 4.24, 2.70)
box(4.24, 2.26, 6.88, 0.88, "5. Complexity (planned)", "SOLO levels, by how many knowledge types are combined", "plan")
box(11.76, 2.26, 6.88, 0.88, "6. Statistics over many trials (built)", "Hamming distance and a mastery estimate per learner, DINA for the class")
arrow(7.68, 2.26, 8.32, 2.26)
arrow(11.76, 1.82, 11.76, 1.2)
box(8, 0.85, 10.24, 0.7, "Dashboard (built) of attainment by reasoning, knowledge and quality", kind="user", tsize=16)

# legend
for k, (lab, kind) in enumerate([("built", "built"), ("planned", "plan")]):
    y = 1.05 - k * 0.42
    ax.add_patch(FancyBboxPatch((13.5, y - 0.13), 0.5, 0.26, boxstyle="round,pad=0,rounding_size=0.05",
                                fc=TEAL_L if kind == "built" else AMBER_L, ec=TEAL if kind == "built" else AMBER,
                                lw=2, ls="-" if kind == "built" else "--"))
    ax.text(14.15, y, lab, fontsize=13, va="center", color=INK)

fig.savefig(OUT, dpi=200)
print("ok")
