# Problem statement, Ex equipment inspection (Meeting 3 use case)

Draft 1, 27 November 2026, by Claude for Eusoff, to be checked by Dr Ho and the partner engineer. Dr Ho said that for the FYP it is enough to state the problem and its impact clearly, so examiners understand the purpose (`meeting3-notes.md`, section 2.1). No partner data has arrived yet, so nothing here is measured.

Facts about the standards below are from general knowledge and must be checked against IEC 60079-10-1 (zones) and IEC 60079-17 (inspection) before they go into the thesis.

## 1. The problem in one paragraph

On an oil and gas plant, flammable gas can be present around some equipment. Electrical equipment in these areas is built so it cannot ignite the gas, and it is called Ex equipment. Over time this protection can wear out. A gasket cracks, a cable gland loosens, a cover bolt goes missing or the enclosure corrodes. Engineers inspect hundreds of these items, often from many photos, and write down every defect they find. The hard part is not finding defects but deciding **which ones matter most**. A missing bolt on a box in a place where gas is rarely present is less urgent than a small gap on a box where gas is often present. Today this ranking depends on a few experienced engineers, and their reasoning is rarely written down.

## 2. Why it matters (impact)

- **Safety.** An Ex defect is a possible ignition source in a place where gas may be present. Fixing the most dangerous defects first lowers the chance of a fire or explosion.
- **Time and cost.** An inspection can produce a long list of defects. Ranking them lets the team plan repairs in the right order, instead of treating every item as equally urgent.
- **Knowledge that leaves.** The ranking lives in the heads of a few senior engineers. When they retire or move, the reasoning goes with them. Writing it as a graph keeps it.
- **Trust.** A ranking that shows its reasons can be checked by a person and audited later, which a black box cannot.

## 3. What we propose

A system that takes the defects found in an inspection and ranks them by safety impact, and shows why. It joins two graphs, as Dr Ho described.

1. **A hazard graph** of what causes ignition. For example, a damaged gasket lets water in, water causes corrosion, and corrosion can open a flamepath gap that lets a flame escape. Each protection type (for example flameproof, increased safety, intrinsic safety) has its own ways to fail.
2. **An infrastructure graph** of the plant. Each item is linked to where it sits (its hazardous area zone), what it is part of, and what it is near, for example a tank or a process line on the single line diagram.
3. **A link between them.** A defect on an item gets its chance of becoming an ignition source from the hazard graph, and the chance that gas is there from the infrastructure graph.

The ranking then follows a simple idea. A defect matters more when it is more likely to make a spark or hot surface, when gas is more likely to be present, and when the result would be worse. The chances come from the partner's past records where they exist, and from engineers' judgement where they do not, clearly marked as guesses.

The same three moves as the Diagnosis demo apply.

- **Inductive.** Learn how often each defect leads to a real fault, from past inspection records.
- **Abductive.** From what the photos show, find the most likely underlying fault (for example, a stain under a cover suggests water got in through the gasket).
- **Deductive.** Apply the inspection rules and the zone rules to decide what must be done and how soon.

The agents are used only where a fixed algorithm cannot do the job, such as reading an engineer's free text notes or explaining the ranking. The chances and the ranking are plain code, as in `app/diagnose.py`.

## 4. How it uses the relation classes

These are the classes drafted for task 5 (`relation-classes.md`).

| Example | Class |
|---|---|
| gasket part_of enclosure | part_of |
| gasket prevents water entry | prevents |
| water inside causes corrosion | causes |
| close inspection tests gasket condition | tests |
| dry interior rules_out water entry | rules_out |
| damaged gasket fixed_by replace gasket | fixed_by |
| enclosure located_in Zone 1 area | new, needed to link the two graphs |

So the Ex case needs at least one more class, something like "located_in", to join an item to its place on the plant. This is a question for Dr Ho.

## 5. Scope for the FYP

- **In.** A small example of the two graphs and the ranking, on a few types of Ex equipment, with chances marked as guesses until real records arrive. A clear explanation for each ranked defect.
- **Out.** Detecting defects in photos (Dr Ho said image classification is not our job), connecting to live plant systems, and replacing the engineer's decision. The system advises, a person decides.

## 6. What we need from the partner

1. A list of common defects for each protection type, as their engineers record them.
2. Past inspection records with outcomes, even a few hundred rows, so chances can be counted.
3. The hazardous area zone of each item, or a sample area drawing.
4. One or two engineers to check the hazard graph and say how they rank defects today.
5. Permission to use anonymised examples in the thesis and a paper.

## 7. How we will know it works

- The ranking agrees with experienced engineers on a set of real inspection results (for example, how often our top 10 matches theirs).
- Engineers can follow the reason given for each ranked defect.
- On an open dataset the same method already found the right fault every time (the AI4I demo), which shows the method works before real data arrives.

## 8. Questions for Dr Ho

1. Is this the problem as you see it, and is ranking by safety impact the right goal?
2. Should we add a "located_in" class to join the two graphs?
3. Can the partner share past records with outcomes, not only photos?
4. Who at the partner can check the hazard graph?
