# Demo for Dr Ho (after Meeting 3)

About 15 minutes of demo, 5 minutes on the papers, then questions. Written 27 November 2026, updated 28 November 2026 for the two user groups, the engineer Knowledge page, Your own machine on Diagnosis, and the simpler Knowledge Summary and step by step Diagnosis.

Each page has a short part called "Why it looks like this". Those are not to read out. They are the reasons to give if Dr Ho asks why a page is designed the way it is.

The story to tell is simple. RootAI has two kinds of users. For students, it teaches reasoning and measures it. For engineers, it stores what is known about a machine in three ways, from a book, an engineer and data, and uses all three to find why the machine failed.

## Before the meeting

1. The night before, make one good chat on a topic close to Dr Ho, for example "Generative AI for data analysis" or his Intro to AI slides as a file. Answer 4 or 5 rounds properly, so the level goes up and the chat has a full map. In the demo, open this chat from Recents instead of making a new topic live.
2. Avoid unclear topics live. Some topics first ask which meaning you want, and the choices can be odd.
3. Record a short screen video of the whole flow as a backup, in case the wifi or Gemini fails.
4. Open https://socratic-ai-qlk6.onrender.com about 5 minutes before, so the server is awake, and press Ctrl+Shift+R so the RootAI logo shows.
5. Open /api/health and check it says ok. Open /api/config and check ai_guard is true.
6. Open the Diagnosis page once, so the network is already learned (the first load takes a few seconds), then press Other machines so it starts on the three machines. Open Knowledge once too, so it opens on Summary.
7. Have these open in tabs, the knowledge graph review (thesis section 2.8 or `docs/thesis/drafts/kg-generation-review.md`), the relation classes doc, the Ex problem statement, the teaching study plan and the AI4I results.
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

### 4. Knowledge page (2 minutes)

Open Knowledge in the sidebar. It opens on Summary, one row for each way the milling machine from the open AI4I data can fail.

Say "From here on the user is an engineer, not a student. RootAI knows five ways this machine can fail. Each row says what causes the fault and what to do. On the right, the green ticks show where each fact is known from, a book, an engineer's rules of thumb and data from 7,000 past runs. All three agree, and the line at the bottom says the data found the same causes as the book without being told them."

Tap the Data tick on Overstrain failure. It opens From data.

Say "Each tick opens that source. This is the network learned from the data." Set Tool wear to Old. "Old tool wear makes overstrain the most likely, because the data learned that a worn tool usually carries high strain."

If Dr Ho asks, show From books (tap a fault to see its rule and source) and Rules of thumb (press No, then Yes, to walk the checklist).

**A case from a chat.** Open the menu next to the title and pick the case from your prepared chat.

Say "The same page shows what the AI built for every topic a student chats about, the map from books with the source of each box, the expert rules and the network. So for any topic, we can check the knowledge the tutor reasons with."

**Why it looks like this.**
- It opens on Summary, like Overall status, so the first look is one plain table and not three graphs. The graphs are one tap away for anyone who wants the detail.
- One row per fault, because that is how an engineer thinks, "what can go wrong, why, and what do I do".
- The three ticks show the three kinds of knowledge from Goal 3 side by side, and each tick opens its own tab, so every fact can be traced to its source.
- It opens on the machine, the same one Diagnosis works on, so the two pages are a pair. Knowledge is what RootAI knows, and Diagnosis is RootAI using it.

### 5. Diagnosis page, the main new part (4 minutes)

Open Diagnosis in the sidebar. It looks like the New chat page, a title and three stopped machines to pick.

Say "This is a first working version of the industrial use case, on open data while we wait for the partner's data. Three machines have stopped. Let us find out why."

Tap Machine 1.

Say "RootAI does not check everything. It asks for the one reading that tells the most. Here it asks for the strain on the tool first."

Press Check all for me, and talk while it runs.

Say "Strain is low, so overstrain is unlikely. The bars below show the chance of each fault, and they move after every check. Next it checks power."

Say "Power is low, so it points to power failure, at 99 percent. It found the cause after 2 of the 6 readings, it gives the fix, and the expert rule agrees. And because this machine is from the test data, we know it really was power failure."

Open Why.

Say "Only this text comes from the agent. The numbers come from the network, so the model cannot change a number. RootAI walked from the failure back to its cause, which is abductive. It applied the published rule, which is deductive. And the chances were learned from data, which is inductive."

Open the Full data tab.

Say "Here is the same reasoning as a graph, the readings, the faults they can cause and the fix. The lit path is the path RootAI followed." Point to the line at the bottom. "And this is not one lucky machine. On all 114 failed test machines it found the right cause 98 percent of the time, with about 2 of the 6 readings."

If there is time, press Other machines, pick Machine 3 and this time press the smaller Check button each time, one reading at a time. Say "This machine had two faults at once. RootAI rules out power and heat, then finds overstrain, one of the two real faults."

**Your own machine.** Press Other machines, then Type its readings. Press L, then type air 300, process 308, speed 1300 and torque 40, and press Find the cause.

Say "An engineer can type in their own machine. They leave out any reading they do not have, and RootAI works out the rest. Here it finds heat dissipation. Nobody knows the real answer for a new machine, so it does not claim one."

**Why it looks like this.**
- It starts like New chat, a title and three things to tap, so nobody has to learn the page first. The machines have plain names, Machine 1 to 3, instead of data IDs.
- RootAI asks for one reading at a time, so the viewer follows the reasoning step by step, the same way the tutor asks one question at a time. Check all for me is the main button, so the presenter can just talk, and the smaller button makes one check at a time.
- Each check is one plain sentence, what the reading is and what it means, so the reasoning reads like a short story.
- The bars show the chance of each fault, the one number that matters while checking. The big graph sits behind Full data, like Overall status, for anyone who wants the evidence.
- The answer card has the cause, the fix, how many readings it needed, how sure it is and whether the expert rule holds, because that is what an engineer acts on.
- Your own machine makes it a tool and not only a demo. A reading left out shows as Not given, and there is no "It really was" line.

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
