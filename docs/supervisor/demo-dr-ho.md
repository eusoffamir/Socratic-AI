# Demo for Dr Ho (after Meeting 3)

About 15 minutes of demo, then questions. Written 27 November 2026.

## Before the meeting

1. Open https://socratic-ai-qlk6.onrender.com about 5 minutes before, so the server is awake.
2. Open /api/health and check it says ok. Open /api/config and check ai_guard is true.
3. Open the Diagnosis page once, so the network is already learned (the first load takes a few seconds).
4. Have these open in tabs, the relation classes doc, the teaching study plan and the AI4I results.

## What to show and what to say

### 1. The tutor (3 minutes)

Start a New chat on a short topic.

Say "We start with the tutor. It never gives the answer. It asks questions up Paul's six levels, and after each answer the Assessor scores it on the nine standards and marks which reasoning the student used. Here you can see the level go up when the answer is good enough."

### 2. Knowledge page (3 minutes)

The idea to get across is that the same topic is stored three ways, and each way matches one kind of reasoning.

Open Knowledge in the sidebar. It shows the topic of your prepared chat.

**From books.** Tap one box.

Say "Each box is one idea, and each arrow says how two ideas link, like causes or supports. When I tap a box, it shows the Wikipedia quote it came from, so nothing is made up."

Open Show and pick Deductive reasoning.

Say "This lights up the path a student walks when they reason this way, so we can see their thinking as a walk on the graph."

**Rules of thumb.** Answer the questions with the buttons until it reaches a decision.

Say "This is how an expert decides. They ask a few questions in order and each answer leads to the next one, until there is a decision. Following fixed rules like this is deductive reasoning."

**From data.** Point to the diagram on top, then the chance bars below.

Say "This is a small Bayesian network. The top boxes are causes and the arrows show what they change. The chances underneath were counted from data, which is inductive. Asking it which cause is most likely, given what we saw, is abductive. This is the same engine the Diagnosis page uses."

### 3. Diagnosis page, the main new part (5 minutes)

Open Diagnosis in the sidebar. Machine L47230 is picked already.

Say "This is a first working version of the industrial use case, on open data while we wait for the partner's data. This machine has stopped. The bars show how likely each fault is before we check anything, and the buttons below are the checks we can do. The green one is the check that would tell us the most."

Click Strain on the tool.

Say "Strain is low, so overstrain failure becomes unlikely. That is the first row under What we checked."

Click Power.

Say "Power is low, and low power is a known cause of power failure, so it points straight there. Now one fault is at 99 percent, so it stops. It walked from the failure back to its cause, which is abductive. Then it applied the published rule and gave the fix, which is deductive. And all the chances were learned from seven thousand past runs, which is inductive. The agent only writes this explanation at the end. The numbers come from the network, because an algorithm can do that part."

Then pick machine L49739 from the menu and keep clicking the green check.

Say "Here every check rules one fault out, one by one. In the end no reading explains the failure, so the best answer left is a random failure, and that is right. The system does not pretend to know more than the data shows."

If asked how good it is, say "On the 114 failed machines in the test set, the network named the right fault every time when it had all the readings."

### 4. Relation classes (2 minutes)

Open the relation classes doc.

Say "For task five, we drafted eleven standard relation classes. We kept our seven and added part of, prevents, rules out and fixed by, because each one answers a question in debugging. The diagnosis page already uses them. We would like your view before we change the graph prompt."

### 5. Teaching study (2 minutes)

Open the teaching study plan.

Say "For the backup paper, we planned a pretest and posttest study with matched groups. We suggest a pilot with your master students and the main study with a foundation cohort. To show a medium effect we need about fifty students in each group. We need your advice on ethics approval."

## Questions to ask Dr Ho

1. Is the diagnosis page the right shape for the inspection use case? What should change before we show it to the partner or the startup contacts?
2. Are the eleven relation classes right, and is anything missing that inspection engineers use?
3. Which cohort and topic for the teaching study, and how does ethics approval work at UTP?
4. Is the Azure access ready, so we can test the agents on it?
5. The tool now does more than Socratic tutoring, so we renamed the app RootAI, meaning reasoning that finds the root. Is that name fine with you? (The thesis keeps its title.)

## Things to say honestly if asked

- The AI4I data is synthetic, so it is cleaner than real plant data. Its value is that the true causes are published, so we can check the method.
- The fixes on the diagnosis page are plain engineering sense, not from a standard, and are marked as a draft.
- The Reasoning agent has not been checked against a human marker yet. The marking sheet is ready.
