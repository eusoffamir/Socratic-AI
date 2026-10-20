// Proposal defence deck for Socratic AI (26S005), in the UTP style of the senior's deck.
// Run: node build.js <figDir> <shotDir> <out.pptx>
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const [FIG, SHOT, OUT] = process.argv.slice(2);
const HERE = __dirname;
// Speaker notes come from script.json (the defence script), so the notes and the script stay in step.
const SCRIPT = JSON.parse(fs.readFileSync(path.join(HERE, "script.json"), "utf8"));
const C = {
  navy: "07517A", navyDark: "053A58", navyLight: "DCEAF2", gold: "7A6E3C", goldLight: "F3EEDC",
  ink: "111827", grey: "4B5563", line: "CBD5E1", white: "FFFFFF", bg: "F7F9FB", green: "166534",
};
const F = "Arial";
const W = 13.333, M = 0.55;

function pngSize(file) { const b = fs.readFileSync(file); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
function fit(file, maxW, maxH) {
  const s = pngSize(file); let w = maxW, h = (maxW * s.h) / s.w;
  if (h > maxH) { h = maxH; w = (maxH * s.w) / s.h; }
  return { w, h };
}

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Socratic AI: FYP 1 Proposal Defence";
let n = 0;

function stripes(s, y) {
  s.addShape(pres.shapes.RECTANGLE, { x: 0.25, y, w: 4.1, h: 0.06, fill: { color: C.navy }, line: { color: C.navy } });
  s.addShape(pres.shapes.RECTANGLE, { x: 4.5, y, w: 4.3, h: 0.06, fill: { color: C.gold }, line: { color: C.gold } });
  s.addShape(pres.shapes.RECTANGLE, { x: 8.95, y, w: 4.13, h: 0.06, fill: { color: C.navy }, line: { color: C.navy } });
}
function base(title) {
  const s = pres.addSlide(); n += 1;
  s.background = { color: C.white };
  s.addImage({ path: path.join(HERE, "utp_logo_wide.png"), x: 0.25, y: 0.1, w: 1.55, h: 0.647 });
  s.addShape(pres.shapes.RECTANGLE, { x: 2.0, y: 0.12, w: W - 2.0, h: 0.62, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText(title.toUpperCase(), { x: 2.25, y: 0.12, w: W - 2.5, h: 0.62, fontFace: F, fontSize: 22, bold: true, color: C.white, valign: "middle", margin: 0 });
  stripes(s, 0.84);
  s.addText(String(n), { x: W - 0.9, y: 7.08, w: 0.5, h: 0.28, fontFace: F, fontSize: 10, color: C.grey, align: "right", margin: 0 });
  return s;
}
function circle(s, x, y, d, label, fill = C.navy, color = C.white, size = 15) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  s.addText(label, { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: F, fontSize: size, bold: true, color, margin: 0 });
}
function card(s, x, y, w, h, fill = C.bg, line = C.line) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill }, line: { color: line, width: 1 } });
}
function pill(s, x, y, w, text, fill = C.navyLight, color = C.navy, size = 14) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.42, rectRadius: 0.2, fill: { color: fill }, line: { color: fill } });
  s.addText(text, { x, y, w, h: 0.42, fontFace: F, fontSize: size, bold: true, color, align: "center", valign: "middle", margin: 0 });
}
function bullets(s, items, x, y, w, h, size = 15, color = C.ink) {
  s.addText(items.map((t, i) => {
    const runs = Array.isArray(t) ? t : [t];
    return { text: runs.join(""), options: { bullet: true, breakLine: i < items.length - 1 } };
  }), { x, y, w, h, fontFace: F, fontSize: size, color, valign: "top", paraSpaceAfter: 7, margin: 0 });
}
function shot(s, file, x, y, w, h) {
  const f = path.join(SHOT, file), sz = fit(f, w, h);
  s.addShape(pres.shapes.RECTANGLE, { x: x - 0.03, y: y - 0.03, w: sz.w + 0.06, h: sz.h + 0.06, fill: { color: C.line }, line: { color: C.line } });
  s.addImage({ path: f, x, y, w: sz.w, h: sz.h });
  return sz;
}
function table(s, hdr, rows, opts) {
  const cell = (t, o = {}) => ({ text: t, options: { fontFace: F, fontSize: opts.size || 12, color: C.ink, valign: "middle", ...o } });
  const data = [hdr.map((h) => cell(h, { bold: true, color: C.white, fill: { color: C.navy }, align: "center" }))];
  rows.forEach((r, i) => data.push(r.map((t, j) => cell(t, {
    bold: j === 0 || (opts.boldLast && i === rows.length - 1),
    align: opts.center && opts.center.includes(j) ? "center" : "left",
    fill: { color: opts.boldLast && i === rows.length - 1 ? C.goldLight : (i % 2 ? C.white : C.bg) },
  }))));
  s.addTable(data, { x: opts.x, y: opts.y, w: opts.w, colW: opts.colW, rowH: opts.rowH, border: { type: "solid", pt: 0.75, color: C.line }, margin: 0.06 });
}

// 1. Cover
{
  const s = pres.addSlide(); n += 1;
  s.background = { color: C.white };
  stripes(s, 0.2);
  s.addImage({ path: path.join(HERE, "utp_logo_cover.jpeg"), x: 0.55, y: 1.25, w: 2.6, h: 2.6 });
  s.addText("Proposal Defense", { x: 3.6, y: 0.75, w: 9, h: 0.45, fontFace: F, fontSize: 18, color: C.navy, margin: 0 });
  s.addText("Socratic AI: Agentic AI for Fostering Critical Thinking Education", { x: 3.6, y: 1.25, w: 9.2, h: 1.35, fontFace: F, fontSize: 30, bold: true, color: C.navy, margin: 0, valign: "top" });
  s.addText("A multi-agent tutor that asks instead of answers, and measures how well the learner reasons", { x: 3.6, y: 2.65, w: 9.2, h: 0.5, fontFace: F, fontSize: 16, italic: true, color: C.gold, margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.6, y: 3.45, w: 9.2, h: 3.55, fill: { color: C.navy }, line: { color: C.navy } });
  const rows = ["Presented by : Muhammad Eusoff Amir bin Hazri (22010491)", "Supervised by : Dr Ho Tatt Wei", "Department : Electrical and Electronics Engineering",
    "Course : EFB4042 Final Year Project I", "Project code : 26S005", "Date : 21st October 2026"];
  s.addText(rows.map((t, i) => ({ text: t, options: { breakLine: i < rows.length - 1 } })),
    { x: 3.9, y: 3.6, w: 8.7, h: 3.25, fontFace: F, fontSize: 15, color: C.white, valign: "middle", paraSpaceAfter: 9, margin: 0 });
  s.addNotes(SCRIPT[n].text || "Good afternoon. My name is Eusoff, and my supervisor is Dr Ho Tatt Wei. My project is Socratic AI, an AI tutor that does not give answers. It asks questions step by step and measures how well the student reasons.");
}

