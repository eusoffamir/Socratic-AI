# Standard relation classes for diagnosis (Meeting 3, task 5)

Draft 1, 27 November 2026, by Claude for Eusoff, to be checked by Dr Ho. Builds on the knowledge graph review (thesis section 2.8, `docs/thesis/kg-generation-review.md`) and the storage note (`docs/supervisor/kg-storage.md`).

## Why we need a fixed set

The review showed two kinds of method. Open methods (Open IE, GraphRAG) let the text name each relation, so the same idea appears as "causes", "leads to", "results in" and "produces", and the graph is hard to reason over. Schema methods (ontologies, NELL, COMET) use a fixed list, so every edge can be checked and graphs built at different times can be joined. For diagnosis we want the second kind, and a small list, so that each class has one clear use in the search for a fault.

Our graph today has 7 classes (`app/knowledge.py`, `RELATIONS`): causes, then, defines, supports, weakens, tests, leads_to. They were chosen for teaching. Diagnosis needs a few more.

## The proposed set

We keep all 7 and add 4, so 11 in all. Each class has one reasoning move that uses it, and one question it answers while debugging.

| Class | From, to | Debugging question it answers | Reasoning move | Number on the edge | New? |
|---|---|---|---|---|---|
| part_of | component, equipment | Where in the equipment can the fault be? | deductive (narrows the search) | none | new |
| causes | cause, effect | What could have made this happen? | abductive when walked backward, deductive when walked forward | chance, learned from data or given by an expert | kept |
| prevents | barrier, hazard | Which protection has failed? | abductive (a failed barrier is a suspect) | chance the barrier fails | new |
| tests | check, fault | What should we check next? | chooses the next step (value of information) | cost of the check | kept |
| rules_out | finding, fault | Which faults can we drop? | deductive | none (a hard rule) | new |
| supports | evidence, belief | How much does this raise our belief? | inductive | strength, from counts | kept |
| weakens | evidence, belief | How much does this lower our belief? | inductive | strength, from counts | kept |
| fixed_by | fault, action | What do we do once we know the fault? | deductive | none | new |
| then | step, next step | In what order do we inspect? | procedural | none | kept |
| defines | concept, term | What does this word mean? | none (teaching only) | none | kept |
| leads_to | knowledge, choice | Which decision does this point to? | strategic (teaching only) | none | kept |

So the 9 classes from part_of to then are the diagnosis core. defines and leads_to stay for the teaching cases.

We did not add "symptom_of", because it is just "causes" read backward. Walking a "causes" edge from effect to cause is the abductive move, so one class serves both directions.

## How a diagnosis walks the graph

1. **Start from what was seen.** For example, a machine failed, or an inspector saw corrosion inside an enclosure.
2. **Walk "causes" backward (abductive).** Collect every fault that could cause what was seen. The chances on the edges rank them. "prevents" edges add failed barriers to the list.
3. **Narrow with "part_of" and "rules_out" (deductive).** Drop faults in parts that were not involved, and faults a finding has ruled out.
4. **Pick the next check with "tests".** Choose the check that most raises the chance of naming the right fault for its cost. This is the value of information from Koller and Friedman (2009), Chapter 23.
5. **Update with "supports" and "weakens" (inductive).** The result of the check changes the chances. Repeat from step 3 until one fault is clear enough.
6. **Act with "fixed_by".** Give the repair, and use "then" to order the steps.

This is the same loop as the Bayesian network test on the AI4I data (`docs/supervisor/pgm-ai4i.md`). There, each check was a reading such as power or strain, and the network named the right fault after one to three checks every time.

## Worked example 1, the AI4I milling machine (open data)

The dataset publishes the rule behind each failure mode, so the edges below are known to be true. They are built into the diagnosis demo (`app/diagnose.py`).

- spindle part_of machine, tool part_of machine
- low temperature gap causes heat dissipation failure, slow speed causes heat dissipation failure
- power out of range causes power failure
- high strain causes overstrain failure, product type L causes overstrain failure (its strain limit is the lowest)
- long tool wear causes tool wear failure
- power reading tests power failure, strain reading tests overstrain failure, and so on
- normal power rules_out power failure
- tool wear failure fixed_by replace the tool

## Worked example 2, Ex equipment inspection (for the partner use case)

This one is only a sketch to show the classes fit. The real nodes must come from the partner's engineers and from the inspection standard IEC 60079-17, which sets the visual, close and detailed grades of inspection. We have not read the standard yet, so none of these lines should be quoted as fact.

- gasket part_of flameproof enclosure
- gasket prevents water and dust entering
- damaged gasket causes water inside the enclosure, and water inside causes corrosion
- close inspection tests gasket condition
- dry enclosure interior rules_out water entry as the cause
- damaged gasket fixed_by replace the gasket, then check the flamepath gaps

## Words that map to each class

When a model or a person writes a relation in their own words, plain code maps it to a class before it is stored. This is the step that open methods skip, and it is the main change for task 3 (refining the graph prompt).

| Class | Words that map to it |
|---|---|
| causes | leads to (for events), results in, produces, triggers, makes, raises the chance of |
| part_of | is in, belongs to, is a component of, sits inside |
| prevents | protects against, stops, guards against, seals against |
| tests | checks, measures, detects, inspects, reveals |
| rules_out | excludes, means it is not, cannot be, eliminates |
| supports | suggests, is evidence for, agrees with |
| weakens | argues against, is evidence against, makes less likely |
| fixed_by | is repaired by, is solved by, is corrected by |
| then | after that, next, followed by |

## Questions for Dr Ho

1. Is 11 a good size, or should the teaching classes and the diagnosis classes be two separate sets?
2. Should "causes" always carry a chance, even when an engineer only says "often"? We could map words to numbers, for example "rarely" to 10 percent and "often" to 60 percent, and mark them as guesses.
3. For the Ex case, are there relations the engineers use that are missing here, for example "requires" (a check that needs a permit or isolation first)?
4. Once agreed, we change `RELATIONS` in `app/knowledge.py` and the Topic Builder prompt, so every new graph uses this set.
