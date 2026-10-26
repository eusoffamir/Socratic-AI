"""Week-by-week Gantt table for FYP 1 and FYP 2, in the style of the UTP example. Run: python gantt_weeks.py out.png"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, RegularPolygon

OUT = sys.argv[1]
NAVY, MAROON, GOLD, INK, GRID = "#1F3A5F", "#7A1F3D", "#F2B705", "#111827", "#B8C0CC"
DONE, PROG, TODO, BAR = "#A9C99B", "#F4B183", "#DCE6F2", "#8FAADC"
HEAD = "#3B2F4A"
plt.rcParams.update({"font.family": "DejaVu Sans"})

fyp1 = ["7 Sep", "14 Sep", "21 Sep", "28 Sep", "5 Oct", "12 Oct", "19 Oct", "26 Oct", "2 Nov", "9 Nov", "16 Nov", "23 Nov", "30 Nov", "7 Dec"]
fyp2 = ["11 Jan", "18 Jan", "25 Jan", "1 Feb", "8 Feb", "15 Feb", "22 Feb", "1 Mar", "8 Mar", "15 Mar", "22 Mar", "29 Mar", "5 Apr", "12 Apr"]
NOW = 7  # FYP 1 week 7 (19 Oct): the proposal defence week

# (task, objectives, (sem, start week), (sem, end week), status, milestone week or None, bar colour)
tasks = [
    ("Literature review and research gap", "", (1, 1), (1, 6), "Done", None),
    ("Gem tests and design requirements", "", (1, 2), (1, 4), "Done", None),
    ("Build and deploy the prototype", "O1, O3", (1, 3), (1, 6), "Done", None),
    ("Proposal defence", "", (1, 5), (1, 7), "In progress", (1, 7)),
    ("Reasoning and knowledge layer (Goal 1)", "O2, O3", (1, 7), (1, 7), "Done", None),
    ("Any topic with a Topic Builder (Goal 2)", "O1", (1, 7), (1, 7), "Done", None),
    ("Trees and Bayesian networks (Goal 3)", "O1, O2", (1, 7), (1, 7), "Done", None),
    ("Mock presentation and product demo", "", (1, 10), (1, 11), "Not started", (1, 11)),
    ("Interim report", "", (1, 10), (1, 14), "Not started", (1, 14)),
    ("Assessor vs human markers (kappa)", "O2", (2, 1), (2, 5), "Not started", None),
    ("Bigger question bank, check thresholds", "O2, O3", (2, 2), (2, 7), "Not started", None),
    ("Learner tests (with ethics approval)", "O1, O2, O3", (2, 7), (2, 11), "Not started", None),
    ("Technical paper", "", (2, 10), (2, 12), "Not started", (2, 12)),
    ("Dissertation and final presentation", "", (2, 10), (2, 14), "Not started", (2, 14)),
]

# column layout (in arbitrary units)
cols = [("No", 0.55), ("Task", 5.0), ("Obj.", 1.4), ("Start", 1.45), ("End", 1.45), ("Status", 1.6)]
WK = 0.55
GAP = 0.25
x0s, x = [], 0
for _, w in cols:
    x0s.append(x); x += w
weeks_x = x
fyp2_x = weeks_x + 14 * WK + GAP
total_w = fyp2_x + 14 * WK
ROW, H1, H2, H3 = 0.55, 0.45, 0.45, 1.0
n = len(tasks)
total_h = H1 + H2 + H3 + n * ROW

fig, ax = plt.subplots(figsize=(total_w * 0.72, total_h * 0.72))
ax.set_xlim(0, total_w); ax.set_ylim(total_h, 0); ax.axis("off")

def box(x, y, w, h, fc, ec=GRID, lw=0.8):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=lw))

def txt(x, y, s, size=9, color=INK, weight="normal", ha="center", rot=0):
    ax.text(x, y, s, fontsize=size, color=color, weight=weight, ha=ha, va="center", rotation=rot)

# left header block
for (name, w), x in zip(cols, x0s):
    box(x, 0, w, H1 + H2 + H3, HEAD, "white")
    txt(x + w / 2, (H1 + H2 + H3) / 2, name, 9.5, "white", "bold")

# semester headers, week numbers, dates
for sem, base, colr, dates in [(1, weeks_x, NAVY, fyp1), (2, fyp2_x, MAROON, fyp2)]:
    box(base, 0, 14 * WK, H1, colr, "white")
    txt(base + 7 * WK, H1 / 2, f"FYP {sem}   (Semester {sem})", 10, "white", "bold")
    for k in range(14):
        xx = base + k * WK
        now = sem == 1 and k + 1 == NOW
        box(xx, H1, WK, H2, GOLD if now else colr, "white")
        txt(xx + WK / 2, H1 + H2 / 2, f"W{k + 1}", 7, INK if now else "white", "bold")
        box(xx, H1 + H2, WK, H3, GOLD if now else "white")
        txt(xx + WK / 2, H1 + H2 + H3 / 2, dates[k], 6.8, INK, "bold" if now else "normal", rot=90)

# task rows
status_col = {"Done": DONE, "In progress": PROG, "Not started": TODO}
for i, (name, obj, (s1, w1), (s2, w2), status, ms) in enumerate(tasks):
    y = H1 + H2 + H3 + i * ROW
    vals = [str(i + 1), name, obj, f"FYP{s1} W{w1}", f"FYP{s2} W{w2}", status]
    for j, ((_, w), x) in enumerate(zip(cols, x0s)):
        box(x, y, w, ROW, status_col[status] if j == 5 else "white")
        txt(x + (0.12 if j == 1 else w / 2), y + ROW / 2, vals[j], 8.2, ha="left" if j == 1 else "center")
    for base in (weeks_x, fyp2_x):
        for k in range(14):
            box(base + k * WK, y, WK, ROW, "white")
    # bar
    def wx(sem, w):
        return (weeks_x if sem == 1 else fyp2_x) + (w - 1) * WK
    fill = {"Done": DONE, "In progress": PROG}.get(status, BAR)
    for sem in (1, 2):
        if s1 <= sem <= s2:
            a = w1 if sem == s1 else 1
            b = w2 if sem == s2 else 14
            box(wx(sem, a), y + 0.04, (b - a + 1) * WK, ROW - 0.08, fill, "white", 0.6)
    if ms:
        ax.add_patch(RegularPolygon((wx(*ms) + WK / 2, y + ROW / 2), 4, radius=0.13, facecolor="#C00000", edgecolor="#C00000"))

# outer frame
box(0, 0, weeks_x + 14 * WK, total_h, "none", INK, 1.2)
box(fyp2_x, 0, 14 * WK, total_h, "none", INK, 1.2)
# legend
ly = total_h + 0.35
for k, (lab, c) in enumerate([("Done", DONE), ("In progress", PROG), ("Planned", BAR)]):
    box(0.2 + k * 2.3, ly - 0.14, 0.45, 0.28, c, "white"); txt(0.8 + k * 2.3, ly, lab, 8.5, ha="left")
ax.add_patch(RegularPolygon((7.6, ly), 4, radius=0.13, facecolor="#C00000")); txt(7.85, ly, "Milestone", 8.5, ha="left")
box(10.3, ly - 0.14, 0.45, 0.28, GOLD, "white"); txt(10.9, ly, "Current week (19 Oct)", 8.5, ha="left")
txt(total_w, ly, "O1 to O3 are the three objectives (teach, assess, adapt)", 8.5, ha="right")
ax.set_ylim(total_h + 0.65, 0)
fig.savefig(OUT, dpi=220, bbox_inches="tight")
print("ok")
