# Review of knowledge graph generation methods (draft 1, 25 November 2026)

Draft for the thesis and for a discussion with Dr Ho (Meeting 3, task 2). Every source in the list at the end was checked on Crossref, the ACL Anthology, JMLR or arXiv on 25 November 2026, except the two technical reports marked as such.

## 1. Why this review

Our tool already builds a small knowledge graph for any topic, and Dr Ho wants the diagnosis in the Ex inspection use case to be a walk on such a graph. There is no single right way to build a knowledge graph, so before we refine our own method we look at how others do it. For each method we ask three questions, because these decide what the reasoning can later see.

1. **Which things become nodes?**
2. **How many nodes are kept?**
3. **How are the edges and their relation types chosen?**

We also note whether a method puts numbers on its edges, since the Ex use case needs to rank hazards by their chance of causing a spark.

Hogan et al. (2021), Ji et al. (2022) and Zhong et al. (2023) give broad surveys of knowledge graphs and how they are built. This review is narrower. It groups the methods into twelve families and looks only at the three questions above.

## 2. The methods

### 2.1 Hand-built ontologies and concept maps

**Approach.** Experts list the questions the graph must answer (competency questions), then name the classes, their properties and the relations between them by hand (Noy & McGuinness, 2001). Concept maps in education work the same way, with a focus question at the top and the main concepts linked by short linking phrases (Novak & Cañas, 2008).

- **Nodes.** The experts choose them from the competency questions or the focus question.
- **How many.** Set by the scope the experts agree on. They start from a short list of key concepts for the focus question.
- **Edges.** Chosen by hand. Ontologies use a fixed, named set of relations. Concept maps allow free linking phrases.
- **Pros.** High quality and trusted by domain experts. The relation classes are standard from the start.
- **Cons.** Slow and costly, and it depends on the few experts who know the domain, which is exactly the bottleneck the project wants to remove.

### 2.2 Pattern rules

**Approach.** Hand-written text patterns find one kind of relation. Hearst (1992) used patterns such as "X such as Y" and "Y and other X" to find that Y is a kind of X.

- **Nodes.** The noun phrases that fill the pattern slots.
- **How many.** Whatever the patterns match in the text, with no direct control.
- **Edges.** One fixed relation per pattern, mostly "is a".
- **Pros.** Simple, fast, needs no training data, and each edge can be traced to a sentence.
- **Cons.** Low recall, and it only finds the few relations someone wrote patterns for. It gives a taxonomy, not causes or steps.

### 2.3 Word co-occurrence graphs

**Approach.** TextRank (Mihalcea & Tarau, 2004) links words that appear near each other in a text and ranks them with a PageRank style score.

- **Nodes.** Words or phrases that pass a part of speech filter (usually nouns and adjectives).
- **How many.** The top ranked nodes are kept, often a fixed share of the words, so the size is a simple setting.
- **Edges.** An edge joins two words that appear within a window of a few words. The edge has no meaning beyond "appear together", but it can carry a count.
- **Pros.** Fully unsupervised, cheap, works on any language and topic, and the ranking gives a clear rule for size.
- **Cons.** The edges have no relation type, so the graph cannot say "causes" or "tests". It finds what is frequent, which is not always what is important.

### 2.4 Mining semi-structured sources

**Approach.** DBpedia (Auer et al., 2007) turns Wikipedia infoboxes into facts. YAGO (Suchanek et al., 2007) joins Wikipedia categories to the WordNet taxonomy.

- **Nodes.** One node per Wikipedia article (an entity), plus classes from categories or WordNet.
- **How many.** All articles that exist, so millions. There is no idea of a small graph for one problem.
- **Edges.** From infobox fields mapped onto a fixed ontology, and "type" and "subclass" links from the categories.
- **Pros.** Very large, fairly accurate, and each fact points to its source page.
- **Cons.** It only covers facts that already sit in tables or categories. Causes, procedures and engineering know-how are mostly missing.

