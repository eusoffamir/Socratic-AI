# Demo for Dr Ho (after Meeting 3)

About 15 minutes of demo, then questions. Written 27 November 2026, updated the same day for RootAI and the new pages.

The story to tell is simple. First we teach reasoning, then we measure it, then we store knowledge as a graph so the reasoning can walk it, and now the same engine finds faults in machines.

## Before the meeting

1. The night before, make one good chat on a topic close to Dr Ho, for example "Generative AI for data analysis" or his Intro to AI slides as a file. Answer 4 or 5 rounds properly, so the level goes up and the Knowledge page has a full map. In the demo, open this chat from Recents instead of making a new topic live.
2. Avoid unclear topics live. Some topics first ask which meaning you want, and the choices can be odd.
3. Record a short screen video of the whole flow as a backup, in case the wifi or Gemini fails.
4. Open https://socratic-ai-qlk6.onrender.com about 5 minutes before, so the server is awake, and press Ctrl+Shift+R so the RootAI logo shows.
5. Open /api/health and check it says ok. Open /api/config and check ai_guard is true.
6. Open the Diagnosis page once, so the network is already learned (the first load takes a few seconds).
7. Have these open in tabs, the relation classes doc, the teaching study plan and the AI4I results.
8. If you forget what a page does, press the question mark at the bottom of the sidebar. It walks through the page that is open, and Dr Ho can see it too.

## What to show and what to say

### 1. The start page and the name (1 minute)

Point to the logo and the name in the sidebar.

Say "The tool now does more than Socratic tutoring, so we call it RootAI, reasoning that finds the root. It has four parts in the sidebar. The chat teaches, Overall status measures, Knowledge shows how the ideas fit, and Diagnosis uses the same reasoning on machines."

### 2. The tutor (3 minutes)

Open your prepared chat from Recents.

Say "Any topic can go in here. The Topic Builder turns it into short cases, and the tutor never gives the answer. It asks questions up Paul's six levels, from clarify to question the question."

Answer one more question live. Pick A or B and give a short reason.

Say "After each answer, the Assessor scores it on Paul and Elder's nine standards and marks which reasoning I used, inductive, deductive or abductive."

Tap the bar at the top of the chat to open the progress panel.

Say "Here is the level I reached, the nine standards as a radar, and the Coach, who comments after a few answers."

### 3. Overall status (1 minute)

Open Overall status in the sidebar.

Say "This adds up every chat and skill check. Summary says it in plain words, and Full data shows the bars and grids we use for the study. The skill check is six questions, each tagged with one kind of reasoning, and a skill only counts as mastered after three or more answers on it."

### 4. Knowledge page (3 minutes)

Open Knowledge in the sidebar. It shows the cases from your chats, and the menu at the top switches between them.

Say "The same topic is stored in three ways, and each way matches one kind of reasoning."

**From books.** Tap one box.

Say "Each box is one idea, and each arrow says how two ideas link, like causes or supports. When I tap a box, it shows the Wikipedia quote it came from, so nothing is made up."

Open Show and pick Deductive reasoning.

Say "This lights up the path a student walks when they reason this way, so we can read their thinking as a walk on the graph."

**Rules of thumb.** Point to the list of possible decisions first, then answer the questions with the buttons.

Say "This is how an expert decides. These are the decisions they can reach. They ask a few questions in order, and each answer leads to the next, until one decision turns green. Following fixed rules like this is deductive reasoning."

**From data.** Point to the diagram on top, then the two groups of chances.

Say "This is a small Bayesian network. The top box is the cause and the arrows point to the signs it causes. The first group goes forward, from the cause to a sign, which is deductive. The second group goes backward, from the signs to the cause, which is abductive. For a new topic there is no data, so the AI guesses these chances, and the page says so. For the machines, the chances are counted from real records, and that is the next page."

### 5. Diagnosis page, the main new part (5 minutes)

Open Diagnosis in the sidebar. Machine L47230 is picked already.

Say "This is a first working version of the industrial use case, on open data while we wait for the partner's data. The page says the machine has stopped. What could have caused it shows the chance of each fault before we check anything. On the right, under Check next, the big green button is the reading that would tell us the most, and the smaller ones are the other readings we could take."

Click the big green button, Check strain on the tool.

Say "Strain is low, so under What we checked it says it makes overstrain failure unlikely. The line at the top now shows the best guess so far."

Click the big green button again, Check power.

Say "Power is low, and low power is a known cause of power failure, so it points straight there. One fault is now at 99 percent, so it stops and says Found it. It walked from the failure back to its cause, which is abductive. Then it applied the published rule and gave the fix, which is deductive. And all the chances were learned from seven thousand past runs, which is inductive. The agent only writes this explanation at the end. The numbers come from the network, because an algorithm can do that part. The last line checks the answer against what really happened."

Then pick machine L49739 from the menu and keep clicking the big green button.

Say "Here every check makes one fault unlikely, one by one. In the end no reading explains the failure, so the best answer left is a random failure, and that is right. The system does not pretend to know more than the data shows."

If asked how good it is, say "On the 114 failed machines in the test set, the network named the right fault every time when it had all the readings."

### 6. Relation classes (1 minute)

Open the relation classes doc.

Say "For task five, we drafted eleven standard relation classes. We kept our seven and added part of, prevents, rules out and fixed by, because each one answers a question in debugging. The Diagnosis page already uses causes, tests and fixed by. We would like your view before we change the graph prompt."

### 7. Teaching study (1 minute)

Open the teaching study plan.

Say "For the backup paper, we planned a pretest and posttest study with matched groups. We suggest a pilot with your master students and the main study with a foundation cohort. To show a medium effect we need about fifty students in each group. We need your advice on ethics approval."

## Questions to ask Dr Ho

1. Is the Diagnosis page the right shape for the inspection use case? What should change before we show it to the partner or the startup contacts?
2. Are the eleven relation classes right, and is anything missing that inspection engineers use?
3. Which cohort and topic for the teaching study, and how does ethics approval work at UTP?
4. Is the Azure access ready, so we can test the agents on it?
5. Is the name RootAI fine with you? The thesis keeps its title.

## Things to say honestly if asked

- The AI4I data is synthetic, so it is cleaner than real plant data. Its value is that the true causes are published, so we can check the method.
- The fixes on the Diagnosis page are plain engineering sense, not from a standard, and are marked as a draft.
- For a new topic, the chances on From data are AI guesses, not counted from data.
- The Reasoning agent has not been checked against a human marker yet. The marking sheet is ready.
- The RootAI name has not been checked with SSM or MyIPO yet.
