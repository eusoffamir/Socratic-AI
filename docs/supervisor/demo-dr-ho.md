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

Open Knowledge in the sidebar and go through the three tabs.

Say "This is how the knowledge fits. From books is the knowledge graph with a quote behind each idea. Rules of thumb is an expert's decision tree, which is deductive. From data is a small Bayesian network learned from data, which is inductive, and asking it for a cause is abductive."

### 3. Diagnosis page, the main new part (5 minutes)

Open Diagnosis in the sidebar and use machine L47230.

Say "This is a first working version of the industrial use case, on open data while we wait for the partner's data. A milling machine has failed. The system ranks every possible fault, and it suggests the check that tells us the most."

Click the suggested check, then the next one.

Say "After two checks it is sure it is a power failure. It walks the causes backward to find the best explanation, which is abductive. Then it applies the published rule and gives the fix, which is deductive. And all the chances were learned from seven thousand past runs, which is inductive. The agent only writes the explanation at the end. The numbers come from the network, because an algorithm can do that part."

Then pick machine L49739 to show an honest hard case.

Say "Here no reading explains the failure, so after all six checks the best answer left is a random failure. The system does not pretend to know more than the data shows."

Point to the result line.

Say "On the 114 failed machines in the test set, the network named the right fault every time when it had all the readings."

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