### 2.5 Relation extraction with a fixed schema

**Approach.** A model learns to spot a fixed list of relations in sentences. Distant supervision (Mintz et al., 2009) labels training sentences automatically, using pairs that a known database already links. NELL (Carlson et al., 2010; Mitchell et al., 2018) reads the web without stopping and grows a graph inside a fixed set of categories and relations.

- **Nodes.** Entity mentions that fit the schema's categories.
- **How many.** Not set. The graph grows with the text read, and only confident facts are added.
- **Edges.** Only the relations named in the schema.
- **Pros.** The relation classes are standard and can be checked. Confidence scores let weak facts be left out.
- **Cons.** A relation outside the schema is never found. It needs a seed database or labelled data, which a new industrial domain does not have.

### 2.6 Open information extraction

**Approach.** Open IE pulls (subject, relation phrase, object) triples from any sentence with no schema. Examples are TextRunner (Etzioni et al., 2008), ReVerb (Fader et al., 2011), which keeps relation phrases built around a verb, and Stanford OpenIE (Angeli et al., 2015), which splits sentences into short clauses first.

- **Nodes.** The noun phrases of each triple.
- **How many.** One or more triples per sentence, so the graph is as large as the text.
- **Edges.** The verb phrase found in the sentence becomes the relation, so the relation set is open.
- **Pros.** Works on any domain without training data, and every edge comes from a sentence.
- **Cons.** The same idea appears under many names ("causes", "leads to", "results in"), so the graph is noisy and hard to reason over until the nodes and relations are merged into a standard set.

### 2.7 Knowledge fusion with probabilities

**Approach.** Knowledge Vault (Dong et al., 2014) runs many extractors on the web and joins their output with what an existing graph already knows. Each fact gets a probability of being true. Later work on refinement adds missing edges and removes wrong ones (Paulheim, 2017).

- **Nodes.** Entities from an existing graph and the extractors.
- **How many.** Web scale.
- **Edges.** A fixed schema, but **each edge carries a probability**.
- **Pros.** The graph says how sure it is, which is what a ranking of hazards needs.
- **Cons.** It needs a large existing graph and many extractors. The probability is the chance a fact is true, not the chance an event happens, so it is not the same as a cause and effect strength.

### 2.8 Neural generation of commonsense

**Approach.** COMET (Bosselut et al., 2019) is a language model trained on commonsense graphs such as ConceptNet (Speer et al., 2017). Given a start phrase and a relation, it writes new end phrases.

- **Nodes.** Short phrases the model writes, so they need not appear in any text.
- **How many.** Set by how many phrases are asked for per start node and relation.
- **Edges.** A fixed relation set from the training graph, for example "causes" or "used for".
- **Pros.** Adds knowledge that no text states plainly. The relation set is standard.
- **Cons.** The new facts have no source, so they can be wrong in a way that is hard to check.

### 2.9 Large language model extraction and GraphRAG

**Approach.** A large language model reads the text in chunks and returns entities and relations, usually as JSON. Pan et al. (2024) and Zhu et al. (2024) review this and related work. GraphRAG (Edge et al., 2024) asks the model for entities of given types and a short description of each relation in every chunk, merges entities with the same name, then groups the graph into communities with the Leiden method (Traag et al., 2019) and writes a summary of each community.

- **Nodes.** Whatever the model names, guided by the entity types in the prompt.
- **How many.** Grows with the text. GraphRAG controls size at a later step by grouping nodes into communities at several levels.
- **Edges.** Chosen by the model. In GraphRAG the relation is a free text description with a weight that grows when the same link appears again. Other work gives the model a fixed relation list.
- **Pros.** Works on any topic with no training, reads meaning well, and can be pointed at the dimensions we care about by changing the prompt.
- **Cons.** The output can change from run to run, the model can invent links, and long texts cost many tokens, which is our main limit on free plans.

