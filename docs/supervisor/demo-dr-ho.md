# Demo for Dr Ho (after Meeting 3)

About 15 minutes of demo, 5 minutes on the papers, then questions. Written 27 November 2026, updated the same day for RootAI and the new pages.

The story to tell is simple. First we teach reasoning, then we measure it, then we store knowledge as a graph so the reasoning can walk it, and now the same engine finds faults in machines.

## Before the meeting

1. The night before, make one good chat on a topic close to Dr Ho, for example "Generative AI for data analysis" or his Intro to AI slides as a file. Answer 4 or 5 rounds properly, so the level goes up and the chat has a full map. In the demo, open this chat from Recents instead of making a new topic live.
2. Avoid unclear topics live. Some topics first ask which meaning you want, and the choices can be odd.
3. Record a short screen video of the whole flow as a backup, in case the wifi or Gemini fails.
4. Open https://socratic-ai-qlk6.onrender.com about 5 minutes before, so the server is awake, and press Ctrl+Shift+R so the RootAI logo shows.
5. Open /api/health and check it says ok. Open /api/config and check ai_guard is true.
6. Open the Diagnosis page once, so the network is already learned (the first load takes a few seconds).
7. Have these open in tabs, the knowledge graph review (thesis section 2.8 or `docs/thesis/kg-generation-review.md`), the relation classes doc, the Ex problem statement, the teaching study plan and the AI4I results.
8. If you forget what a page does, press the question mark at the bottom of the sidebar. It walks through the page that is open, and Dr Ho can see it too.

## What to show and what to say

### 1. The start page and the name (1 minute)

Point to the logo and the name in the sidebar.

Say "The tool now does more than Socratic tutoring, so we call it RootAI, reasoning that finds the root. The sidebar has two groups. New chat and Overall status are for students, the chat teaches and Overall status measures. Below the line, Knowledge and Diagnosis are for engineers, so they show what RootAI knows about a machine and use it to find a fault."

### 2. The tutor (3 minutes)

Open your prepared chat from Recents.

Say "Any topic can go in here. The Topic Builder turns it into short cases, and the tutor never gives the answer. It asks questions up Paul's six levels, from clarify to question the question."

Answer one more question live. Pick A or B and give a short reason.

Say "After each answer, the Assessor scores it on Paul and Elder's nine standards and marks which reasoning I used, inductive, deductive or abductive."

Tap the bar at the top of the chat to open the progress panel.

Say "Here is the level I reached, the nine standards as a radar, and the Coach, who comments after a few answers."

### 3. Overall status (1 minute)

Open Overall status in the sidebar.

Say "This adds up every chat and skill check. Summary says it in plain words, and Full data shows the bars and grids we use for the study. The skill check is three short questions, one for each kind of reasoning, and a skill only counts as mastered after three or more answers on it, so it builds up over a few checks."

### 4. Knowledge page (3 minutes)

Open Knowledge in the sidebar. It shows what RootAI knows about one milling machine from the open AI4I data, the same machine the Diagnosis page works on.

Say "From here on the user is an engineer, not a student. The same machine is stored in three ways, from a book, from an engineer and from data, and each way matches one kind of reasoning."

**From books.** Tap Overstrain.

Say "This is what the published source says. Each reading can cause a fault, and each fault has a fix. When I tap a fault, its links light up and the rule shows with its source, so nothing is made up."

**Rules of thumb.** Press No, then Yes.

Say "This is how an engineer checks a stopped machine, as a flowchart. Each answer lights the path until it reaches a fault and its fix. Following fixed rules like this is deductive reasoning. The checklist is our draft for now, and the Ex partner's inspectors would give us the real one."

**From data.** Set Tool wear to Old.

Say "This is the Bayesian network learned from 7,000 past runs, which is inductive. I say what I know about a stopped machine, and the chance of each fault changes, so it reasons back from the signs to the cause, which is abductive. Look, old tool wear makes overstrain the most likely, not tool wear failure. The arc on the left shows why, since the data learned that a worn tool usually carries high strain."

Then set Product type to L.

Say "Overstrain goes up again, because type L has the lowest strain limit. And the box at the bottom says the data found the same causes as the book, without being told them."

### 5. Diagnosis page, the main new part (5 minutes)

Open Diagnosis in the sidebar. Machine L47230 is picked already.

Say "This is a first working version of the industrial use case, on open data while we wait for the partner's data. This machine has stopped. The card is how RootAI reasons. On the left are the readings it can check, in the middle the faults they can cause, with their chances, and on the right the fix for each. The arrows are the causes, learned from seven thousand past runs. The dashed box is the reading it will check next, because that one tells the most."

