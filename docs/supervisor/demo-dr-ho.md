# Demo for Dr Ho (after Meeting 3)

About 15 minutes of demo, 5 minutes on the papers, then questions. Written 27 November 2026, updated 28 November 2026 for the two user groups, the engineer Knowledge page and Your own machine on Diagnosis.

Each page has a short part called "Why it looks like this". Those are not to read out. They are the reasons to give if Dr Ho asks why a page is designed the way it is.

The story to tell is simple. RootAI has two kinds of users. For students, it teaches reasoning and measures it. For engineers, it stores what is known about a machine in three ways, from a book, an engineer and data, and uses all three to find why the machine failed.

## Before the meeting

1. The night before, make one good chat on a topic close to Dr Ho, for example "Generative AI for data analysis" or his Intro to AI slides as a file. Answer 4 or 5 rounds properly, so the level goes up and the chat has a full map. In the demo, open this chat from Recents instead of making a new topic live.
2. Avoid unclear topics live. Some topics first ask which meaning you want, and the choices can be odd.
3. Record a short screen video of the whole flow as a backup, in case the wifi or Gemini fails.
4. Open https://socratic-ai-qlk6.onrender.com about 5 minutes before, so the server is awake, and press Ctrl+Shift+R so the RootAI logo shows.
5. Open /api/health and check it says ok. Open /api/config and check ai_guard is true.
6. Open the Diagnosis page once, so the network is already learned (the first load takes a few seconds). Then open Knowledge, press Start again on Rules of thumb and Clear all on From data, so both start clean.
7. Have these open in tabs, the knowledge graph review (thesis section 2.8 or `docs/thesis/kg-generation-review.md`), the relation classes doc, the Ex problem statement, the teaching study plan and the AI4I results.
8. If you forget what a page does, press the question mark at the bottom of the sidebar. It walks through the page that is open, and Dr Ho can see it too.

## What to show and what to say

### 1. The start page and the name (1 minute)

Point to the logo and the name in the sidebar.

Say "The tool now does more than Socratic tutoring, so we call it RootAI, reasoning that finds the root. The sidebar has two groups. New chat and Overall status are for students, the chat teaches and Overall status measures. Then Knowledge and Diagnosis are for engineers, so they show what RootAI knows about a machine and use it to find a fault."

**Why it looks like this.**
- Two groups, because there are two users with different jobs. A student never needs the machine pages, and an engineer never needs the tutor, so the student pages come first and the engineer pages after, without hiding anything.
- The start page is one box, like the chat tools students already use, so there is nothing to learn before starting.
- Labels are plain and there are no long help texts on the page. The question mark at the bottom gives a one line guide for whichever page is open, so help is there only when someone asks for it.

### 2. The tutor (3 minutes)

Open your prepared chat from Recents.

Say "Any topic can go in here. The Topic Builder turns it into short cases, and the tutor never gives the answer. It asks questions up Paul's six levels, from clarify to question the question."

Answer one more question live. Pick A or B and give a short reason.

Say "After each answer, the Assessor scores it on Paul and Elder's nine standards and marks which reasoning I used, inductive, deductive or abductive."

Tap the bar at the top of the chat to open the progress panel.

Say "Here is the level I reached, the nine standards as a radar, and the Coach, who comments after a few answers."

Open Read more on the case card and point to the map.

Say "Each case also has a small map of its ideas, and each arrow says how two ideas link. This is where the knowledge graph shows for students."

**Why it looks like this.**
- A chat, because students already know how to use one, and we chose it over a page of cases on 23 November.
- A or B first, then a reason, because picking is an easy way in, but the reason is what shows the thinking, and that is what the Assessor scores.
- The tutor never gives the answer and only asks the next question, because the aim is critical thinking, not an answer machine.
- The scores sit behind the bar at the top, not in the chat, so the student keeps thinking about the case and not the marks.
- The map is folded inside Read more, so the first look stays short and a curious student can still open it.

### 3. Overall status (1 minute)

Open Overall status in the sidebar.

Say "This adds up every chat and skill check. Summary says it in plain words, and Full data shows the bars and grids we use for the study. The skill check is three short questions, one for each kind of reasoning, and a skill only counts as mastered after three or more answers on it, so it builds up over a few checks."