// 2. Outline
{
  const s = base("Outline of Presentation");
  const items = ["Introduction", "Problem Statement, Objectives, Scope of Study", "Literature Review", "Proposed Methodology",
    "Gantt Chart & Milestones", "Preliminary Results", "Conclusion"];
  items.forEach((t, i) => {
    const y = 1.3 + i * 0.8;
    circle(s, 1.2, y, 0.58, String(i + 1));
    s.addText(t, { x: 2.05, y, w: 6.5, h: 0.58, fontFace: F, fontSize: 20, color: C.ink, valign: "middle", margin: 0 });
  });
  shot(s, "01_home.png", 8.1, 1.45, 4.7, 4.6);
  s.addText("The working prototype, live online", { x: 8.1, y: 4.35, w: 4.7, h: 0.35, fontFace: F, fontSize: 12, italic: true, color: C.grey, align: "center", margin: 0 });
  s.addNotes(SCRIPT[n].text || "This is my outline. I will cover the introduction, the problem, objectives and scope, the literature, my methodology, the timeline, my first results and the conclusion. On the right is the working app, which is already online.");
}

// 3. Introduction
{
  const s = base("Introduction");
  s.addText("Generative AI now gives students a finished answer in seconds, so they can skip the thinking.", { x: M, y: 1.15, w: W - 2 * M, h: 0.5, fontFace: F, fontSize: 18, bold: true, color: C.ink, margin: 0 });
  const stats = [["62%", "of students use generative AI at least weekly [12]"],
    ["319", "knowledge workers studied: more trust in AI meant less critical thinking [10]"],
    ["4", "costs of \"outsourced reasoning\": fewer ideas, less effort, weaker memory, less reflection [11]"]];
  stats.forEach(([big, txt], i) => {
    const x = M + i * 4.12;
    card(s, x, 1.85, 3.88, 2.6);
    s.addText(big, { x: x + 0.25, y: 1.95, w: 3.4, h: 1.05, fontFace: F, fontSize: 50, bold: true, color: C.navy, margin: 0 });
    s.addText(txt, { x: x + 0.25, y: 3.05, w: 3.4, h: 1.25, fontFace: F, fontSize: 15, color: C.ink, valign: "top", margin: 0 });
  });
  card(s, M, 4.75, W - 2 * M, 2.1, C.goldLight, C.goldLight);
  s.addText([
    { text: "The idea of this project", options: { bold: true, color: C.gold, breakLine: true } },
    { text: "Turn the same AI around. Instead of an answer machine, build a tutor that asks Socratic questions in a set order, so the learner builds the understanding, and then measure the quality of the learner's reasoning against a framework.", options: {} },
  ], { x: M + 0.3, y: 4.85, w: W - 2 * M - 0.6, h: 1.9, fontFace: F, fontSize: 17, color: C.ink, valign: "middle", margin: 0, paraSpaceAfter: 6 });
  s.addNotes(SCRIPT[n].text || "Students can now ask an AI for a finished answer and copy it. A QS report found 62 percent of students use generative AI every week, and a study of 319 workers found that people who trust AI more think less critically. My idea is to use the same AI the other way round: a tutor that asks questions in a set order, and that measures how well the student reasons.");
}

