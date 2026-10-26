# Proposal defence, questions and answers to practise

There are 5 minutes of questions after the talk, with Dr Ho and Dr Syaimaa'. Dr Syaimaa' is a lecturer in Electrical and Electronics Engineering, so expect questions about engineering, testing and evidence more than about teaching theory.

Each answer takes about 20 to 30 seconds to say. Do not learn them word for word. Learn the first sentence and the main point of each one.

## How to answer

1. Pause for a second, then give the short answer first.
2. Add one reason or one example, then stop.
3. If you do not know, say so plainly, for example, "I have not tested that yet. I plan to check it in FYP2 by ..."
4. Never claim the tool improves thinking. It is not proven yet, and saying so honestly is a strength.
5. If the question is about the app, offer to show it live, but keep the screenshots ready in case Render is slow.

## The most likely questions

### 1. Why is this an engineering project?

The official listing for 26S005 sets the goal of building an agentic AI tool for engineering undergraduates. AI can now do much of the analysis engineers used to do, so engineers need to judge AI output instead of just accepting it. The work itself is engineering too, because it is a multi-agent system with rules that guard it, with tests, measurement and a live deployment.

### 2. How do you know the Assessor's marks are correct?

I do not know yet, and I say so on slide 19. So far I only have AI marks on 61 test answers, and they go in the right direction, because strong answers score high and trick answers score low. In FYP2, human markers will mark the same answers, and I will compare them with Cohen's kappa. The grant aims for 0.8.

### 3. What makes it "agentic"? Is it not just a chatbot with a long prompt?

A single chatbot does everything in one prompt. My system has separate agents with separate jobs, like the Assessor, Planner, Tutor and Checker, and they pass work to each other in a graph. The Planner decides the next move, and the Tutor can choose to run a simulation tool. Plain code checks every decision, so the agents decide and the rules guard them.

### 4. How will you show that students actually think better?

That is objective three and the evaluation in FYP2. I will use a short survey with real learners after ethics approval, plus the mastery data the app already records over several questions. A proper before and after study needs more time and more students than one FYP, so I will report it as a limitation.

### 5. Can a student just paste an answer from ChatGPT?

The app checks for this. Plain code gives zero to an answer copied from the hint. There is also a check for answers that read like a chatbot wrote them, and in the skill check, paste is turned off. It cannot catch everything, because a student can retype an AI answer, but then the Tutor asks a simpler follow-up question that a copied answer does not fit.

### 6. What if the AI gives wrong facts?

The quant topic and its three cases are written and checked by hand, and the Tutor may only use facts from those notes. For other topics, the Topic Builder grounds the cases on Wikipedia, and the page shows a clear warning that they were made by AI and not checked by an expert. In FYP2 I will add real reading material with Dr Ho.

### 7. Why Paul and Elder, and not another framework?

Paul and Elder give two things I need in one framework. The six kinds of Socratic questions give the tutor its ladder, and the nine standards give the assessor something to mark against. They are also widely used in teaching and are easy to explain to a student. Bloom and SOLO add the type of knowledge and how complex the answer is.

### 8. Why use Gemini? What does it cost?

I have no budget for paid AI, so I use the free tier of Gemini. One session uses about 24 AI calls, which fits the free plan. The code can also switch to Claude or to a mock mode with no AI at all, so the tests run for free and the tool does not depend on one company.

### 9. How is this different from ChatGPT study mode or Khanmigo?

They also refuse to give answers, which is good. But they have no fixed ladder of questions, they do not mark the thinking against a framework, and they do not show the learner which kinds of reasoning they have mastered. My tool does all three, and its marks can be checked against human markers.

### 10. How does it adapt to the learner?

After every answer, the Assessor marks the nine standards and the type of reasoning. The Planner uses those marks to pick the next move, such as moving up a level, staying, or giving a hint. Plain code then checks the plan. For example, a frustrated learner always gets an easier question.

### 11. Why did you pick quant as the topic?

Dr Ho set the topic. It suits critical thinking well, because the core skill is telling a real pattern in data from luck, which needs evidence, assumptions and other viewpoints. It is also kept for beginners, with no complex maths. The Topic Builder now lets learners use any other topic too.

### 12. What are the main limitations?

There are four. The Assessor is not yet checked against human markers. Only the quant topic has been checked by hand. There is no study with real learners yet. And the free AI model can sometimes write a weak question, which I fix from real transcripts.

## Questions that may come up

### 13. A or B questions look too easy. Are they critical thinking?

They are the easiest format, used when a learner is stuck. The learner must still say why, and the send button stays off until they write a reason. The marks come from the reason, not from the pick.

### 14. How do you decide that a student has mastered a skill?

One good answer is not enough, because it could be luck. Each skill is checked over several questions, and the app keeps a running estimate of how likely the learner is to show that skill again. Mastery needs that estimate to stay high over several answers.

### 15. What about privacy and student data?

Sign in with Google is optional. The app does not store the name or the email, only a scrambled code made from the Google account. For the study with real learners, I will get ethics approval first.

### 16. Your Assessor gives keyword answers about 4 out of 9. Is that a problem?

Yes, it is my next fix, and I show it on slide 19 on purpose. Answers that only repeat key words should score lower. I will add clear examples of such answers to the Assessor's instructions and test it on the same 61 answers again.

### 17. What if Gemini changes or stops its free plan?

The code keeps the AI provider separate from the rest of the system, so switching is one setting. It already works with Gemini, with Claude, and with a mock mode, and a paid Claude subscription for the project has been requested through Dr Ho.

### 18. What is LangGraph, and why use it?

LangGraph is a Python library for joining AI agents into a graph of steps. It makes the order fixed and easy to test, so each turn always goes assess, plan, guard, tutor, check, and then rewrite once if needed. It also lets me switch single agents on and off to test what each one adds.

### 19. Is 0.8 kappa realistic?

It is the target set by the grant, and it is high. Even human markers often agree less than that on critical thinking. If I fall short, I will report the real value and look at which standards the Assessor and the humans disagree on most.

### 20. What is your main contribution?

A Socratic tutor that does three things together. It asks questions up a fixed ladder, it measures the thinking against a known framework, and it adapts to the learner's gaps. The existing tutors I tested did none of these three.

## If you get stuck

- "That is a good point. I have not looked at that yet, but I will note it for FYP2."
- "Could you say a bit more about what you mean by ...?"
