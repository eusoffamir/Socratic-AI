import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D

out = sys.argv[1]
TEAL, TEAL_L, GREY, GREY_L, AMBER, AMBER_L, INK = "#07517A", "#DCEAF2", "#475569", "#E8ECF0", "#8A6D1F", "#F3EEDC", "#0f172a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})


def box(ax, x, y, w, h, title, sub="", kind="ai", dashed=False, tsize=10.5):
    fc, ec = {"ai": (TEAL_L, TEAL), "code": (GREY_L, GREY), "plan": (AMBER_L, AMBER), "user": ("#ffffff", INK)}[kind]
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec, lw=1.6, ls="--" if dashed else "-"))
    ax.text(x, y + (0.13 if sub else 0), title, ha="center", va="center", fontsize=tsize, weight="bold", color=INK)
    if sub:
        ax.text(x, y - 0.18, sub, ha="center", va="center", fontsize=8, color=GREY)


def arrow(ax, x1, y1, x2, y2, label="", color=INK, ls="-"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3, ls=ls))
    if label:
        ax.text((x1 + x2) / 2 + 0.12, (y1 + y2) / 2, label, ha="left", va="center", fontsize=7.6, color=GREY, style="italic")


# ---------- Figure A: agent flow ----------
fig, ax = plt.subplots(figsize=(8.6, 10.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 12.2); ax.axis("off")
X, W, H = 3.6, 4.0, 0.72
steps = [
    (11.4, "Learner answer", "typed in the chat, or A or B", "user"),
    (10.2, "Copy check (code)", "copied from a hint? then 0, no AI call", "code"),
    (9.0, "Assessor agent", "marks the answer against the 9 standards", "ai"),
    (7.8, "Planner agent", "proposes the next move", "ai"),
    (6.6, "Rules / guard (code)", "check the plan and fix it if needed", "code"),
    (5.4, "Tutor agent", "may run the simulation, then writes the reply", "ai"),
    (4.2, "Free code checks", "word limits, one question, options, repeats", "code"),
    (3.0, "Checker agent", "answer given away? fits the level? repeat?", "ai"),
    (1.8, "Reply to the learner", "feedback, hidden key idea, one question", "user"),
]
for y, t, s, k in steps:
    box(ax, X, y, W, H, t, s, k)
labels = ["answer + question", "not copied", "9 standards (1 or 0),\nmove, flags, evidence",
          "plan: level, format,\nhint, simulation", "instruction: level, format, hint",
          "draft reply (JSON)", "passed", "ok, or a list of problems"]
for (y1, *_), (y2, *_), lab in zip(steps, steps[1:], labels):
    arrow(ax, X, y1 - H / 2, X, y2 + H / 2, lab)
ax.annotate("", xy=(X - W / 2, 5.4), xytext=(X - W / 2, 3.0),
            arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.3, connectionstyle="arc3,rad=-0.55"))
ax.text(0.45, 4.2, "problem found,\nso the Tutor\nrewrites once", ha="center", va="center", fontsize=7.8, color=AMBER, weight="bold")
box(ax, 8.1, 5.4, 2.6, 0.72, "Simulation tool", "seeded Python, chart", "code")
arrow(ax, X + W / 2, 5.5, 8.1 - 1.3, 5.5)
arrow(ax, 8.1 - 1.3, 5.3, X + W / 2, 5.3)
box(ax, 8.1, 9.0, 2.6, 0.9, "Session state", "saved every turn\n(Supabase database)", "code")
ax.plot([X + W / 2, 8.1 - 1.3], [9.0, 9.0], color=GREY, lw=1, ls=":")
box(ax, 8.1, 1.8, 2.6, 0.8, "Coach agent", "end of session only,\none comment", "ai")
arrow(ax, X + W / 2, 1.8, 8.1 - 1.3, 1.8)
box(ax, 8.1, 7.6, 2.6, 0.8, "Reasoning agent", "planned: reasoning type\nand knowledge used", "plan", dashed=True)
box(ax, 8.1, 3.3, 2.6, 0.8, "Explainer agent", "planned: why this\nskill matters", "plan", dashed=True)
arrow(ax, X + W / 2, 8.8, 8.1 - 1.3, 7.6, color=AMBER, ls="--")
for i, (k, lab) in enumerate([("ai", "AI agent (Gemini)"), ("code", "plain code, no AI"), ("plan", "planned for Goal 1")]):
    box(ax, 1.5 + i * 3.1, 0.5, 2.7, 0.42, lab, "", k, dashed=(k == "plan"), tsize=9)