### 2.10 Prerequisite graphs and concept map mining for teaching

**Approach.** Liang et al. (2015) decide whether concept A must be learned before concept B by checking how often the Wikipedia pages linked to A refer to B (reference distance). Falke and Gurevych (2017) built a benchmark of small concept maps that summarise a set of documents, which made concept map mining a task that can be measured.

- **Nodes.** Wikipedia concepts (Liang et al.), or concept mentions found and grouped in the texts (Falke & Gurevych).
- **How many.** For concept maps, a small fixed limit, so the map stays readable.
- **Edges.** One relation, "is needed before" (Liang et al.), or a short phrase from the text (Falke & Gurevych).
- **Pros.** Built for learners, which matches our tutor. A small, fixed size is a clear choice of how many nodes.
- **Cons.** Prerequisite graphs have only one relation. Concept map mining is still hard and scores in the benchmark are low.

### 2.11 Learning a graph from data (Bayesian network structure)

**Approach.** Here the graph comes from a table of data, not from text. The PC method (Spirtes et al., 2001) starts with every pair of variables joined, removes an edge when a test shows the two are independent given others, then turns some edges into arrows. Score based search such as GES (Chickering, 2002) adds and removes arrows while a score keeps getting better. Koller and Friedman (2009) explain both families.

- **Nodes.** The columns of the data. A person still chooses which variables to measure.
- **How many.** Exactly the number of variables.
- **Edges.** Kept or dropped by statistical tests or a score, and **each arrow comes with conditional probabilities** counted from the data.
- **Pros.** The numbers come from evidence, not from a guess, and the graph supports reasoning under uncertainty (which cause best explains these signs).
- **Cons.** It needs enough data, and the arrows found are not always true causes. Choosing the variables is still a human job.

### 2.12 Fault trees from engineering analysis

**Approach.** Engineers start from one unwanted top event, such as "ignition in a hazardous area", and break it down into the events that could cause it, joined by AND and OR gates (Ruijters & Stoelinga, 2015).

- **Nodes.** Failure events chosen by engineers, working down from the top event.
- **How many.** Set by how far the engineers break each event down.
- **Edges.** AND and OR gates only. Each basic event can carry a failure probability.
- **Pros.** Standard in safety work, easy for engineers to check, and it gives a clear way to rank which failures matter most.
- **Cons.** Built by hand, and it holds only failure logic, not the wider concepts an inspector uses.

## 3. Comparison

| Method | Nodes chosen by | Size set by | Edges chosen by | Relation set | Numbers on edges |
|---|---|---|---|---|---|
| Hand-built ontology or concept map | Experts | Expert scope | Experts | Fixed (ontology) or free (concept map) | No |
| Pattern rules | Pattern slots | Matches in text | Pattern | Fixed, very small | No |
| Co-occurrence graph | Word filter plus rank | Top ranked share | Nearness in text | None | Counts |
| Semi-structured mining | Wikipedia articles | All articles | Infobox fields, categories | Fixed | No |
| Fixed schema extraction | Schema categories | Text read | Trained model | Fixed | Confidence |
| Open IE | Noun phrases | Text read | Verb phrases | Open | Confidence |
| Knowledge fusion | Existing graph plus extractors | Web scale | Extractors | Fixed | Probability true |
| Neural commonsense | Model writes phrases | Phrases asked for | Given relation | Fixed | Model score |
| LLM extraction, GraphRAG | Model, guided by types | Text read, then communities | Model | Open or fixed by prompt | Weight (GraphRAG) |
| Prerequisite or concept map mining | Wikipedia concepts or mentions | Small fixed limit | Link statistics or phrases | One relation or free | Score |
| Structure learning from data | Data columns | Number of variables | Tests or score | Arrows | Conditional probabilities |
| Fault tree | Engineers, from top event | Depth of breakdown | Engineers | AND, OR | Failure probabilities |

