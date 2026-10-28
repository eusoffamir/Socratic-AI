"""Figures made after Dr Ho's defence feedback (28 October 2026).

The literature review slides were tables, and critical thinking was not explained
clearly, so these pictures replace them. Run: python figs_feedback.py figures
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle

out = sys.argv[1]
TEAL, TEAL_L, GREY, GREY_L, AMBER, AMBER_L, INK = "#07517A", "#DCEAF2", "#475569", "#E8ECF0", "#8A6D1F", "#F3EEDC", "#0f172a"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})


def rbox(ax, x, y, w, h, fc, ec, lw=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=fc, ec=ec, lw=lw))


def save(fig, name):
    fig.savefig(f"{out}/{name}.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------- A. Agentic building blocks and where each one lives ----------
fig, ax = plt.subplots(figsize=(12.2, 5.4))
ax.set_xlim(0, 12.2); ax.set_ylim(-0.45, 5.4); ax.axis("off")
ideas = [("Prompting", "2025", "instruction plus context", "[15]"),
         ("Chain of Thought", "2022", "think in steps first", "[16]"),
         ("ReAct", "2023", "reason, act, observe", "[17]"),
         ("Multi-agent systems", "2024", "MetaGPT, AgileCoder", "[20], [21]"),
         ("RAG", "2023", "answer from retrieved text", "[14], [18]"),
         ("Model Context Protocol", "2024", "standard tool access", "[19]")]
uses = [("Every agent", "structured JSON prompts", "ai"),
        ("Planner", "reasons before the next move", "ai"),
        ("Tutor", "runs a simulation, reads it, replies", "ai"),
        ("Assessor, Planner, Tutor, Checker", "one job each, joined in a graph", "ai"),
        ("Topic Builder", "Wikipedia or the learner's file now, knowledge graph RAG in FYP2", "plan"),
        ("Knowledge graph and learner records", "planned", "plan")]
ax.text(2.2, 5.15, "Idea from the literature", ha="center", fontsize=12, weight="bold", color=TEAL)
ax.text(9.0, 5.15, "Where it lives in our tutor", ha="center", fontsize=12, weight="bold", color=TEAL)
for k, ((name, year, idea, ref), (who, what, kind)) in enumerate(zip(ideas, uses)):
    y = 4.35 - k * 0.82
    rbox(ax, 0.1, y - 0.3, 4.2, 0.62, "white", TEAL)
    ax.text(0.3, y + 0.08, name, fontsize=11, weight="bold", color=INK, va="center")
    ax.text(0.3, y - 0.16, f"{idea}  {ref}", fontsize=8.6, color=GREY, va="center")
    ax.text(4.1, y + 0.08, year, fontsize=9, color=GREY, ha="right", va="center")
    fc, ec = (TEAL_L, TEAL) if kind == "ai" else (AMBER_L, AMBER)
    rbox(ax, 5.9, y - 0.3, 6.2, 0.62, fc, ec)
    ax.text(6.1, y + 0.08, who, fontsize=11, weight="bold", color=INK, va="center")
    ax.text(6.1, y - 0.16, what, fontsize=8.6, color=GREY, va="center")
    ax.annotate("", xy=(5.85, y), xytext=(4.35, y),
                arrowprops=dict(arrowstyle="-|>", color=TEAL if kind == "ai" else AMBER, lw=1.6,
                                ls="-" if kind == "ai" else "--"))
ax.add_patch(FancyBboxPatch((6.0, -0.42), 0.3, 0.18, boxstyle="round,pad=0,rounding_size=0.04", fc=TEAL_L, ec=TEAL))
ax.text(6.4, -0.33, "built", fontsize=9, va="center", color=GREY)
ax.add_patch(FancyBboxPatch((7.3, -0.42), 0.3, 0.18, boxstyle="round,pad=0,rounding_size=0.04", fc=AMBER_L, ec=AMBER))
ax.text(7.7, -0.33, "planned or partly built", fontsize=9, va="center", color=GREY)
save(fig, "lit_agentic")


# ---------- B. What the tutor asks and what the Assessor marks ----------
fig, ax = plt.subplots(figsize=(12.2, 5.6))
ax.set_xlim(0, 12.2); ax.set_ylim(0, 5.6); ax.axis("off")
ax.text(0.1, 5.38, 'Learner says  "The circuit overheats because the resistor is too small."',
        fontsize=11.5, color=INK, style="italic", va="center")
ax.text(3.6, 4.95, "6 levels, what the Tutor asks next", ha="center", fontsize=12, weight="bold", color=TEAL)
levels = [("Clarify", "What do you mean by too small?"),
          ("Assumptions", "What are you assuming about it?"),
          ("Evidence", "How could you check it is the resistor?"),
          ("Viewpoints", "What else could make it overheat?"),
          ("Implications", "If you swap it, what else changes?"),
          ("Question the question", "Is overheating the real problem?")]
for k, (lv, q) in enumerate(levels):
    y = 0.35 + k * 0.72          # level 1 at the bottom, so it reads as a ladder
    x = 0.25 + k * 0.12
    shade = 0.25 + 0.75 * k / 5
    rbox(ax, x, y, 6.75, 0.58, TEAL_L if k < 5 else AMBER_L, TEAL if k < 5 else AMBER)
    ax.add_patch(Circle((x + 0.32, y + 0.29), 0.2, fc=TEAL if k < 5 else AMBER, ec="none"))
    ax.text(x + 0.32, y + 0.29, str(k + 1), ha="center", va="center", color="white", weight="bold", fontsize=10)
    ax.text(x + 0.65, y + 0.29, lv, fontsize=10.5, weight="bold", color=INK, va="center")
    ax.text(4.05, y + 0.29, q, fontsize=8.6, color=GREY, va="center")
ax.annotate("", xy=(0.02, 4.55), xytext=(0.02, 0.4), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.2))
ax.text(9.85, 4.95, "9 standards, what the Assessor marks", ha="center", fontsize=12, weight="bold", color=TEAL)
stds = [("Clarity", "Can you give\nan example?"), ("Accuracy", "Is that true?"), ("Precision", "Can you be\nmore exact?"),
        ("Relevance", "How does\nit relate?"), ("Depth", "What makes\nit hard?"), ("Breadth", "Is there\nanother view?"),
        ("Logic", "Does it follow?"), ("Significance", "Is it the\nkey point?"), ("Fairness", "Is it fair to\nother views?")]
for k, (s, q) in enumerate(stds):
    col, row = k % 3, k // 3
    x, y = 7.65 + col * 1.5, 3.7 - row * 1.25
    rbox(ax, x, y, 1.42, 1.05, "white", TEAL)
    ax.text(x + 0.71, y + 0.72, s, ha="center", fontsize=10, weight="bold", color=INK)
    ax.text(x + 0.71, y + 0.33, q, ha="center", va="center", fontsize=8.2, color=GREY)
ax.text(9.85, 0.0, "Each standard is marked 1 (met) or 0 (not met), with evidence from the answer",
        ha="center", fontsize=9, color=GREY, style="italic")
save(fig, "ct_ladder")


# ---------- C. Types of reasoning and types of knowledge ----------
fig, ax = plt.subplots(figsize=(12.2, 5.6))
ax.set_xlim(0, 12.2); ax.set_ylim(0, 5.6); ax.axis("off")
ax.text(3.0, 5.35, "3 types of reasoning", ha="center", fontsize=12, weight="bold", color=TEAL)
reas = [("Inductive", "many cases, then a general idea",
         "Every board from this batch overheats,\nso the batch may share a fault."),
        ("Deductive", "a rule, then a sure conclusion",
         "The resistor is rated 0.25 W but takes 0.5 W,\nso it will overheat."),
        ("Abductive", "what was seen, then the best explanation",
         "It only overheats after an hour, so heat\nbuilding up slowly is the likely cause.")]
for k, (name, how, ex) in enumerate(reas):
    y = 3.75 - k * 1.65
    rbox(ax, 0.1, y, 5.8, 1.45, TEAL_L, TEAL)
    ax.text(0.3, y + 1.15, name, fontsize=11.5, weight="bold", color=INK, va="center")
    ax.text(2.0, y + 1.15, how, fontsize=9.2, color=TEAL, va="center", style="italic")
    ax.text(0.3, y + 0.5, ex, fontsize=9.5, color=GREY, va="center")
ax.text(9.15, 5.35, "8 types of knowledge, and the question each answers", ha="center", fontsize=12, weight="bold", color=TEAL)
know = [("Factual", "What is true?"), ("Conceptual", "What does it mean?"), ("Procedural", "How do I do it?"),
        ("Causal", "Why does it happen?"), ("Relational", "How are things connected?"),
        ("Strategic", "What should I do here?"), ("Metacognitive", "How do I know, how sure am I?"),
        ("Epistemic", "What is it fair to believe?")]
for k, (name, q) in enumerate(know):
    col, row = k % 2, k // 2
    x, y = 6.35 + col * 2.95, 4.2 - row * 1.12
    doing = k >= 5
    rbox(ax, x, y, 2.8, 0.95, AMBER_L if doing else "white", AMBER if doing else TEAL)
    ax.text(x + 0.18, y + 0.64, name, fontsize=10.5, weight="bold", color=INK, va="center")
    ax.text(x + 0.18, y + 0.28, q, fontsize=8.8, color=GREY, va="center")
ax.text(6.4, -0.05, "White boxes are knowing.  Gold boxes lead to a decision or a judgement.",
        fontsize=9, color=GREY, style="italic")
save(fig, "ct_types")


# ---------- D. Past studies on a timeline ----------
fig, ax = plt.subplots(figsize=(12.2, 4.9))
ax.set_xlim(2014.6, 2027.3); ax.set_ylim(-3.05, 2.65); ax.axis("off")
ax.plot([2015, 2026], [0, 0], color=GREY, lw=2)
for yr in (2016, 2019, 2023, 2025):
    ax.text(yr, -0.32, str(yr), ha="center", fontsize=10, color=GREY, weight="bold")
studies = [  # year, x offset, height, name, finding, limit, kind
    (2016, 0, 1.25, "Sahamid [4]", "Socratic questions built\ncritical thinking in class", "small, one class", "human"),
    (2019, 0, -1.3, "Makhene [5]", "Socratic inquiry helps\nnursing students", "needs skilled teachers", "human"),
    (2023, -0.35, 1.25, "Ho, Chen and Li [6]", "Socratic method improved\nhealthcare students' thinking", "needs a human tutor", "human"),
    (2025, -1.6, -1.3, "Lee et al. [10]", "more trust in AI,\nless critical thinking", "self-reported", "risk"),
    (2025, 0.9, 1.25, "Degen and Asanov [7]", "Socratic AI beat a plain\nchatbot for reflection", "self-reported", "ai"),
    (2025, 0.95, -1.3, "Fan [8]; Lee, Ang, Lai [9]", "AI scaffolding deepens inquiry,\nlogs show thinking", "no reasoning types", "ai")]
col = {"human": TEAL, "ai": AMBER, "risk": "#9B2C2C"}
for yr, dx, h, name, find, lim, kind in studies:
    x = yr + dx
    ax.plot([yr, x], [0, h * 0.25], color=col[kind], lw=1) if dx else None
    ax.plot([x, x], [h * 0.25 if dx else 0, h], color=col[kind], lw=1.2)
    ax.add_patch(Circle((yr, 0), 0.09, fc=col[kind], ec="white", lw=1, zorder=3))
    top = h > 0
    bx, by, bw, bh = x - 1.2, (h if top else h - 1.3), 2.4, 1.3
    rbox(ax, bx, by, bw, bh, "white", col[kind])
    ax.text(x, by + bh - 0.22, name, ha="center", fontsize=9.6, weight="bold", color=INK)
    ax.text(x, by + 0.68, find, ha="center", va="center", fontsize=8.4, color=GREY)
    ax.text(x, by + 0.17, "limit, " + lim, ha="center", fontsize=7.8, color=col[kind], style="italic")
for k, (lab, kind) in enumerate((("Human Socratic tutor", "human"), ("Socratic AI", "ai"), ("Risk of AI", "risk"))):
    ax.add_patch(Circle((2015.0 + k * 2.3, -2.92), 0.08, fc=col[kind], ec="none"))
    ax.text(2015.15 + k * 2.3, -2.92, lab, fontsize=9, va="center", color=GREY)
save(fig, "lit_studies")


# ---------- E. Existing tutors against what we need ----------
fig, ax = plt.subplots(figsize=(12.2, 4.4))
ax.set_xlim(0, 12.2); ax.set_ylim(0, 4.4); ax.axis("off")
cols = ["Refuses\nanswers", "Question\nladder", "Framework\nmarks", "Goal, progress,\nend", "Reasoning and\nknowledge types"]
tools = [("Gemini Gem Socratic Tutor (Test #1)", [2, 0, 0, 0, 0]),
         ("Our first prompt v1 (Test #2)", [2, 1, 1, 0, 0]),
         ("Khanmigo, custom GPTs *", [2, -1, -1, 1, 0]),
         ("Socratic AI (this project)", [2, 2, 2, 2, 2])]
for j, c in enumerate(cols):
    ax.text(5.1 + j * 1.55, 4.05, c, ha="center", va="center", fontsize=9.6, weight="bold", color=TEAL)
for i, (name, vals) in enumerate(tools):
    y = 3.1 - i * 0.82
    ours = i == 3
    if ours:
        rbox(ax, 0.05, y - 0.36, 12.0, 0.72, AMBER_L, AMBER)
    ax.text(0.25, y, name, fontsize=10.5, weight="bold" if ours else "normal", color=INK, va="center")
    for j, v in enumerate(vals):
        x = 5.1 + j * 1.55
        if v == 2:
            ax.add_patch(Circle((x, y), 0.2, fc=TEAL, ec=TEAL))
        elif v == 1:
            ax.add_patch(Circle((x, y), 0.2, fc="white", ec=TEAL, lw=1.6))
            ax.add_patch(matplotlib.patches.Wedge((x, y), 0.2, 90, 270, fc=TEAL, ec=TEAL))
        elif v == 0:
            ax.add_patch(Circle((x, y), 0.2, fc="white", ec=GREY, lw=1.4))
        else:
            ax.text(x, y, "?", ha="center", va="center", fontsize=13, color=GREY)
leg = [(2, "yes"), (1, "partly"), (0, "no"), (-1, "not shown")]
for k, (v, lab) in enumerate(leg):
    x = 0.4 + k * 1.6
    if v == 2:
        ax.add_patch(Circle((x, 0.12), 0.11, fc=TEAL, ec=TEAL))
    elif v == 1:
        ax.add_patch(Circle((x, 0.12), 0.11, fc="white", ec=TEAL, lw=1.4))
        ax.add_patch(matplotlib.patches.Wedge((x, 0.12), 0.11, 90, 270, fc=TEAL, ec=TEAL))
    elif v == 0:
        ax.add_patch(Circle((x, 0.12), 0.11, fc="white", ec=GREY, lw=1.2))
    else:
        ax.text(x, 0.12, "?", ha="center", va="center", fontsize=11, color=GREY)
    ax.text(x + 0.2, 0.12, lab, fontsize=9, va="center", color=GREY)
ax.text(12.1, 0.12, "* from public descriptions, not tested by us", ha="right", fontsize=8.6, color=GREY, style="italic")
ax.set_aspect("equal")
save(fig, "lit_tools")
print("figures done")