fig.savefig(f"{out}/agent_flow.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure B: framework ----------
fig, ax = plt.subplots(figsize=(9.6, 6.4))
ax.set_xlim(0, 12.4); ax.set_ylim(0, 8.4); ax.axis("off")
cols = [
    (1.55, "1. Prerequisites", "8 elements of thought", ["Purpose", "Question at issue", "Information"], "plan"),
    (4.6, "2. Reasoning", "modes of reasoning", ["Inductive", "Deductive", "Abductive", "later: analogic,", "counterfactual"], "plan"),
    (7.65, "3. Knowledge", "types of knowledge used", ["Factual", "Conceptual", "Procedural", "Causal", "Relational",
                                                        "later: strategic,", "metacognitive, epistemic"], "plan"),
    (10.75, "4. Quality", "Paul-Elder standards", ["Clarity, accuracy,", "precision, relevance,", "depth, breadth, logic,",
                                                   "significance, fairness", "(built)"], "ai"),
]
for x, t, s, items, k in cols:
    box(ax, x, 7.55, 2.8, 0.9, t, s, k, dashed=(k == "plan"))
    for i, it in enumerate(items):
        grey = it.startswith(("later", "metacog", "counterf", "(built)"))
        ax.text(x, 6.75 - i * 0.36, it, ha="center", va="center", fontsize=8.6, color=GREY if grey else INK)
for x1, x2 in [(2.95, 3.2), (6.0, 6.25), (9.05, 9.35)]:
    arrow(ax, x1, 7.55, x2, 7.55)
box(ax, 6.2, 3.1, 11.6, 0.9, "Paul's 6 Socratic question levels (built), the ladder the Tutor climbs",
    "clarify, assumptions, evidence, viewpoints, implications, question the question", "ai")
box(ax, 3.2, 1.6, 5.4, 0.95, "5. Complexity (planned)", "SOLO levels: how many knowledge types are combined", "plan", dashed=True)
box(ax, 9.2, 1.6, 5.8, 0.95, "6. Statistics over many trials (planned)", "1 or 0 per element, Hamming distance, factor analysis", "plan", dashed=True)
box(ax, 6.2, 0.35, 8.6, 0.6,"Dashboard: attainment by reasoning, knowledge and quality", "", "user", tsize=9.5)
arrow(ax, 3.2, 1.12, 5.0, 0.63)
arrow(ax, 9.2, 1.12, 7.4, 0.63)
fig.savefig(f"{out}/framework.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---------- Figure C: Gantt ----------
months = ["Sep 26", "Oct 26", "Nov 26", "Dec 26", "Jan 27", "Feb 27", "Mar 27", "Apr 27"]
tasks = [
    ("Topic, literature review, Gem tests", 0.0, 1.3, "done"),
    ("Design requirements R1 to R9", 0.6, 0.7, "done"),
    ("Build and deploy prototype (4 agents)", 0.9, 1.0, "done"),
    ("Proposal defence (21 Oct)", 1.66, 0.0, "mile"),
    ("Goal 1: reasoning and knowledge layer", 1.7, 0.85, "plan"),
    ("Mock presentation and product demo", 2.45, 0.0, "mile"),
    ("Interim report", 2.0, 1.5, "plan"),
    ("Assessor vs human markers (kappa)", 3.6, 1.6, "plan"),
    ("Question bank and statistics", 4.0, 1.6, "plan"),
    ("Goal 2: a second topic", 5.0, 1.2, "plan"),
    ("Learner tests (with ethics approval)", 5.4, 1.4, "plan"),
    ("Dissertation and technical paper", 6.0, 2.0, "plan"),
]
fig, ax = plt.subplots(figsize=(9.6, 5.2))
for i, (lab, s, l, k) in enumerate(tasks):
    y = len(tasks) - 1 - i
    if k == "mile":
        ax.plot(s, y, marker="D", ms=10, color=AMBER, zorder=3)
    else:
        ax.barh(y, l, left=s, height=0.55, color=TEAL if k == "done" else TEAL_L, edgecolor=TEAL, lw=1.2)
ax.set_yticks(range(len(tasks))); ax.set_yticklabels([t[0] for t in tasks][::-1], fontsize=9)
ax.set_xticks([m + 0.5 for m in range(len(months))]); ax.set_xticklabels(months, fontsize=9)
ax.tick_params(axis="x", length=0)
ax.set_xlim(0, len(months)); ax.set_ylim(-0.7, len(tasks) + 0.2)
for m in range(1, len(months)):
    ax.axvline(m, color=GREY_L, lw=0.8, zorder=0)
ax.axvline(4, color=GREY, lw=1.4, ls="--")
ax.text(2.0, len(tasks) - 0.25, "FYP 1", ha="center", weight="bold", color=GREY)
ax.text(6.0, len(tasks) - 0.25, "FYP 2", ha="center", weight="bold", color=GREY)
ax.axvline(1.66, color=AMBER, lw=1, ls=":")
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
ax.legend(handles=[Patch(color=TEAL, label="done"), Patch(fc=TEAL_L, ec=TEAL, label="planned"),
                   Line2D([], [], marker="D", color=AMBER, ls="", label="milestone")],
          loc="lower left", fontsize=8.5, frameon=False)
fig.savefig(f"{out}/gantt.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("ok")