Two patterns stand out. First, every method that reads text either fixes the relation set in advance or ends up with an open set that must be cleaned later. Second, only the data based methods and fault trees give numbers that mean "how likely this event is", which is what a hazard ranking needs. Methods that read text give at most "how sure we are this fact is true".

## 4. What our tool does now

The Topic Builder (`app/builder.py`) is a large language model extraction method with a fixed schema (family 2.9 with the fixed relation list of 2.5), grounded in a Wikipedia page (`app/sources.py`).

- **Nodes.** The model writes 5 teaching notes and 3 to 5 extra facts per case, each tagged with one of Dr Ho's eight knowledge types. Each case must hold at least one factual, conceptual, procedural and causal piece.
- **How many.** Fixed by the prompt at 8 to 10 nodes per case, and the code keeps at most 11.
- **Edges.** The model writes 6 to 12 links, and the code drops any link whose relation is not one of seven names (causes, then, defines, supports, weakens, tests, leads_to) or whose ends are not real nodes.
- **Checks.** Each node may carry a quote, and the code keeps the quote only if it really appears in the source text (`python -m eval.check_quotes` for the built-in topic).
- **Numbers.** None on the graph's edges. The separate cause and signs model (`app/pgm.py`) has chances, but the model guesses them as round numbers.
- **Storage.** The graph is saved as JSON inside the session (under each case's "knowledge" key), so it is a hard artifact that the agents read back, not something that lives only in the chat.

Where it falls short.

1. **Size is fixed, not chosen.** Every topic gets about 10 nodes, whether it is simple or deep.
2. **The relation set was designed for teaching**, not checked against a standard and not tested for diagnosis.
3. **No numbers from evidence.** Edges have no weights, and the chances in the small model are guesses.
4. **One source.** Only one Wikipedia page, so the graph cannot be larger than what one page says, and nodes from separate runs are not merged.
5. **Runs can differ.** The same topic can give a different graph each time, and we have not measured how much.

## 5. What this suggests for the Ex inspection use case (for discussion)

No single method fits, so a mix seems likely. One possible split follows Dr Ho's two graphs and the link between them.

- **Graph of the infrastructure.** Built from the partner's documents (single line diagram, equipment lists). The nodes are real items, so the schema can be fixed in advance, as in 2.4 and 2.5.
- **Graph of what causes damage.** Drafted by the language model from the inspection standard (IEC 60079-17) and from engineers' notes, with a fixed relation list (2.9 with 2.5), then checked by an engineer (2.1). Its causal core could be written as a fault tree with "ignition" as the top event (2.12).
- **Numbers.** Chances counted from past inspection records when there are enough of them (2.11), and engineer estimates where there are not.

This also gives a first answer to Eusoff's idea of choosing the method from the input. Tables of data point to structure learning. Standards and textbooks point to schema guided model extraction. Engineers' interviews point to decision trees and fault trees. Free text with no known schema points to open extraction, followed by merging into a standard relation set.

## 6. Questions for Dr Ho

1. Should the relation classes be standard ones from an existing source (for example ConceptNet's relations), or our own set tested on the inspection data?
2. Is it acceptable for the first version to fix the graph size by the prompt, or should we choose it from the material (for example by ranking, as in TextRank, or by communities, as in GraphRAG)?
3. Will the partner share past inspection records, so that chances can be counted rather than guessed?
4. Should the review stay at these twelve families, or go deeper on one (for example large language model extraction) for the paper?

## References

Angeli, G., Johnson Premkumar, M. J., & Manning, C. D. (2015). Leveraging linguistic structure for open domain information extraction. In *Proceedings of the 53rd Annual Meeting of the Association for Computational Linguistics* (pp. 344-354). https://doi.org/10.3115/v1/P15-1034

Auer, S., Bizer, C., Kobilarov, G., Lehmann, J., Cyganiak, R., & Ives, Z. (2007). DBpedia: A nucleus for a web of open data. In *The Semantic Web* (Lecture Notes in Computer Science, pp. 722-735). Springer. https://doi.org/10.1007/978-3-540-76298-0_52

Bosselut, A., Rashkin, H., Sap, M., Malaviya, C., Celikyilmaz, A., & Choi, Y. (2019). COMET: Commonsense transformers for automatic knowledge graph construction. In *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics* (pp. 4762-4779). https://doi.org/10.18653/v1/P19-1470

Carlson, A., Betteridge, J., Kisiel, B., Settles, B., Hruschka, E. R., & Mitchell, T. M. (2010). Toward an architecture for never-ending language learning. *Proceedings of the AAAI Conference on Artificial Intelligence, 24*(1), 1306-1313. https://doi.org/10.1609/aaai.v24i1.7519

Chickering, D. M. (2002). Optimal structure identification with greedy search. *Journal of Machine Learning Research, 3*, 507-554.

Dong, X., Gabrilovich, E., Heitz, G., Horn, W., Lao, N., Murphy, K., Strohmann, T., Sun, S., & Zhang, W. (2014). Knowledge vault: A web-scale approach to probabilistic knowledge fusion. In *Proceedings of the 20th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 601-610). https://doi.org/10.1145/2623330.2623623

Edge, D., Trinh, H., Cheng, N., Bradley, J., Chao, A., Mody, A., Truitt, S., Metropolitansky, D., Ness, R. O., & Larson, J. (2024). *From local to global: A graph RAG approach to query-focused summarization* (arXiv:2404.16130). arXiv. https://doi.org/10.48550/arXiv.2404.16130

Etzioni, O., Banko, M., Soderland, S., & Weld, D. S. (2008). Open information extraction from the web. *Communications of the ACM, 51*(12), 68-74. https://doi.org/10.1145/1409360.1409378

Fader, A., Soderland, S., & Etzioni, O. (2011). Identifying relations for open information extraction. In *Proceedings of the 2011 Conference on Empirical Methods in Natural Language Processing* (pp. 1535-1545). Association for Computational Linguistics. https://aclanthology.org/D11-1142/

Falke, T., & Gurevych, I. (2017). Bringing structure into summaries: Crowdsourcing a benchmark corpus of concept maps. In *Proceedings of the 2017 Conference on Empirical Methods in Natural Language Processing* (pp. 2951-2961). https://doi.org/10.18653/v1/D17-1320

Hearst, M. A. (1992). Automatic acquisition of hyponyms from large text corpora. In *Proceedings of the 14th Conference on Computational Linguistics* (Vol. 2, pp. 539-545). https://doi.org/10.3115/992133.992154

Hogan, A., Blomqvist, E., Cochez, M., d'Amato, C., de Melo, G., Gutierrez, C., Kirrane, S., Labra Gayo, J. E., Navigli, R., Neumaier, S., Ngonga Ngomo, A.-C., Polleres, A., Rashid, S. M., Rula, A., Schmelzeisen, L., Sequeda, J., Staab, S., & Zimmermann, A. (2021). Knowledge graphs. *ACM Computing Surveys, 54*(4), 1-37. https://doi.org/10.1145/3447772

Ji, S., Pan, S., Cambria, E., Marttinen, P., & Yu, P. S. (2022). A survey on knowledge graphs: Representation, acquisition, and applications. *IEEE Transactions on Neural Networks and Learning Systems, 33*(2), 494-514. https://doi.org/10.1109/TNNLS.2021.3070843

Koller, D., & Friedman, N. (2009). *Probabilistic graphical models: Principles and techniques*. MIT Press.

Liang, C., Wu, Z., Huang, W., & Giles, C. L. (2015). Measuring prerequisite relations among concepts. In *Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing* (pp. 1668-1674). https://doi.org/10.18653/v1/D15-1193

Mihalcea, R., & Tarau, P. (2004). TextRank: Bringing order into text. In *Proceedings of the 2004 Conference on Empirical Methods in Natural Language Processing* (pp. 404-411). Association for Computational Linguistics. https://aclanthology.org/W04-3252/

Mintz, M., Bills, S., Snow, R., & Jurafsky, D. (2009). Distant supervision for relation extraction without labeled data. In *Proceedings of the Joint Conference of the 47th Annual Meeting of the ACL and the 4th International Joint Conference on Natural Language Processing of the AFNLP* (Vol. 2, pp. 1003-1011). https://doi.org/10.3115/1690219.1690287

Mitchell, T., Cohen, W., Hruschka, E., Talukdar, P., Yang, B., Betteridge, J., Carlson, A., Dalvi, B., Gardner, M., Kisiel, B., Krishnamurthy, J., Lao, N., Mazaitis, K., Mohamed, T., Nakashole, N., Platanios, E., Ritter, A., Samadi, M., Settles, B., ... Welling, J. (2018). Never-ending learning. *Communications of the ACM, 61*(5), 103-115. https://doi.org/10.1145/3191513

Novak, J. D., & Cañas, A. J. (2008). *The theory underlying concept maps and how to construct and use them* (Technical Report IHMC CmapTools 2006-01 Rev 01-2008). Florida Institute for Human and Machine Cognition. (Technical report, not on Crossref.)

Noy, N. F., & McGuinness, D. L. (2001). *Ontology development 101: A guide to creating your first ontology* (Technical Report KSL-01-05). Stanford Knowledge Systems Laboratory. (Technical report, not on Crossref.)

Pan, S., Luo, L., Wang, Y., Chen, C., Wang, J., & Wu, X. (2024). Unifying large language models and knowledge graphs: A roadmap. *IEEE Transactions on Knowledge and Data Engineering, 36*(7), 3580-3599. https://doi.org/10.1109/TKDE.2024.3352100

Paulheim, H. (2017). Knowledge graph refinement: A survey of approaches and evaluation methods. *Semantic Web, 8*(3), 489-508. https://doi.org/10.3233/SW-160218

Ruijters, E., & Stoelinga, M. (2015). Fault tree analysis: A survey of the state-of-the-art in modeling, analysis and tools. *Computer Science Review, 15-16*, 29-62. https://doi.org/10.1016/j.cosrev.2015.03.001

Speer, R., Chin, J., & Havasi, C. (2017). ConceptNet 5.5: An open multilingual graph of general knowledge. *Proceedings of the AAAI Conference on Artificial Intelligence, 31*(1). https://doi.org/10.1609/aaai.v31i1.11164

Spirtes, P., Glymour, C., & Scheines, R. (2001). *Causation, prediction, and search* (2nd ed.). MIT Press. https://doi.org/10.7551/mitpress/1754.001.0001

Suchanek, F. M., Kasneci, G., & Weikum, G. (2007). YAGO: A core of semantic knowledge. In *Proceedings of the 16th International Conference on World Wide Web* (pp. 697-706). https://doi.org/10.1145/1242572.1242667

Traag, V. A., Waltman, L., & van Eck, N. J. (2019). From Louvain to Leiden: Guaranteeing well-connected communities. *Scientific Reports, 9*, Article 5233. https://doi.org/10.1038/s41598-019-41695-z

Zhong, L., Wu, J., Li, Q., Peng, H., & Wu, X. (2023). A comprehensive survey on automatic knowledge graph construction. *ACM Computing Surveys, 56*(4), 1-62. https://doi.org/10.1145/3618295

Zhu, Y., Wang, X., Chen, J., Qiao, S., Ou, Y., Yao, Y., Deng, S., Chen, H., & Zhang, N. (2024). LLMs for knowledge graph construction and reasoning: Recent capabilities and future opportunities. *World Wide Web, 27*(5), Article 58. https://doi.org/10.1007/s11280-024-01297-w