// 4. Problem statement
{
  const s = base("Problem Statement");
  s.addText("Students increasingly hand their thinking to generative AI, and studies link this to weaker critical thinking [10]. Socratic AI tutors can refuse to give answers, but they share three gaps.",
    { x: M, y: 1.1, w: W - 2 * M, h: 0.65, fontFace: F, fontSize: 16, color: C.ink, margin: 0 });
  const probs = [["No ladder", "Questions only lead toward an answer, so learners are never pushed to ask whether they are asking the right question."],
    ["No measurement", "They do not measure the learner's critical thinking against any framework."],
    ["No adaptation", "They do not adapt to what each learner is missing."]];
  probs.forEach(([h, t], i) => {
    const x = M + i * 4.12;
    card(s, x, 1.9, 3.88, 2.65);
    circle(s, x + 0.25, 2.1, 0.58, String(i + 1), C.gold);
    s.addText(h, { x: x + 0.25, y: 2.8, w: 3.4, h: 0.5, fontFace: F, fontSize: 20, bold: true, color: C.navy, margin: 0 });
    s.addText(t, { x: x + 0.25, y: 3.35, w: 3.4, h: 1.15, fontFace: F, fontSize: 15, color: C.ink, valign: "top", margin: 0 });
  });
  s.addShape(pres.shapes.RECTANGLE, { x: M, y: 4.85, w: W - 2 * M, h: 1.95, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText([
    { text: "Seen in early testing of two Gemini Gem tutors:  ", options: { bold: true, color: "BFD7E6" } },
    { text: "\"bro i explained this before\"", options: { italic: true, color: C.white, breakLine: true } },
    { text: "As a result, neither the learner nor the lecturer can tell whether critical thinking is actually improving.", options: { bold: true, color: C.white } },
  ], { x: M + 0.3, y: 4.95, w: W - 2 * M - 0.6, h: 1.75, fontFace: F, fontSize: 17, valign: "middle", margin: 0, paraSpaceAfter: 8 });
  s.addNotes(SCRIPT[n].text || "");
}

// 5. Objectives (3, written as end states)
{
  const s = base("Objectives");
  const obj = [
    ["Teach", "Undergraduates new to a topic build their own reasoning, guided step by step up Paul's six levels of Socratic questioning, without being given the answers."],
    ["Assess", "Each learner's critical thinking attainment is measured from the conversation against the Paul-Elder framework (the nine standards, plus the type of reasoning and knowledge used), with marks that agree with human markers."],
    ["Adapt", "The support and difficulty match each learner's gaps, and the learner can see what they have mastered and what to work on next."],
  ];
  obj.forEach(([h, t], i) => {
    const y = 1.2 + i * 1.6;
    circle(s, M + 0.1, y + 0.3, 0.75, String(i + 1), C.navy, C.white, 22);
    card(s, M + 1.1, y, W - 2 * M - 1.1, 1.38);
    s.addText(h, { x: M + 1.35, y, w: 1.6, h: 1.38, fontFace: F, fontSize: 20, bold: true, color: C.navy, valign: "middle", margin: 0 });
    s.addText(t, { x: M + 3.0, y, w: W - 2 * M - 3.25, h: 1.38, fontFace: F, fontSize: 16, color: C.ink, valign: "middle", margin: 0 });
  });
  s.addText("These match the three objectives and deliverables in the official project listing (26S005).",
    { x: M, y: 6.1, w: W - 2 * M, h: 0.4, fontFace: F, fontSize: 13, italic: true, color: C.grey, margin: 0 });
  s.addNotes(SCRIPT[n].text || "");
}

// 6. Scope
{
  const s = base("Scope of Study");
  const items = [
    ["One quant topic", "Telling a real pattern in data from luck, for beginners, with no complex machine learning. Three short cases."],
    ["Multi-agent tutor", "Four AI agents (Assessor, Planner, Tutor, Checker) guarded by plain-code rules, on the free Gemini model."],
    ["Framework assessment", "6 Socratic levels and 9 standards now, then reasoning type and knowledge type, with a learner dashboard."],
  ];
  items.forEach(([h, t], i) => {
    const x = M + i * 4.12;
    circle(s, x + 1.6, 1.2, 0.6, String(i + 1), C.white, C.navy, 16);
    s.addShape(pres.shapes.OVAL, { x: x + 1.6, y: 1.2, w: 0.6, h: 0.6, fill: { type: "none" }, line: { color: C.navy, width: 1.5 } });
    card(s, x, 1.95, 3.88, 2.55);
    s.addText(h, { x: x + 0.25, y: 2.1, w: 3.4, h: 0.5, fontFace: F, fontSize: 19, bold: true, color: C.navy, align: "center", margin: 0 });
    s.addText(t, { x: x + 0.25, y: 2.65, w: 3.4, h: 1.75, fontFace: F, fontSize: 15, color: C.ink, align: "center", valign: "top", margin: 0 });
  });
  card(s, M, 4.85, W - 2 * M, 1.95, C.goldLight, C.goldLight);
  s.addText([
    { text: "Target learners: ", options: { bold: true } }, { text: "university students new to quant (early testers are Dr Ho's students).", options: { breakLine: true } },
    { text: "Future work, outside FYP: ", options: { bold: true } }, { text: "a second topic, real reading material with retrieval (RAG) [15], knowledge graphs, and a full class study (needs a paid key and ethics approval)." },
  ], { x: M + 0.3, y: 4.95, w: W - 2 * M - 0.6, h: 1.75, fontFace: F, fontSize: 16, color: C.ink, valign: "middle", margin: 0, paraSpaceAfter: 8 });
  s.addNotes(SCRIPT[n].text || "To keep it small, the prototype covers one quant topic: is a pattern in data real, or just luck. It uses four AI agents guarded by code, and it assesses reasoning against a framework. A second topic, real reading material and knowledge graphs are future work.");
}

// 6b. Literature review: agentic AI building blocks (Dr Ho's course modules)
{
  const s = base("Literature Review");
  pill(s, M, 1.05, 4.6, "Agentic AI Building Blocks");
  table(s, ["Technique", "Year", "Core idea", "Use in this project", "Ref"], [
    ["Prompting", "2025", "A prompt is an instruction plus context; output depends on how the context is built", "Every agent gets a structured JSON prompt", "[16]"],
    ["Chain of Thought", "2022", "Break a task into intermediate reasoning steps", "The Planner reasons before choosing the next move", "[17]"],
    ["ReAct", "2023", "Reason, act, observe, then repeat", "The Tutor runs a simulation, reads the result, then replies", "[18]"],
    ["RAG", "2023", "Ground answers in retrieved knowledge (naive, advanced, modular)", "Case notes now; real RAG and knowledge graphs are future work", "[15], [19]"],
    ["Model Context Protocol", "2024", "A standard way to give an LLM tools, resources and prompts", "Future: query a knowledge graph and learner records", "[20]"],
    ["Multi-agent systems", "2024", "Specialised agents collaborate (MetaGPT, AgileCoder)", "Assessor, Planner, Tutor and Checker roles", "[21], [22]"],
  ], { x: M, y: 1.65, w: W - 2 * M, colW: [2.3, 0.75, 4.2, 4.0, 0.98], rowH: 0.64, size: 12, center: [1, 4] });
  s.addText("Based on the supervisor's course slides [16], [23] and the DeepLearning.AI short courses he recommended [24].",
    { x: M, y: 6.7, w: W - 2 * M, h: 0.32, fontFace: F, fontSize: 12, italic: true, color: C.grey, margin: 0 });
  s.addNotes(SCRIPT[n].text || "The agentic AI building blocks come from Dr Ho's course modules. Each technique maps to a part of my system: Chain of Thought in the Planner, ReAct in the Tutor's simulation loop, and multi-agent systems in the four agent roles. RAG and MCP are future work.");
}

// 7. Literature review 1: frameworks
{
  const s = base("Literature Review");
  pill(s, M, 1.05, 4.6, "Frameworks for Critical Thinking");
  table(s, ["Framework", "Year", "Core idea", "Role in this project", "Limitation", "Ref"], [
    ["Paul's 6 Socratic question levels", "-", "Clarify, assumptions, evidence, viewpoints, implications, question the question", "The ladder: what the Tutor asks next", "Says what to ask, not how good the answer is", "[1]"],
    ["Paul-Elder 9 intellectual standards", "-", "Clarity, accuracy, precision, relevance, depth, breadth, logic, significance, fairness", "The Assessor marks each as 1 or 0", "Does not say which type of reasoning was used", "[1]"],
    ["Paul-Elder 8 elements of thought", "-", "Purpose, question, information, inference, concepts, assumptions, implications, point of view", "Prerequisites before reasoning (planned)", "Links to reasoning types still open", "[1]"],
    ["Revised Bloom's taxonomy", "2001", "Knowledge dimension: factual, conceptual, procedural, metacognitive", "Types of knowledge used (planned)", "No causal or relational type", "[2]"],
    ["SOLO taxonomy", "1982", "Prestructural to extended abstract outcomes", "Complexity: how many knowledge types are joined", "Needs adapting to dialogue", "[3]"],
  ], { x: M, y: 1.65, w: W - 2 * M, colW: [2.45, 0.65, 3.35, 2.6, 2.6, 0.58], rowH: 0.86, size: 12, center: [1, 5] });
  s.addNotes(SCRIPT[n].text || "The literature gives several frameworks. From Paul and Elder, the six question levels tell the tutor what to ask, and the nine standards tell the assessor how good the answer is. The eight elements of thought, the revised Bloom's taxonomy and the SOLO taxonomy will add the type of knowledge and the complexity, in the next stage.");
}

// 8. Literature review 2: empirical studies
{
  const s = base("Literature Review");
  pill(s, M, 1.05, 4.6, "Socratic Questioning and Socratic AI");
  table(s, ["Study", "Year", "Setting", "Main finding", "Limitation", "Ref"], [
    ["Sahamid", "2016", "Classroom action research", "Socratic questioning built critical thinking", "Small, one class", "[4]"],
    ["Makhene", "2019", "Nursing education", "Socratic inquiry helps critical thinking", "Needs skilled teachers' time", "[5]"],
    ["Ho, Chen and Li", "2023", "Healthcare students", "Socratic method improved thinking skills", "Human tutor, does not scale", "[6]"],
    ["Degen and Asanov", "2025", "65 pre-service teachers, Socratic AI vs plain chatbot", "More support for critical, reflective thinking; argues for multi-agent systems", "Self-reported, not a direct measure", "[7]"],
    ["Fan", "2025", "Socratic scaffolding through AI", "Structured scaffolding deepened inquiry", "No link to reasoning constructs", "[8]"],
    ["Lee, Ang and Lai", "2025", "Bloom labels on chatbot dialogues", "Dialogue logs reveal thinking processes", "Descriptive only", "[9]"],
    ["Lee et al. (CHI)", "2025", "319 knowledge workers", "More AI trust, less critical thinking", "Survey, self-reported", "[10]"],
  ], { x: M, y: 1.65, w: W - 2 * M, colW: [2.1, 0.7, 2.9, 3.6, 2.35, 0.58], rowH: 0.68, size: 12, center: [1, 5] });
  s.addNotes(SCRIPT[n].text || "Studies in education, nursing and healthcare show that Socratic questioning improves reasoning, but a human tutor cannot do it for every student. AI can do it at scale. Degen and Asanov in 2025 found a Socratic AI tutor gave more support for reflective thinking than a plain chatbot, and they argue for multi-agent systems. But most of this work is self-reported, and it does not measure the reasoning directly.");
}

// 9. Literature review 3: existing tools
{
  const s = base("Literature Review");
  pill(s, M, 1.05, 4.6, "Existing Socratic AI Tutors");
  table(s, ["Tool", "Refuses answers", "Question ladder", "Framework assessment", "Goal, progress, end", "Reasoning and knowledge types"], [
    ["Online Gemini Gem \"Socratic Tutor\" (Test #1)", "Yes", "No", "No (informal points)", "No", "No"],
    ["Project prompt v1 (Test #2)", "Yes", "Partly", "Partly (hidden 1 to 3 score)", "No", "No"],
    ["Khanmigo, custom GPTs *", "Yes", "Not shown", "Not shown", "Partly", "No"],
    ["Socratic AI (this project)", "Yes", "Yes, 6 levels", "Yes, 9 standards", "Yes", "Planned"],
  ], { x: M, y: 1.7, w: W - 2 * M, colW: [3.6, 1.6, 1.6, 2.15, 1.65, 1.63], rowH: 0.85, size: 14, center: [1, 2, 3, 4, 5], boldLast: true });
  s.addText("* From public descriptions, not tested in this project.", { x: M, y: 5.95, w: 9, h: 0.35, fontFace: F, fontSize: 12, italic: true, color: C.grey, margin: 0 });
  s.addText("No tested tool combines a question ladder, framework assessment and a clear session, and none shows which type of reasoning a learner used.",
    { x: M, y: 6.35, w: W - 2 * M, h: 0.7, fontFace: F, fontSize: 16, bold: true, color: C.navy, margin: 0 });
  s.addNotes(SCRIPT[n].text || "Here is the comparison of existing tutors. They refuse to give answers, but none combine a principled question ladder, assessment against a framework, and a clear goal with progress and an end. None show which type of reasoning the learner used. Socratic AI covers these, and the last column is the next stage.");
}

// 10. Research gap and justification
{
  const s = base("Literature Review");
  const colW = (W - 2 * M - 0.35) / 2;
  s.addShape(pres.shapes.RECTANGLE, { x: M, y: 1.15, w: colW, h: 5.7, fill: { color: C.gold }, line: { color: C.gold } });
  s.addText("RESEARCH GAP", { x: M + 0.3, y: 1.3, w: colW - 0.6, h: 0.5, fontFace: F, fontSize: 18, bold: true, color: C.white, margin: 0 });
  bullets(s, [
    "AI use can reduce critical thinking effort, and current tutors are mostly answer machines.",
    "Socratic AI tutors are promising, but their questions have no principled ladder.",
    "Reasoning is rarely measured against a defined framework, and evidence is mostly self-reported.",
    "No tool shows the learner which type of reasoning or knowledge they used.",
  ], M + 0.3, 1.95, colW - 0.6, 4.7, 16, C.white);
  const x2 = M + colW + 0.35;
  s.addShape(pres.shapes.RECTANGLE, { x: x2, y: 1.15, w: colW, h: 5.7, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("JUSTIFICATION", { x: x2 + 0.3, y: 1.3, w: colW - 0.6, h: 0.5, fontFace: F, fontSize: 18, bold: true, color: C.white, margin: 0 });
  bullets(s, [
    "A multi-agent tutor where the Tutor follows Paul's six levels, so questions climb in a set order.",
    "A separate Assessor marks every answer against the nine standards, with evidence, so it can be checked against human markers.",
    "Plain-code rules guard every AI decision, so steps are fair and testable (\"agents decide, rules guard\").",
    "Next, new agents add reasoning type and knowledge type, measured over many questions.",
  ], x2 + 0.3, 1.95, colW - 0.6, 4.7, 16, C.white);
  s.addNotes(SCRIPT[n].text || "So the gap is this. AI can reduce thinking, Socratic tutors have no principled ladder, reasoning is rarely measured against a framework, and no tool shows which type of reasoning a learner used. My project answers each point: a tutor that follows the six levels, a separate assessor marking the nine standards, code rules guarding the AI, and next, reasoning and knowledge types.");
}

// 11. Methodology: phases + environment
{
  const s = base("Proposed Methodology");
  const ph = [["Phase 1", "Early testing", "Two Gemini Gem tutors tested; problems written down"],
    ["Phase 2", "Requirements", "9 design requirements R1 to R9 from the tests"],
    ["Phase 3", "Build", "4 agents, rules, 3 cases, simulations, web app"],
    ["Phase 4", "Test and fix", "Real sessions read turn by turn; problems fixed"],
    ["Phase 5", "Evaluate", "Requirements, Assessor vs humans, learners"]];
  s.addShape(pres.shapes.RIGHT_ARROW, { x: M, y: 2.35, w: 9.3, h: 0.7, fill: { color: C.navy }, line: { color: C.navy } });
  ph.forEach(([p, h, t], i) => {
    const x = M + 0.1 + i * 1.82;
    pill(s, x, 1.4, 1.65, p, C.goldLight, C.gold);
    s.addShape(pres.shapes.OVAL, { x: x + 0.66, y: 2.53, w: 0.34, h: 0.34, fill: { color: C.white }, line: { color: C.gold, width: 2 } });
    s.addText(h, { x, y: 3.25, w: 1.7, h: 0.4, fontFace: F, fontSize: 15, bold: true, color: C.navy, align: "center", margin: 0 });
    s.addText(t, { x, y: 3.65, w: 1.7, h: 1.2, fontFace: F, fontSize: 12, color: C.ink, align: "center", valign: "top", margin: 0 });
  });
  const reqs = ["R1 Clear mission", "R2 Fixed rounds, progress", "R3 Remember, never re-ask", "R4 Feedback and teaching",
    "R5 Notice frustration", "R6 Vary formats", "R7 Separate assessor", "R8 Learner stats", "R9 Stable topic"];
  reqs.forEach((t, i) => {
    const x = M + (i % 3) * 3.12, y = 5.0 + Math.floor(i / 3) * 0.62;
    card(s, x, y, 2.98, 0.5);
    s.addText(t, { x: x + 0.15, y, w: 2.75, h: 0.5, fontFace: F, fontSize: 12.5, color: C.ink, valign: "middle", margin: 0 });
  });
  const ex = 10.2, ew = W - ex - M;
  card(s, ex, 1.25, ew, 5.6, C.navyLight, C.navyLight);
  s.addText([
    { text: "Software", options: { bold: true, color: C.navy, breakLine: true } },
    { text: "Python 3.13, FastAPI, LangGraph", options: { bullet: true, breakLine: true } },
    { text: "Gemini 3.5 Flash Lite (free tier)", options: { bullet: true, breakLine: true } },
    { text: "HTML and JavaScript front end", options: { bullet: true, breakLine: true } },
    { text: "Supabase database, Render hosting (free)", options: { bullet: true, breakLine: true } },
    { text: "pytest: 94 automatic tests", options: { bullet: true, breakLine: true } },
    { text: "Hardware", options: { bold: true, color: C.navy, breakLine: true } },
    { text: "A normal laptop; the AI runs in the cloud, so no GPU is needed", options: { bullet: true } },
  ], { x: ex + 0.2, y: 1.4, w: ew - 0.35, h: 5.3, fontFace: F, fontSize: 13, color: C.ink, valign: "top", paraSpaceAfter: 6, margin: 0 });
  s.addNotes(SCRIPT[n].text || "My method is iterative prototyping in five phases. I tested existing tutors, turned what failed into nine design requirements, built the prototype, tested it with real sessions and fixed what broke, and next I evaluate it. It uses Python, FastAPI, LangGraph and the free Gemini model, and it is hosted for free. No GPU is needed, because the AI runs in the cloud.");
}

// 12. Methodology: architecture
{
  const s = base("Proposed Methodology");
  pill(s, M, 1.05, 4.9, "System Architecture: Agents Decide, Rules Guard");
  const f = path.join(FIG, "agent_flow.png"), sz = fit(f, 5.4, 5.6);
  s.addImage({ path: f, x: M, y: 1.6, w: sz.w, h: sz.h });
  const x2 = M + sz.w + 0.45, w2 = W - x2 - M;
  const pts = [["Assessor", "marks each answer, 9 standards as 1 or 0, with an evidence quote"],
    ["Planner", "proposes the next level, question format, hint and simulation"],
    ["Rules (code)", "a frustrated learner always gets an easy A or B question; no level up after a weak answer"],
    ["Tutor", "short feedback, a hidden hint, one question; may run a quant simulation"],
    ["Checker", "stops replies that give away the answer or repeat a question"],
    ["Coach", "one comment at the end on how the learner answered"]];
  pts.forEach(([h, t], i) => {
    const y = 1.6 + i * 0.8;
    circle(s, x2, y + 0.1, 0.48, String(i + 1), h.startsWith("Rules") ? C.gold : C.navy, C.white, 13);
    s.addText([{ text: h + ": ", options: { bold: true, color: C.navy } }, { text: t }],
      { x: x2 + 0.65, y, w: w2 - 0.65, h: 0.7, fontFace: F, fontSize: 14, color: C.ink, valign: "middle", margin: 0 });
  });
  s.addText("Each agent gets a small JSON payload built by code and must reply in a fixed JSON shape. About 25 AI calls per 6-round session.",
    { x: x2, y: 6.5, w: w2, h: 0.5, fontFace: F, fontSize: 12, italic: true, color: C.grey, margin: 0 });
  s.addNotes(SCRIPT[n].text || "This is the heart of the system. Every answer goes through these steps. The Assessor marks it. The Planner proposes the next move. Then plain code rules check the plan, so the AI cannot break important rules. The Tutor writes the reply and may run a small simulation, and the Checker reviews it before the learner sees it. So the agents decide, and the rules guard.");
}

// 13. Methodology: session design with screenshots
{
  const s = base("Proposed Methodology");
  pill(s, M, 1.05, 3.6, "Session Design (R1 to R9)");
  const a = shot(s, "02_reading.png", M, 1.65, 6.0, 3.7);
  shot(s, "04_chat.png", M + 6.25, 1.65, 6.0, 3.7);
  s.addText("1. A short reading and a mission before each case", { x: M, y: 1.7 + a.h, w: 6.0, h: 0.35, fontFace: F, fontSize: 12, italic: true, color: C.grey, margin: 0 });
  s.addText("2. Feedback, one question, a hidden hint, and a simulation result", { x: M + 6.25, y: 1.7 + a.h, w: 6.0, h: 0.35, fontFace: F, fontSize: 12, italic: true, color: C.grey, margin: 0 });
  const feats = ["3, 6 or no-limit rounds", "Round and level shown", "4 question formats", "\"I'm not sure\" button", "Status panel", "Tutorial"];
  feats.forEach((t, i) => pill(s, M + i * 2.06, 6.35, 1.95, t, C.navyLight, C.navy, 11));
  s.addNotes(SCRIPT[n].text || "This is what the learner sees. On the left, each case starts with a short reading. On the right, a real session: the tutor gives short feedback, one question, a hint that stays hidden until the learner opens it, and here it ran a simulation: out of 500 random stocks, 15 went up every day by luck. Underneath are the other features from the design requirements.");
}

// 14. Methodology: planned framework
{
  const s = base("Proposed Methodology");
  pill(s, M, 1.05, 5.6, "Next Stage (Goal 1): Reasoning and Knowledge Layer");
  const f = path.join(FIG, "framework.png"), sz = fit(f, 7.3, 5.2);
  s.addImage({ path: f, x: M, y: 1.65, w: sz.w, h: sz.h });
  const x2 = M + 7.6, w2 = W - x2 - M;
  bullets(s, [
    "Knowledge layer: each case note tagged with its type of knowledge; an agent drafts a knowledge graph",
    "Reasoning agent: 1 or 0 for inductive, deductive and abductive reasoning and each knowledge type, with evidence",
    "Question bank: several questions per skill, so there are enough trials",
    "Statistics: share of 1s and Hamming distance per learner [14]; factor analysis across learners",
    "Explainer agent: a plain scenario on why a skill matters",
  ], x2, 1.7, w2, 4.6, 14);
  s.addText("Example: \"All the regional banks fell, not just CIMB\" is inductive reasoning on relational knowledge.",
    { x: M, y: 6.5, w: W - 2 * M, h: 0.4, fontFace: F, fontSize: 13, italic: true, color: C.gold, margin: 0 });
  s.addNotes(SCRIPT[n].text || "From my last meeting, Dr Ho and I widened the framework. Navy parts are built, gold parts are planned. Besides quality, we want to know which type of reasoning the student used, like inductive or deductive, and which type of knowledge, like causal or relational. New agents will do this, without rebuilding the old ones. Each skill is measured over several questions, then simple statistics. For example, noticing that all regional banks fell, not just one bank, is inductive reasoning.");
}

// 15. Evaluation plan
{
  const s = base("Proposed Methodology");
  pill(s, M, 1.05, 3.2, "Evaluation Plan");
  const ev = [["Requirement check", "Objective 1", "Run the same scenarios on the baseline Gem tutors and on Socratic AI, and mark R1 to R9 as met or not."],
    ["Assessor vs human markers", "Objective 2", "Mark 61 test answers by hand with a marking guide. Compare using percent agreement and Cohen's kappa per standard (parent grant target 0.8)."],
    ["With and without agents", "All objectives", "Switch the Planner, simulations or Checker off, and compare the same sessions."],
    ["Learner experience", "Objective 3", "A short questionnaire with Dr Ho's students, after ethics approval."]];
  ev.forEach(([h, tag, t], i) => {
    const x = M + (i % 2) * 6.2, y = 1.7 + Math.floor(i / 2) * 2.6;
    card(s, x, y, 5.95, 2.35);
    circle(s, x + 0.25, y + 0.25, 0.58, String(i + 1));
    pill(s, x + 4.15, y + 0.33, 1.6, tag, C.goldLight, C.gold, 11);
    s.addText(h, { x: x + 1.0, y: y + 0.25, w: 3.1, h: 0.58, fontFace: F, fontSize: 18, bold: true, color: C.navy, valign: "middle", margin: 0 });
    s.addText(t, { x: x + 0.25, y: y + 1.0, w: 5.45, h: 1.2, fontFace: F, fontSize: 15, color: C.ink, valign: "top", margin: 0 });
  });
  s.addNotes(SCRIPT[n].text || "I will evaluate in four ways. A requirement check against the baseline tutors. The Assessor against human markers using Cohen's kappa, where the parent grant targets 0.8. Switching agents on and off to see what each one adds. And a short questionnaire with real learners after ethics approval.");
}

// 16. Gantt (week by week, FYP 1 and FYP 2)
{
  const s = base("Gantt Chart & Milestones");
  const f = path.join(FIG, "gantt_weeks.png"), sz = fit(f, W - 2 * M, 4.75);
  s.addImage({ path: f, x: (W - sz.w) / 2, y: 1.2, w: sz.w, h: sz.h });
  const ms = [["21 Oct 2026 (FYP1 W7)", "Proposal defence"], ["16 Nov 2026 (FYP1 W11)", "Product demo, mock presentation"],
    ["7 Dec 2026 (FYP1 W14)", "Interim report"], ["29 Mar 2027 (FYP2 W12)", "Technical paper"], ["12 Apr 2027 (FYP2 W14)", "Dissertation, final presentation"]];
  const y0 = 1.3 + sz.h, cw = (W - 2 * M) / 5;
  ms.forEach(([d, t], i) => {
    const x = M + i * cw;
    s.addShape(pres.shapes.OVAL, { x, y: y0 + 0.08, w: 0.22, h: 0.22, fill: { color: "C00000" }, line: { color: "C00000" } });
    s.addText(d, { x: x + 0.32, y: y0, w: cw - 0.4, h: 0.38, fontFace: F, fontSize: 12, bold: true, color: C.gold, margin: 0 });
    s.addText(t, { x: x + 0.32, y: y0 + 0.38, w: cw - 0.4, h: 0.5, fontFace: F, fontSize: 12, color: C.ink, valign: "top", margin: 0 });
  });
  s.addNotes(SCRIPT[n].text || "This is my timeline, week by week. The green bars are done: the literature review, the Gem tests and the working prototype. This week is the proposal defence. By mid November I add the reasoning and knowledge layer and show a demo, then the interim report. In FYP 2 I validate the Assessor against human markers, build the question bank and statistics, try a second topic, test with learners, and finish with the technical paper and dissertation.");
}

// 17. Preliminary results: a real session
{
  const s = base("Preliminary Results");
  pill(s, M, 1.05, 4.6, "A Real 3-Round Session (Gemini)");
  const a = shot(s, "07_profile.png", M, 1.65, 6.6, 4.6);
  s.addText("End profile: level reached, the 9 standards chart and the Coach comment", { x: M, y: 1.72 + a.h, w: 6.6, h: 0.35, fontFace: F, fontSize: 12, italic: true, color: C.grey, margin: 0 });
  const x2 = M + 6.95, w2 = W - x2 - M;
  const st = [["0", "times the answer was given away, even when asked to ignore the rules"],
    ["5 of 5", "problems found in testing were fixed"], ["~24", "AI calls per session, inside the free tier"]];
  st.forEach(([big, t], i) => {
    const y = 1.65 + i * 1.6;
    card(s, x2, y, w2, 1.4, C.navyLight, C.navyLight);
    s.addText(big, { x: x2 + 0.25, y, w: 1.9, h: 1.4, fontFace: F, fontSize: 34, bold: true, color: C.navy, valign: "middle", margin: 0 });
    s.addText(t, { x: x2 + 2.15, y, w: w2 - 2.35, h: 1.4, fontFace: F, fontSize: 14, color: C.ink, valign: "middle", margin: 0 });
  });
  s.addNotes(SCRIPT[n].text || "These are results from real sessions with Gemini. On the left is the end profile from a real 3-round session: the level reached, the nine standards and the Coach's comment. In my two full test sessions, the tutor never gave the answer away, even when I asked it to ignore its rules. I found five problems and fixed all five, and a session uses about 24 AI calls, which fits the free tier.");
}

// 18. Preliminary results: assessor
{
  const s = base("Preliminary Results");
  pill(s, M, 1.05, 4.6, "Assessor on a 61-Answer Test Set");
  s.addChart(pres.charts.BAR, [{ name: "Standards met (of 9)", labels: ["Trick answers", "Keyword-only answers", "Strong answers"], values: [1.5, 4, 8.5] }], {
    x: M, y: 1.65, w: 6.4, h: 3.6, barDir: "bar", chartColors: [C.navy], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0",
    dataLabelFontSize: 14, catAxisLabelFontSize: 14, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: false, valAxisMaxVal: 9, valAxisMinVal: 0, catAxisLabelColor: C.ink, catAxisLabelFontFace: F,
    showTitle: true, title: "Average standards met, out of 9 (approximate)", titleFontSize: 13, titleColor: C.grey,
  });
  s.addText("37 real answers from test sessions and 24 constructed answers. Not yet compared with human markers, so this is not a validation yet.",
    { x: M, y: 5.45, w: 6.4, h: 0.9, fontFace: F, fontSize: 13, italic: true, color: C.grey, margin: 0 });
  const x2 = M + 6.8, w2 = W - x2 - M;
  s.addText("Problems found and fixed", { x: x2, y: 1.7, w: w2, h: 0.4, fontFace: F, fontSize: 17, bold: true, color: C.navy, margin: 0 });
  bullets(s, [
    "The welcome said there was no round limit: now written by code",
    "The same question asked again in new words: the Checker now compares questions",
    "The Planner's simulation was ignored: the rules now run it",
    "Levels rose too fast: now 2 good answers in a row, or 1 strong answer",
    "The Assessor was generous: strict rules per standard; standards met fell from 24 to 16 on 12 real answers",
  ], x2, 2.2, w2, 3.6, 14);
  card(s, x2, 5.75, w2, 0.95, C.goldLight, C.goldLight);
  s.addText("Next: keyword-only answers still score about 4 of 9, so the Assessor prompt is tightened again.",
    { x: x2 + 0.2, y: 5.75, w: w2 - 0.4, h: 0.95, fontFace: F, fontSize: 14, bold: true, color: C.gold, valign: "middle", margin: 0 });
  s.addNotes(SCRIPT[n].text || "I then ran the Assessor on 61 test answers. Strong answers met about 8 or 9 standards and trick answers about 1 or 2, which is the right direction. But answers that only repeat keywords still score about 4, so that is the next fix. These numbers are approximate and not yet compared with human markers. On the right are the five problems I found in testing and how each was fixed.");
}

// 19. Conclusion
{
  const s = base("Conclusions");
  card(s, 1.0, 1.5, W - 2.0, 2.7, C.navyLight, C.navyLight);
  s.addText("Existing Socratic AI tutors have no question ladder, no measurement and no adaptation. Socratic AI is a working multi-agent tutor that follows Paul's six levels, marks every answer against the nine standards, adapts to the learner, and never gives the answer away. Next, it will show which type of reasoning and knowledge a learner used, and be checked against human markers.",
    { x: 1.35, y: 1.6, w: W - 2.7, h: 2.5, fontFace: F, fontSize: 20, color: C.ink, align: "center", valign: "middle", margin: 0 });
  s.addText("Take-home message", { x: 1.0, y: 4.75, w: W - 2.0, h: 0.4, fontFace: F, fontSize: 15, bold: true, color: C.gold, align: "center", margin: 0 });
  s.addText("This is a reasoning trainer, not an answer machine, built in a new way: many prompted agents working together, guarded by code.",
    { x: 1.0, y: 5.2, w: W - 2.0, h: 0.9, fontFace: F, fontSize: 19, bold: true, color: C.navy, align: "center", valign: "top", margin: 0 });
  s.addNotes(SCRIPT[n].text || "To conclude. Current tutors have no question ladder and no real assessment. Socratic AI follows the six levels, marks the nine standards and never gives the answer away. Next, it will show which type of reasoning and knowledge a learner used, checked against human markers. It is a reasoning trainer, not an answer machine.");
}

// 20. References (two slides, like the senior's deck)
{
  const refs = [
    "[1] R. Paul and L. Elder, The Thinker's Guide to the Art of Socratic Questioning. Foundation for Critical Thinking, 2006; and The Miniature Guide to Critical Thinking Concepts and Tools, 8th ed. Rowman & Littlefield, 2019.",
    "[2] L. W. Anderson and D. R. Krathwohl, Eds., A Taxonomy for Learning, Teaching, and Assessing. Longman, 2001.",
    "[3] J. B. Biggs and K. F. Collis, Evaluating the Quality of Learning: The SOLO Taxonomy. Academic Press, 1982.",
    "[4] H. Sahamid, \"Developing critical thinking through Socratic questioning,\" Int. J. Educ. Literacy Stud., vol. 4, no. 3, pp. 62-72, 2016.",
    "[5] A. Makhene, \"The use of Socratic inquiry to facilitate critical thinking in nursing education,\" Health SA Gesondheid, vol. 24, a1224, 2019.",
    "[6] Y.-R. Ho, B.-Y. Chen and C.-M. Li, \"Thinking more wisely: Using the Socratic method to develop critical thinking skills amongst healthcare students,\" BMC Med. Educ., vol. 23, 173, 2023.",
    "[7] P.-B. Degen and I. Asanov, \"Beyond automation: Socratic AI, epistemic agency, and ... multi-agent learning architectures,\" arXiv:2508.05116, 2025.",
    "[8] F. Fan, \"Socratic scaffolding in AI education: A framework for critical thinking,\" Regional Educ. Technol. J., vol. 8, no. 1, 2025.",
    "[9] K. W. Lee, Y. S. Ang and J. W. Lai, \"Learning analytics with scalable Bloom's taxonomy labeling of Socratic chatbot dialogues,\" Computers, vol. 14, no. 12, 555, 2025.",
    "[10] H.-P. Lee et al., \"The impact of generative AI on critical thinking,\" in Proc. CHI '25, Art. 1121, 2025.",
    "[11] A. Sarkar, \"How to stop AI from killing your critical thinking,\" TEDAI Vienna, 2025.",
    "[12] L. Brand, \"A practical guide to agentic AI in higher education,\" QS, 11 Sep. 2026.",
    "[13] L. Yan et al., \"Practical and ethical challenges of large language models in education,\" Br. J. Educ. Technol., vol. 55, no. 1, pp. 90-112, 2023.",
    "[14] R. W. Hamming, \"Error detecting and error correcting codes,\" Bell Syst. Tech. J., vol. 29, no. 2, pp. 147-160, 1950.",
    "[15] P. Lewis et al., \"Retrieval-augmented generation for knowledge-intensive NLP tasks,\" NeurIPS, vol. 33, pp. 9459-9474, 2020.",
    "[16] T. W. Ho, Foundations of Modern Deep Neural Networks, Module 8: Towards Agentic AI [Course slides]. CAPE, Universiti Teknologi PETRONAS, 2025.",
    "[17] J. Wei et al., \"Chain-of-thought prompting elicits reasoning in large language models,\" NeurIPS, vol. 35, pp. 24824-24837, 2022.",
    "[18] S. Yao et al., \"ReAct: Synergizing reasoning and acting in language models,\" in Proc. ICLR, 2023.",
    "[19] Y. Gao et al., \"Retrieval-augmented generation for large language models: A survey,\" arXiv:2312.10997, 2023.",
    "[20] Anthropic, \"Introducing the Model Context Protocol,\" 25 Nov. 2024. [Online]. Available: https://www.anthropic.com/news/model-context-protocol",
    "[21] S. Hong et al., \"MetaGPT: Meta programming for a multi-agent collaborative framework,\" in Proc. ICLR, 2024.",
    "[22] M. H. Nguyen, T. P. Chau, P. X. Nguyen and N. D. Q. Bui, \"AgileCoder: Dynamic collaborative agents for software development based on agile methodology,\" arXiv:2406.11912, 2024.",
    "[23] T. W. Ho, Foundations of Modern Deep Neural Networks, Module 7: Foundation Models and Generative AI [Course slides]. CAPE, Universiti Teknologi PETRONAS, 2025.",
    "[24] DeepLearning.AI, short courses: Knowledge Graphs for RAG; Building and Evaluating Advanced RAG; Agentic Knowledge Graph Construction; Long-Term Agentic Memory with LangGraph; Building Agentic RAG with LlamaIndex; Retrieval Augmented Generation. [Online]. Available: https://learn.deeplearning.ai",
  ];
  [refs.slice(0, 12), refs.slice(12)].forEach((part, k) => {
    const s = base("References");
    s.addText(part.map((t, i) => ({ text: t, options: { breakLine: i < part.length - 1 } })),
      { x: M, y: 1.15, w: W - 2 * M, h: 5.85, fontFace: F, fontSize: 12, color: C.ink, valign: "top", paraSpaceAfter: 6, margin: 0 });
    s.addNotes(SCRIPT[n].text || (k === 0 ? "These are my references. The full list is in my thesis." : "These are the rest of my references."));
  });
}

// 21. Thank you
{
  const s = pres.addSlide(); n += 1;
  s.background = { color: C.white };
  stripes(s, 0.2);
  s.addImage({ path: path.join(HERE, "utp_logo_cover.jpeg"), x: (W - 2.2) / 2, y: 1.0, w: 2.2, h: 2.2 });
  s.addText("THANK YOU", { x: 0, y: 3.55, w: W, h: 0.9, fontFace: F, fontSize: 44, bold: true, color: C.navy, align: "center", margin: 0 });
  s.addText("Q & A", { x: 0, y: 4.45, w: W, h: 0.7, fontFace: F, fontSize: 28, color: C.gold, align: "center", margin: 0 });
  stripes(s, 7.2);
  s.addNotes(SCRIPT[n].text || "Thank you. I am happy to take your questions.");
}

pres.writeFile({ fileName: OUT }).then(() => console.log("wrote", OUT, n, "slides"));
