# Teaching study, test forms A and B (draft)

Made by `eval/study_forms.py` from the everyday skill check bank in `app/skillcheck.py`, 27 November 2026.
Draft for Dr Ho. The questions were written by Claude and still need a check that each one is sound.

## How to use them

1. Each form has 15 questions, 5 for each kind of reasoning, one for each kind of knowledge.
2. Half the students take Form A before the session and Form B after. The other half take B first, then A.
3. Students answer each question in a few sentences, by hand or in a plain form, not inside the tutor, so the control group is not at a disadvantage.
4. Marking. An answer scores 1 if it uses the target kind of reasoning on the target kind of knowledge, and 0 if not, using the rules in `docs/evaluation/assessor-marking-guide.md`. Two markers mark a sample of answers to check they agree.
5. Each student gets a total out of 15 and a score out of 5 for each kind of reasoning.

The target is shown here for the markers only. Students see the situation and the question, not the target.

## Form A

1. Your bus came 10 minutes late on Monday, Wednesday and Friday. What general idea do you get about this bus?
   (target inductive reasoning, factual knowledge, id e-ind-fact-1)

2. A fair coin has a 50% chance of landing heads each time you flip it. What is the chance of getting 2 heads in a row, and how did you get it?
   (target deductive reasoning, factual knowledge, id e-ded-fact-1)

3. A quiet cafe near campus was packed last Tuesday, but on every other Tuesday it is almost empty. What is the best explanation, and what would you check?
   (target abductive reasoning, factual knowledge, id e-abd-fact-1)

4. A mango, a tomato and a cucumber all grow from a flower and hold seeds inside. From these 3, what do you think makes something a fruit?
   (target inductive reasoning, conceptual knowledge, id e-ind-conc-1)

5. A mammal is an animal that feeds its babies with milk. A whale feeds its baby with milk, so is a whale a mammal, and why?
   (target deductive reasoning, conceptual knowledge, id e-ded-conc-1)

6. A post says organic food is always healthy, and shows an organic chocolate cake as proof. What has the post most likely misunderstood about what organic means?
   (target abductive reasoning, conceptual knowledge, id e-abd-conc-1)

7. You burned your rice 3 times this month, and each time you had left the kitchen to check your phone. What cooking habit would you build from these 3 times?
   (target inductive reasoning, procedural knowledge, id e-ind-proc-1)

8. In a fair taste test, every drink must be tasted without seeing its label. Your friend compared 2 colas while looking at the cans, so what follows about the test?
   (target deductive reasoning, procedural knowledge, id e-ded-proc-1)

9. You and a friend baked the same cake recipe, and yours came out flat while theirs rose well. What difference in how you baked could best explain this?
   (target abductive reasoning, procedural knowledge, id e-abd-proc-1)

10. On 3 nights you slept after 2 am, and each next morning you did badly in the quiz. What do these 3 nights suggest about why the quizzes went badly?
   (target inductive reasoning, causal knowledge, id e-ind-caus-1)

11. Rain makes the roads wet and also makes more people book a Grab. If tomorrow is dry and sunny, what should happen to both, and why?
   (target deductive reasoning, causal knowledge, id e-ded-caus-1)

12. Everyone in one hostel block got a stomach ache on the same night, but nobody in the other blocks did. What is the most likely cause, and why?
   (target abductive reasoning, causal knowledge, id e-abd-caus-1)

13. A cafe sold 20 iced drinks on a 25 degree day, 50 on a 30 degree day, and 90 on a 35 degree day. What link between the heat and iced drink sales do you notice?
   (target inductive reasoning, relational knowledge, id e-ind-rela-1)

14. The more people share a pizza, the fewer slices each person gets. A pizza has 12 slices and 6 friends share it equally, so what follows for each friend?
   (target deductive reasoning, relational knowledge, id e-ded-rela-1)

15. Your football team has won every match this season when it wore its blue kit. What could best explain this link?
   (target abductive reasoning, relational knowledge, id e-abd-rela-1)

## Form B

1. Three bubble tea shops near campus each have a queue of 20 people at 5 pm, but almost nobody at 10 am. What do these 3 shops suggest about when people buy bubble tea?
   (target inductive reasoning, factual knowledge, id e-ind-fact-2)

2. Your phone loses about 10% battery every hour while you watch videos, and it has 40% left. How long can you keep watching before it dies, and why?
   (target deductive reasoning, factual knowledge, id e-ded-fact-2)

3. A new online shop has 200 reviews, all with 5 stars, and all written in the same week. What is the most likely explanation for these reviews?
   (target abductive reasoning, factual knowledge, id e-abd-fact-2)

4. Aina, Ben and Chong each said they were too busy to study, and each spent over 4 hours on their phone that day. What do these 3 stories suggest being too busy often means?
   (target inductive reasoning, conceptual knowledge, id e-ind-conc-2)

5. A fair game gives every player the same chance to win. In a board game the host always moves first and wins most games, so is it fair by this meaning, and why?
   (target deductive reasoning, conceptual knowledge, id e-ded-conc-2)

6. Someone says the cheetah must be the strongest animal because it is the fastest. What has this person most likely mixed up?
   (target abductive reasoning, conceptual knowledge, id e-abd-conc-2)

7. Three friends bought the same new phone. The 2 who read reviews first were happy, but the 1 who bought it on launch day was not. What step do these 3 stories suggest before buying a gadget?
   (target inductive reasoning, procedural knowledge, id e-ind-proc-2)

8. To get a free coffee, you must buy 9 coffees and show your full stamp card. Mei bought 9 coffees but lost the stamp card, so does Mei get a free coffee, and why?
   (target deductive reasoning, procedural knowledge, id e-ded-proc-2)

9. Two classes took the same quiz, and one class scored much higher than the other. What might have been different in how each class took the quiz?
   (target abductive reasoning, procedural knowledge, id e-abd-proc-2)

10. Your plant drooped in the week you forgot to water it, in the week it sat in the dark, and in the week it got too hot. What do these 3 weeks suggest makes a plant droop?
   (target inductive reasoning, causal knowledge, id e-ind-caus-2)

11. Caffeine keeps you awake for about 6 hours after you drink it. You drink a big coffee at 9 pm, so what should happen at midnight, and why?
   (target deductive reasoning, causal knowledge, id e-ded-caus-2)

12. Your phone suddenly loses battery twice as fast as it did last week. What is the best explanation, and what would you check?
   (target abductive reasoning, causal knowledge, id e-abd-caus-2)

13. Your group project took 4 hours with 2 people, 3 hours with 4 people, and 5 hours with 8 people. What link do you see between group size and the time taken?
   (target inductive reasoning, relational knowledge, id e-ind-rela-2)

14. The earlier you book a flight, the cheaper the ticket usually is. Sara books 1 day before the trip and Ken books 2 months before, so who should pay less, and why?
   (target deductive reasoning, relational knowledge, id e-ded-rela-2)

15. Ice cream sales and the number of drownings rise and fall together every year. What connection could best explain this?
   (target abductive reasoning, relational knowledge, id e-abd-rela-2)