Press Find the cause, and talk while it runs.

Say "Strain is low, so overstrain drops. Power is low, and the link from power to power failure lights up. One fault is now at 99 percent, so it stops."

Point to the result card.

Say "It found power failure after checking 2 of the 6 readings, it gives the fix, and the expert rule agrees. It walked from the failure back to its cause, which is abductive. It applied the published rule, which is deductive. And the chances were learned from data, which is inductive. The agent only writes the explanation behind Why. The numbers come from the network, because an algorithm can do that part."

Point to the line at the bottom.

Say "This is not one lucky machine. On all 114 failed test machines it found the right cause 98 percent of the time, checking about 2 of the 6 readings on average."

If there is time, pick machine L49739 and press Find the cause again. Say "Here every check rules a fault out, until the best answer left is a random failure, and that is right."

**Your own machine.** Open the machine menu and pick Your own machine at the bottom. Press L, then type air 300, process 308, speed 1300 and torque 40, and press Find the cause.

Say "An engineer can type in their own machine. They leave out any reading they do not have, and RootAI works out the gap, the power and the strain from the rest. Here it finds heat dissipation at 96 percent and checks the expert rule on the numbers. Nobody knows the real answer for a new machine, so it does not claim one."

### 6. Knowledge graph review (2 minutes)

Open the review. This was the main task from the last meeting, so give it time.

Say "We looked at twelve families of methods for building a knowledge graph. For each one we asked how it chooses the nodes, how many nodes it makes, and how it chooses the edges and their types. The main finding is that methods with a fixed list of relation types give graphs we can check and join, while open methods give many names for the same link. And from the open data test, choosing the right nodes mattered more than anything else, because the same method went from 82 percent to 100 percent just by using the variables an engineer would choose."

Then ask "Which of these methods do you think fits the inspection case best?"

### 7. Fusing the three graphs (1 minute)

Say "Task seven was to fuse the three kinds of graph. Each topic has all three, the map from books, the expert rules and the network from data. On the Diagnosis page they now work together. The graph says which reading can cause which fault, the network ranks the faults and picks the next check, and at the end the expert rule is tested on the real numbers. On all 114 failed test machines the rule agreed with a real fault. What we do not have yet is one single fused graph that the agents walk. How do you picture that?"

### 8. Relation classes (1 minute)

Open the relation classes doc.

Say "For task five, we drafted eleven standard relation classes. We kept our seven and added part of, prevents, rules out and fixed by, because each one answers a question in debugging. The Diagnosis page already uses causes, tests and fixed by. We would like your view before we change the graph prompt."

### 9. The Ex problem statement (1 minute)

Open the Ex problem statement.

Say "You said that for the FYP it is enough to state the problem and its impact clearly. This is our draft. The problem is not finding defects but ranking them by safety impact, so the most dangerous ones are fixed first. It joins a hazard graph with a graph of the plant, and we think it needs one more relation, located in, to link them. We also wrote down what we need from the partner."

### 10. Teaching study (1 minute)

Open the teaching study plan.

Say "For the backup paper, we planned a pretest and posttest study with matched groups. We suggest a pilot with your master students and the main study with a foundation cohort. To show a medium effect we need about fifty students in each group. We need your advice on ethics approval."

## Questions to ask Dr Ho

The full list, including older questions, is in `questions-for-dr-ho.md`.

1. Is the Diagnosis page the right shape for the inspection use case? What should change before we show it to the partner or the startup contacts?
2. Are the eleven relation classes right, and is anything missing that inspection engineers use?
3. Which cohort and topic for the teaching study, and how does ethics approval work at UTP?
4. Is the Azure access ready, so we can test the agents on it?
5. Is the name RootAI fine with you? The thesis keeps its title.
6. Which graph-building method from the review fits the inspection case, and how do you picture fusing the three graphs?
7. Is the Ex problem statement right? Can the partner share past inspection records with outcomes, not only photos, and who can check the hazard graph?
8. Can you share one deck of your IML training slides, so we can try loading slides and check that the tool asks deeper questions, not just summaries?
9. When can we meet? You are away until about 6 December, and my exams start around 7 December.

## Things to say honestly if asked

- The AI4I data is synthetic, so it is cleaner than real plant data. Its value is that the true causes are published, so we can check the method.
- The fixes on the Diagnosis page are plain engineering sense, not from a standard, and are marked as a draft.
- For a new topic, the chances on From data are AI guesses, not counted from data.
- The Reasoning agent has not been checked against a human marker yet. The marking sheet is ready.
- The RootAI name has not been checked with SSM or MyIPO yet.