**Why it looks like this.**
- Summary comes first in plain words, because a student wants to know how they are doing, not read a chart. Full data keeps the bars and grids for us and for the study.
- Each part sits in its own card with the title on the left, so the page reads top to bottom like a report.
- The skill check is three questions, one for each kind of reasoning. It was six, but that felt too long, and three still covers all three kinds.
- A skill counts as mastered only after three or more answers on it, so one lucky check can never show a skill as mastered.
- "Seen in your chats" only gives credit and never changes mastery, because chat marks are not checked against a human marker yet.

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

**A case from a chat.** Open the menu next to the title and pick the case from your prepared chat.

Say "The same page also shows what the AI built for every topic a student chats about. Here is the map from books, with the source of each box, the expert rules and the network. So for any topic, not only the machine, we can check the knowledge the tutor reasons with."

Press Walk through it.

Say "This lights the map one link at a time, the way a student walks it when they reason."

**Why it looks like this.**
- It opens on the machine, the same one Diagnosis works on, so the two pages are a pair. Knowledge is what RootAI knows, and Diagnosis is RootAI using it.
- The menu next to the title also lists the case from every recent chat, so we can check what the AI built for any topic. The machine comes first because the page is for engineers, and the cases are there for us and for you to review.
- Three tabs for the three kinds of knowledge from Goal 3, books, rules of thumb and data, and each one matches one kind of reasoning. Keeping them apart lets an engineer check each source on its own.
- Every tab is something to try, not text to read, because an engineer trusts what they can test. Tapping a fault shows its source, so every claim can be traced.
- Rules of thumb is a flowchart and not one question at a time, so the engineer sees the whole checklist at once and can say where it is wrong.
- From data is a what if, because that is how engineers already think, as in "if the tool is worn and the torque is high, what is likely?" The chance moves as soon as a reading is set.
- The arcs and the "Most likely" line explain the answer, so the network is not a black box. Chances are always percentages.
- The graphs use the same boxes, colours and arrows as Diagnosis, so learning one page teaches the other.

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

**Why it looks like this.**
- One button, Find the cause, runs it all, because an engineer with a stopped machine wants the answer, not a lesson. One step is still there for anyone who wants to follow each check.
- The result card comes first, with the cause, the fix, how many readings it needed, how sure it is and whether the expert rule holds, because that is what an engineer acts on.
- The graph sits under the card as the evidence. The lit path is the reasoning, as you said in Meeting 3, that the path through the graph is what explains the answer.
- The dashed box shows the reading it will check next. It picks the reading that tells the most, so an inspector measures fewer things, about 2 of 6 on average.
- The 114 machine line is there so nobody thinks the demo machine was picked to look good.
- The agent only writes the Why text, and the numbers come from the network, so the model cannot change a number. That follows "agents decide, rules guard".
- Your own machine makes it a tool and not only a demo. It is honest about what it does not know, so a reading left out shows as Not given, a rule without its readings says it cannot be checked, and there is no "It really was" line.

### 6. Knowledge graph review (2 minutes)

Open the review. This was the main task from the last meeting, so give it time.

Say "We looked at twelve families of methods for building a knowledge graph. For each one we asked how it chooses the nodes, how many nodes it makes, and how it chooses the edges and their types. The main finding is that methods with a fixed list of relation types give graphs we can check and join, while open methods give many names for the same link. And from the open data test, choosing the right nodes mattered more than anything else, because the same method went from 82 percent to 100 percent just by using the variables an engineer would choose."

Then ask "Which of these methods do you think fits the inspection case best?"

### 7. Fusing the three graphs (1 minute)

Say "Task seven was to fuse the three kinds of graph. The Knowledge page shows the machine in all three, the graph from the book, the engineer's checklist and the network from data. On the Diagnosis page they work together. The graph says which reading can cause which fault, the network ranks the faults and picks the next check, and at the end the expert rule is tested on the real numbers. On all 114 failed test machines the rule agreed with a real fault. What we do not have yet is one single fused graph that the agents walk. How do you picture that?"

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

1. Are the Knowledge and Diagnosis pages the right shape for the inspection use case? What should change before we show them to the partner or the startup contacts?
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
- The engineer's checklist on Rules of thumb is our draft, built from the published rules. A real inspector should check it.
- Your own machine only makes sense for a milling machine like the one in the data. A real plant machine needs its own data and rules.
- For a student's new topic, the case map is drafted by the AI from Wikipedia, and each box shows its quote so it can be checked.
- The Reasoning agent has not been checked against a human marker yet. The marking sheet is ready.
- The RootAI name has not been checked with SSM or MyIPO yet.
