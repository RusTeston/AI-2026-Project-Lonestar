# Course Specification Builder — Technical Specification (`spec.md`)

**Document status:** Ready for implementation
**Version:** 1.0
**Date:** August 9, 2026
**Based on:** `course-spec-builder-requirements.md` v0.1 (Aug 9, 2026)
**Audience:** An AI build agent (Claude Cowork) implementing this project end-to-end.

---

## 0. How to use this document (read first)

This is a complete, buildable specification for a **client-side-only web application**. It resolves the open questions from the requirements baseline (Section 16 of the source doc) with concrete, reasonable defaults so a build agent doesn't have to stop and ask before starting. Every place a default was chosen instead of confirmed by the project owner is flagged with **[ASSUMPTION]** — build to these defaults, but call them out in your summary so the owner can adjust.

Build order is suggested in Section 15. If anything in here is genuinely ambiguous or contradictory, ask before proceeding rather than guessing — but for everything covered below, you have enough to build without stopping.

---

## 1. Project Summary

A single-page web application that walks a course requestor through a 12-section discovery questionnaire (~150 questions total) and produces two downloadable files:

1. A plain-language **PDF** of the requestor's questions and answers.
2. An optional, template-generated **Markdown course-development specification** (`[course-name]-spec.md`) for whoever builds the course.

No backend, no database, no accounts, no email, no AI API calls. Everything runs in the requestor's browser. Progress is saved to `localStorage` on that browser/device only.

---

## 2. Tech Stack

**[ASSUMPTION]** — chosen to satisfy "no AI API," "simple," "no build complexity," and easy static hosting:

- **Framework:** Vanilla HTML/CSS/JavaScript (ES modules), no UI framework required. This keeps the deliverable a static site deployable anywhere (Netlify, Vercel, GitHub Pages, S3, internal web server) with zero server-side code.
- **Build tooling:** [Vite](https://vitejs.dev/) for local dev server + production bundling. Not required, but recommended for module bundling, minification, and a `dist/` output.
- **PDF generation:** [jsPDF](https://github.com/parallax/jsPDF) (client-side, no server call). Alternative: browser print-to-PDF is NOT sufficient — the requirement is a one-click **download**, not "open print dialog."
- **Markdown generation:** No library needed — plain JavaScript template strings, assembled into a `.md` file and downloaded via a `Blob` + `<a download>`.
- **Storage:** `localStorage` (per requirements — no `sessionStorage`, no cookies, no backend).
- **Styling:** Plain CSS (or a lightweight utility approach). No component library dependency required.
- **No React, no Node backend, no database.**

---

## 3. Project File Structure

```
course-spec-builder/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.js                  # App entry point / router between screens
│   ├── styles/
│   │   └── main.css
│   ├── data/
│   │   ├── questionBank.js      # Full question data — see Section 6
│   │   └── config.js            # ACCESS_CODE, storage keys, version number
│   ├── state/
│   │   └── store.js             # In-memory app state + localStorage sync
│   ├── screens/
│   │   ├── accessGate.js        # Access-code entry screen
│   │   ├── requestorInfo.js     # Requestor identification screen
│   │   ├── questionnaire.js     # Section-by-section question flow
│   │   ├── review.js            # Final review screen
│   │   └── complete.js          # Post-download confirmation screen
│   ├── components/
│   │   ├── sectionMenu.js       # Section nav w/ completion status
│   │   ├── questionField.js     # Renders one question by type
│   │   ├── progressBar.js
│   │   └── validationBanner.js
│   └── utils/
│       ├── validation.js        # Required-question / section-complete logic
│       ├── filenameSanitizer.js
│       ├── pdfGenerator.js
│       └── markdownGenerator.js
└── README.md
```

---

## 4. Data Model (localStorage schema)

Store everything under a single namespaced key so it's easy to version, inspect, and clear.

```js
// localStorage key: "csb:v1:session"
{
  "schemaVersion": 1,
  "createdAt": "2026-08-09T14:00:00.000Z",
  "updatedAt": "2026-08-09T14:22:10.000Z",
  "accessGranted": true,
  "requestor": {
    "firstName": "",
    "lastName": "",
    "courseTitle": "",
    "department": "",
    "role": "",
    "email": ""
  },
  "answers": {
    // keyed by question id, e.g. "s1q1"
    "s1q1": { "value": "text answer here", "notApplicable": false },
    "s2q4": { "value": "", "notApplicable": true }
  },
  "currentSectionId": "s3",
  "completedSections": ["s1", "s2"]
}
```

Rules:
- Auto-save on every field change (debounced ~500ms is fine) — write the whole session object back to `localStorage`.
- `schemaVersion` lets you detect and gracefully handle a future question-bank change (**[ASSUMPTION]** for open item #10 in the source doc: if `schemaVersion` on load doesn't match the current app's expected version, show a one-time notice — "Your saved progress was from an earlier version of this form and may not match exactly. You can continue or start over." — and let the requestor choose. Don't silently discard data.)
- "Clear saved progress" removes the `csb:v1:session` key entirely, after a confirmation dialog ("This will permanently delete your saved answers on this device. This cannot be undone.").

---

## 5. Question Bank

This is the canonical source of truth for all questionnaire content. Build `src/data/questionBank.js` to export exactly this structure (shown here as JSON for portability — convert to a JS module with `export const questionBank = [...]`).

**Field types used below:**
- `textarea` — multi-line free text (default for most questions)
- `text` — single-line free text (short factual answers: names, numbers, dates)
- `radio` — single choice from a small fixed set
- `select` — single choice from a longer fixed set

**`notApplicableAllowed`**: when `true`, render a "Not applicable" option alongside the field; selecting it disables the text input and satisfies the required-field check without free text.

Required flags below implement the "at minimum" list from the requirements doc (Section 7, items 1–15). All other questions default to optional. The project owner should review and adjust required/optional flags per source-doc open item #4 — this is a defensible starting point, not a final ruling.

```json
[
  {
    "id": "s1",
    "title": "Business Need and Purpose",
    "questions": [
      { "id": "s1q1", "text": "What business problem is this course intended to solve?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s1q2", "text": "What triggered the request for training?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s1q3", "text": "Why is training the appropriate solution?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s1q4", "text": "What is happening today that should change?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s1q5", "text": "What should learners do differently after completing the course?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s1q6", "text": "What business result should improve?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s1q7", "text": "What happens if the course is not created?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s1q8", "text": "Is this training required, recommended or optional?", "type": "radio", "options": ["Required", "Recommended", "Optional"], "required": false, "notApplicableAllowed": false },
      { "id": "s1q9", "text": "Is the course connected to a larger initiative, product launch, policy, certification or organizational change?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s1q10", "text": "How will the sponsor determine whether the course was worth creating?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s1q11", "text": "If this course is successful, what will learners be doing differently 30 days after completing it?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s2",
    "title": "Target Audience",
    "questions": [
      { "id": "s2q1", "text": "Who exactly will take the course?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s2q2", "text": "What are their roles or job titles?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q3", "text": "Approximately how many learners are expected?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s2q4", "text": "Are there multiple learner groups or personas?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q5", "text": "Where are the learners located?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q6", "text": "What languages do they use?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q7", "text": "What level of experience do they have?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q8", "text": "What do they already know about the topic?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s2q9", "text": "What common knowledge gaps do they have?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q10", "text": "What misconceptions or mistakes are common?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q11", "text": "What tools, systems or processes do they currently use?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q12", "text": "What motivates them to learn this?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q13", "text": "What might make them resist or ignore the training?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q14", "text": "How much time can they realistically devote to it?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q15", "text": "Are there accessibility, language, cultural, technical or scheduling considerations?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s2q16", "text": "Will managers need to support or reinforce the learning?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s3",
    "title": "Performance Expectations",
    "questions": [
      { "id": "s3q1", "text": "What specific tasks must learners perform?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q2", "text": "What decisions must they be able to make?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q3", "text": "What problems must they be able to solve?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q4", "text": "What conversations must they be able to conduct?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q5", "text": "What tools or systems must they be able to use?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q6", "text": "What does successful performance look like?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q7", "text": "What does poor performance look like?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q8", "text": "What are the most common errors?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q9", "text": "Which mistakes carry the greatest business, customer, financial, security or compliance risk?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q10", "text": "How frequently will learners perform these tasks?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q11", "text": "Under what conditions will they perform them?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q12", "text": "Will they perform independently or with assistance?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q13", "text": "What reference materials will they have while working?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q14", "text": "How is performance currently measured?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s3q15", "text": "Can an experienced employee demonstrate the desired performance?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s4",
    "title": "Learning Objectives",
    "helperText": "Tip: use observable objective verbs such as explain, identify, select, configure, demonstrate, diagnose, compare, troubleshoot, create and complete. Avoid vague standalone terms such as understand, learn and be familiar with.",
    "questions": [
      { "id": "s4q1", "text": "What should learners be able to do by the end of the course?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s4q2", "text": "Which outcomes involve knowledge?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s4q3", "text": "Which outcomes involve practical skills?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s4q4", "text": "Which outcomes involve judgment or decision-making?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s4q5", "text": "Which outcomes involve changes in behavior or attitude?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s4q6", "text": "Which objectives are essential?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s4q7", "text": "Which objectives are useful but optional?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s4q8", "text": "What level of proficiency is required: awareness, basic application, independent performance or mastery?", "type": "radio", "options": ["Awareness", "Basic application", "Independent performance", "Mastery"], "required": false, "notApplicableAllowed": false },
      { "id": "s4q9", "text": "Must learners remember the information, or can they use reference materials?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s4q10", "text": "How will each objective be demonstrated or measured?", "type": "textarea", "required": true, "notApplicableAllowed": false }
    ]
  },
  {
    "id": "s5",
    "title": "Scope and Boundaries",
    "questions": [
      { "id": "s5q1", "text": "What topics must be included?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s5q2", "text": "What topics should be excluded?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q3", "text": "What are the three to five most important things learners need to retain?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q4", "text": "What content is required by policy, regulation, certification or leadership?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q5", "text": "What content is helpful but not essential?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q6", "text": "What prerequisites should learners complete first?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q7", "text": "Should advanced topics be placed in a separate course?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q8", "text": "Are there sensitive or confidential topics?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q9", "text": "Does the course need to distinguish among different roles, products, processes or scenarios?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q10", "text": "Are there topics that must be reviewed by Legal, Compliance, Security, HR or another department?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q11", "text": "Is this one course, a course series or part of a larger learning path?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s5q12", "text": "What is explicitly out of scope?", "type": "textarea", "required": true, "notApplicableAllowed": false }
    ]
  },
  {
    "id": "s6",
    "title": "Source Materials and Subject-Matter Expertise",
    "questions": [
      { "id": "s6q1", "text": "Who is the primary subject-matter expert?", "type": "text", "required": true, "notApplicableAllowed": false },
      { "id": "s6q2", "text": "Who has final authority when sources disagree?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q3", "text": "What source materials already exist?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q4", "text": "Which sources are considered authoritative?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s6q5", "text": "Are there current policies, procedures, job aids, videos, presentations, recordings or examples?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q6", "text": "Are the materials accurate and up to date?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q7", "text": "When were they last reviewed?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s6q8", "text": "Are there known gaps in the existing materials?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q9", "text": "Can existing materials be reused or modified?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q10", "text": "Are there copyright, licensing, confidentiality or brand restrictions?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q11", "text": "Can real customer or employee examples be used?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q12", "text": "Must examples be anonymized?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q13", "text": "Are screenshots or product demonstrations required?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q14", "text": "Is access available to the system, tool or environment being taught?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q15", "text": "Can the subject-matter expert provide examples of both successful and unsuccessful performance?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s6q16", "text": "Who will resolve questions discovered during development?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s7",
    "title": "Course Format and Delivery",
    "questions": [
      { "id": "s7q1", "text": "How will the course be delivered?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s7q2", "text": "Will it be self-paced, instructor-led, virtual, in person, blended or cohort-based?", "type": "select", "options": ["Self-paced", "Instructor-led", "Virtual", "In person", "Blended", "Cohort-based"], "required": false, "notApplicableAllowed": false },
      { "id": "s7q3", "text": "Where will the course be hosted?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q4", "text": "Is an LMS required?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q5", "text": "What technical standard is required, such as SCORM, xAPI, video, HTML or PDF?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q6", "text": "What is the preferred course length?", "type": "text", "required": true, "notApplicableAllowed": false },
      { "id": "s7q7", "text": "Should the course be completed in one sitting?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q8", "text": "Should it be divided into short modules?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q9", "text": "Will learners use desktop computers, tablets or mobile devices?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q10", "text": "Will audio be available or appropriate?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q11", "text": "Are captions, transcripts, keyboard navigation, screen-reader support or other accessibility features required?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q12", "text": "Are there bandwidth or device limitations?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q13", "text": "Will learners need a lab, sandbox, simulation or practice environment?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q14", "text": "Should learners be able to download job aids or reference materials?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q15", "text": "Is there a required visual style, template or branding standard?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s7q16", "text": "Should the course feel formal, conversational, technical, scenario-based or something else?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s8",
    "title": "Instructional Approach",
    "questions": [
      { "id": "s8q1", "text": "Should the course begin with concepts, a demonstration, a problem or a realistic scenario?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q2", "text": "What real-world situations should learners practice?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q3", "text": "Are there common customer, employee or workplace scenarios that should be included?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q4", "text": "Should learners make decisions and see the consequences?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q5", "text": "Should the course include guided practice?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s8q6", "text": "Should learners practice independently?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q7", "text": "Would simulations, case studies, role-plays, demonstrations or hands-on labs be appropriate?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q8", "text": "Should learners receive feedback after each activity?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q9", "text": "What tone should the course use?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q10", "text": "Should examples be role-specific?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q11", "text": "Are stories, characters or recurring scenarios appropriate?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q12", "text": "What supporting job aids should be created?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q13", "text": "What information belongs in the course versus a searchable reference guide?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s8q14", "text": "How should the learning be reinforced after completion?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s9",
    "title": "Assessment and Completion",
    "helperText": "Assessment evidence should match the objective: a knowledge check for explaining a concept, a scenario for choosing an action, a simulation for using a system, a rubric-scored project for creating a deliverable.",
    "questions": [
      { "id": "s9q1", "text": "How will learners prove they achieved the objectives?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q2", "text": "Is a formal assessment required?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q3", "text": "Should the course use knowledge checks, scenarios, demonstrations, projects, observations or a final exam?", "type": "textarea", "required": true, "notApplicableAllowed": false },
      { "id": "s9q4", "text": "What score is required to pass?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s9q5", "text": "How many attempts are permitted?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s9q6", "text": "Should learners receive feedback after incorrect answers?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q7", "text": "Must assessment questions be randomized?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q8", "text": "Is there a required question bank?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q9", "text": "Should learners demonstrate a skill rather than answer questions about it?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q10", "text": "Are there critical behaviors that must be assessed?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q11", "text": "Can learners test out of the course?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q12", "text": "What constitutes completion?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q13", "text": "Is a certificate required?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q14", "text": "Does completion expire?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q15", "text": "Will refresher training or recertification be required?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s9q16", "text": "Who will review and approve the assessment?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s10",
    "title": "Measurement and Business Impact",
    "helperText": "Possible measures: assessment performance, task accuracy, time to proficiency, reduction in errors, support/escalation volume, customer satisfaction, manager observation, productivity, compliance, technical win rate, time to complete a process.",
    "questions": [
      { "id": "s10q1", "text": "What does success look like immediately after training?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q2", "text": "What should change 30, 60 or 90 days afterward?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q3", "text": "What performance data is currently available?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q4", "text": "Is there a baseline against which results can be compared?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q5", "text": "Which metrics should improve?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q6", "text": "How will learner confidence be measured?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q7", "text": "How will managers observe behavior change?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q8", "text": "Will learners be surveyed?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q9", "text": "Will managers or customers provide feedback?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q10", "text": "Who will collect and analyze the results?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q11", "text": "When will the course be evaluated?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s10q12", "text": "What result would indicate that the course needs revision?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s11",
    "title": "Stakeholders and Approvals",
    "questions": [
      { "id": "s11q1", "text": "Who requested the course?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s11q2", "text": "Who owns the final business outcome?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s11q3", "text": "Who is the primary subject-matter expert?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s11q4", "text": "Who represents the learners?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s11q5", "text": "Who will review instructional accuracy?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s11q6", "text": "Who will review branding and visual design?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s11q7", "text": "Is Legal, Compliance, Security, HR or Accessibility review required?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s11q8", "text": "Who has final approval?", "type": "text", "required": true, "notApplicableAllowed": false },
      { "id": "s11q9", "text": "Who can make scope decisions?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s11q10", "text": "How many review cycles are expected?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s11q11", "text": "How will feedback be collected and consolidated?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s11q12", "text": "What happens when reviewers disagree?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s11q13", "text": "What are the review deadlines?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s11q14", "text": "Who signs off on the final course?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  },
  {
    "id": "s12",
    "title": "Schedule, Resources and Constraints",
    "questions": [
      { "id": "s12q1", "text": "When must the course launch?", "type": "text", "required": true, "notApplicableAllowed": false },
      { "id": "s12q2", "text": "What is driving that deadline?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q3", "text": "Are there intermediate milestones?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q4", "text": "Is the deadline fixed or negotiable?", "type": "radio", "options": ["Fixed", "Negotiable"], "required": false, "notApplicableAllowed": false },
      { "id": "s12q5", "text": "What budget is available?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q6", "text": "Who will help develop the course?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q7", "text": "What development tools are available?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q8", "text": "Are voice-over, video, animation or professional production resources available?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q9", "text": "How much subject-matter-expert time is available?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q10", "text": "Are there technical, legal, branding or procurement limitations?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q11", "text": "What dependencies could delay development?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q12", "text": "Is a pilot required?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q13", "text": "How many learners should participate in the pilot?", "type": "text", "required": false, "notApplicableAllowed": true },
      { "id": "s12q14", "text": "How much time is available for revisions?", "type": "textarea", "required": false, "notApplicableAllowed": true },
      { "id": "s12q15", "text": "What is the minimum viable version of the course if time becomes limited?", "type": "textarea", "required": false, "notApplicableAllowed": true }
    ]
  }
]
```

**Requestor information fields** (collected before Section 1, not part of the question bank above — all required):

| Field | Type | Notes |
|---|---|---|
| First name | text | required |
| Last name | text | required |
| Working course title | text | required |
| Department / business unit | text | required |
| Role / job title | text | required |
| Email address | email (validated format) | required |

---

## 6. Screens and User Flow

### 6.1 Access Gate
- First screen shown on load, before anything else — including before checking for saved progress.
- Single input for the access code. **[ASSUMPTION]** default code: `8675309` (from requirements; store in `src/data/config.js` as `ACCESS_CODE` so it's a one-line change).
- On correct entry, set `accessGranted: true` in the session object and proceed. On incorrect entry, show an inline error — do not lock out after N attempts (no such requirement given).
- **Known limitation to state in the README** (per source doc Section 4.1): this is a lightweight client-side gate, not real security — the code is visible in page source/network traffic to a technically inclined visitor. Server-side validation is out of scope for v1.

### 6.2 Requestor Information
- Shown once, after the access gate, before Section 1 of the questionnaire.
- Collects the six fields in Section 5 above. All required; block "Continue" until valid (email format check included).
- If saved progress exists, pre-fill from it and allow editing.

### 6.3 Questionnaire (Sections 1–12)
- One section visible at a time.
- **Section menu** (sidebar or top nav, collapsible on mobile): lists all 12 sections by title, each showing a status indicator:
  - Not started
  - In progress
  - Complete (all required questions in that section answered)
  - Contains missing required question(s) — visually distinct from "not started" (e.g., warning icon), shown once the requestor has attempted to leave/finish
- Clicking any section in the menu jumps directly there (open navigation, not locked to linear order — source doc explicitly requires direct access to all 12 sections).
- **Next** / **Back** buttons move linearly through sections 1→12.
- Each question renders per its `type` (see Section 5 above) with its label always visible (never rely on placeholder-as-label — accessibility requirement).
- Where `notApplicableAllowed` is true, show a "Not applicable" checkbox/toggle next to the field; checking it disables and clears the text field.
- Autosave on change (see Section 4).

### 6.4 Review Screen
- Shown after Section 12, or reachable any time from a persistent "Review" link.
- Displays requestor information, then all 12 sections with every question and its current answer (or "Not applicable" / blank).
- Any unanswered required questions are called out clearly at the top with direct links to jump to that question.
- Each section (or each answer) is editable inline or via a "Revise" link back to that section — requestor should not have to re-navigate from scratch to fix one answer.
- Two download buttons only become active once all required questions are answered (see Section 8, Validation).

### 6.5 Complete / Download Screen
- After a successful download, confirm what happened ("Your PDF has been downloaded" / "Your specification file has been downloaded") without clearing saved progress — the requestor may want to download the other file too, or come back later.
- Offer "Clear saved progress" here with a confirmation dialog (see Section 4).

---

## 7. Filenames and Sanitization

`src/utils/filenameSanitizer.js` — implement a function used by both download buttons:

```js
function sanitizeFilenameSegment(str) {
  return str
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')   // non-alphanumeric -> hyphen
    .replace(/-+/g, '-')            // collapse repeats
    .replace(/^-|-$/g, '')          // trim leading/trailing hyphen
    .slice(0, 60);                  // reasonable max length
}
```

- **PDF filename:** `{first-name}-{last-name}-course-request.pdf` — e.g. `jane-smith-course-request.pdf`.
- **Markdown filename:** `{working-course-title}-spec.md` — e.g. `working-course-title-spec.md`.
- If sanitization produces an empty string (edge case — non-Latin characters, etc.), fall back to `course-request.pdf` / `course-spec.md` respectively rather than producing a broken filename.

---

## 8. Validation Rules

- A required question is satisfied if it has a non-empty trimmed value, OR (where `notApplicableAllowed` is true) "Not applicable" is selected.
- A section is "complete" when every required question within it is satisfied.
- The questionnaire as a whole is "complete" when every required question across all 12 sections, plus all six requestor-info fields, is satisfied.
- Both download buttons on the Review screen are disabled (with an explanatory tooltip/message, not just silently disabled) until the questionnaire is complete.
- Validation messages must name the specific question and section, and link/scroll directly to it — never a generic "please complete required fields."
- Do this validation entirely client-side, live, as the requestor types/selects — don't wait for a submit action to surface problems.

---

## 9. Output 1 — PDF ("Download My Questions and Answers")

Audience: the requestor, non-technical. **Never use the words "Markdown" or `spec.md`** anywhere in this button's label, description, or the PDF itself.

Content, in order:
1. Title: the working course title.
2. Requestor name, department, role, email, and completion date.
3. Each of the 12 sections as a heading, followed by every question in that section and its answer.
   - If "Not applicable" was selected, print **Not applicable**.
   - If an optional question was left blank: **[ASSUMPTION]** print **Not provided** rather than omitting it — this keeps the record complete and avoids the appearance of a missing/broken field. (Source doc left this as an open decision — flag to the project owner that "omit instead" is a one-line change if preferred.)
4. Format for both on-screen reading and printing: reasonable margins, a readable serif or sans-serif body font (e.g. 11–12pt), section headings visually distinct (bold/larger), page numbers, and the course title/requestor name in a running header or footer on pages after the first.

Implementation notes for jsPDF:
- Build content programmatically (loop over sections/questions), not as one giant string — this makes pagination and text-wrapping easier to control (`doc.splitTextToSize()` for wrapping, watch page-height and call `doc.addPage()` as needed).
- Trigger download via `doc.save(filename)`.

---

## 10. Output 2 — Markdown Course Specification ("Download Course Specification")

Audience: whoever develops the course (may be technical or a course owner). This button's description may explain, in plain language, that this file is primarily for the person who will build the course — no need to avoid the word "Markdown" here, but keep the explanation simple (e.g., "This is a structured planning document for whoever develops your course.").

**Rules:**
- Deterministic template only — no AI synthesis, no paraphrasing of the requestor's words, no inference. This satisfies "never fabricate, infer or silently rewrite factual information supplied by the requestor."
- Missing optional information is labeled `_Not provided._` in the output — never invented or filled in with a plausible-sounding guess.
- The requestor's own words are reproduced as given; the template only supplies structure (headings, ordering, labels) around them.

**Template structure** (`src/utils/markdownGenerator.js` should assemble exactly this shape):

```markdown
# Course Specification: {Working Course Title}

**Requested by:** {First Name} {Last Name} ({Role}, {Department})
**Contact:** {Email}
**Date generated:** {Completion Date}

## 1. Business Need
{s1q1 answer}

**Desired change in learner behavior:** {s1q5 answer}

## 2. Target Audience
{s2q1 answer}

**Existing knowledge:** {s2q8 answer}

## 3. Learning Objectives
{s4q1 answer}

**How objectives will be measured:** {s4q10 answer}

## 4. Scope
**In scope:** {s5q1 answer}
**Out of scope:** {s5q12 answer}

## 5. Source Materials & Subject-Matter Expertise
**Primary SME:** {s6q1 answer}
**Authoritative sources:** {s6q4 answer}

## 6. Delivery Format
{s7q1 answer}
**Expected length:** {s7q6 answer}

## 7. Instructional Approach
**Guided practice:** {s8q5 answer}

## 8. Assessment
{s9q3 answer}

## 9. Approvals
**Final approval:** {s11q8 answer}

## 10. Timeline
**Launch date/deadline:** {s12q1 answer}

---

## Appendix: Full Questionnaire Responses

_This appendix preserves every question and answer exactly as submitted, organized by section, for reference._

### {Section 1 title}
**{Question text}**
{Answer, or "_Not applicable._" or "_Not provided._"}

... (repeat for every question in every section)
```

- Sections 1–10 of the generated spec pull from the *required* questions primarily (the ones most load-bearing for course development); this is a reasonable v1 default. **[ASSUMPTION]** — the exact mapping from questionnaire answers to specification sections is explicitly left open in the source doc (item #6); the project owner may want to enrich these sections with more of the optional answers (e.g., pull in `s2q2`, `s3q1`, `s8q7`, etc.) once they see the v1 output. Build the mapping as a single, clearly-commented config object (question-id → spec-section) so it's easy to extend later without touching the rendering logic.
- The Appendix must include **all** questions from all 12 sections, regardless of what was pulled into the summary sections above — nothing is answered once and hidden.
- Trigger download via a `Blob` of type `text/markdown` and a temporary `<a download="{filename}">` click.

---

## 11. Accessibility Requirements

- Every form field has a visible, programmatically-associated `<label>` — never placeholder-only.
- Full keyboard operability: tab order follows visual/logical order; all interactive elements (including the section menu, Next/Back, Not-applicable toggles, and download buttons) are reachable and operable via keyboard.
- Focus is managed sensibly on section change (e.g., focus moves to the new section's heading) so keyboard/screen-reader users aren't stranded.
- Validation and status messages are conveyed accessibly (e.g., `aria-live` region for validation banners, not color alone) — color is never the only signal for required/complete/error states; pair with icons or text.
- Sufficient color contrast (aim for WCAG 2.1 AA contrast ratios as a baseline). **[ASSUMPTION]** — the source doc left the exact conformance target open (item #9); build to WCAG 2.1 AA as a sensible default and flag that a stricter target (AAA) or a formal VPAT is a bigger scope decision for the owner.
- Responsive layout: usable at common desktop, tablet, and mobile widths (test at roughly 375px, 768px, and 1280px+).

---

## 12. Explicit Out of Scope for v1 (do not build)

- Sending email of any kind (including the "Email me a copy" flow described conceptually in the source doc — that's a future phase, not this build).
- Any server, API, or database — no submission storage beyond the requestor's own browser.
- User accounts, login, or SSO.
- Cross-device or cross-browser continuation of progress.
- Any call to an AI/LLM API for generating either output file.
- LMS integration.
- Automatically building the course itself.
- AI-policy or course-maintenance/ownership discovery questions (intentionally excluded from the question bank above).

---

## 13. Assumptions Made in This Spec (flag these to the project owner)

1. **Tech stack**: vanilla JS + Vite, jsPDF for PDF generation. No framework mandated by the requirements — this was chosen for simplicity and zero-backend deployability.
2. **Required/optional flags**: the specific 21 questions marked `required: true` above are a defensible reading of the "at minimum" list in the source doc, but the owner should review the full required/optional matrix (source doc open item #4).
3. **"Not provided" vs. omit** for unanswered optional questions in the PDF: this spec defaults to showing "Not provided" rather than omitting (source doc open item #5).
4. **Spec-section mapping**: the Markdown template's summary sections (1–10) pull from a specific subset of answers; this is a starting point, not a final content design (source doc open item #6).
5. **Access-code security**: client-side-only gate, explicitly documented as a known limitation rather than resolved (source doc open item #2 remains genuinely open — flag it, don't silently "fix" it by adding a backend that wasn't asked for).
6. **Accessibility target**: WCAG 2.1 AA as a working default (source doc open item #9).
7. **Schema-version mismatch behavior**: notify-and-let-the-requestor-choose, rather than silently discarding saved progress (source doc open item #10).
8. **Hosting/deployment**: not decided here — this spec produces a static site buildable output (`dist/`) deployable to any static host; the owner still needs to pick one (source doc open item #1).

None of these are load-bearing for getting a working v1 built — they're all easy to revisit after the owner sees the app running.

---

## 14. Acceptance Criteria

Build is done when all of the following are true:

1. A visitor must enter the correct access code before seeing the requestor-info screen or any questionnaire content.
2. All six requestor-information fields are collected and required before the questionnaire begins.
3. All 12 sections and every question listed in Section 5 of this spec are present and correctly typed.
4. Next, Back, and direct section-menu navigation all work and stay in sync with each other.
5. Progress persists across a page reload in the same browser (verify by refreshing mid-questionnaire).
6. The section menu visibly distinguishes not-started, in-progress, complete, and missing-required-answers states.
7. Both download buttons are disabled until every required question (across all sections + requestor info) is answered, with a clear explanation of what's missing.
8. The Review screen shows every question and answer and allows editing any of them without losing other progress.
9. "Download My Questions and Answers" produces a correctly named, readable, printable PDF containing all sections/questions/answers, with no mention of "Markdown" or `spec.md`.
10. "Download Course Specification" produces a correctly named `.md` file with the structured summary sections plus a complete appendix of all questions and answers, using only the requestor's actual words (no invented content).
11. "Clear saved progress" requires confirmation and, once confirmed, fully resets the app to the access-gate screen.
12. The app is usable via keyboard alone and passes a basic accessibility check (labels, contrast, focus order).
13. The app is usable at mobile, tablet, and desktop widths.
14. No network calls are made to any email or AI service anywhere in the app.

---

## 15. Suggested Build Order

1. Scaffold project (Vite + vanilla JS), set up `questionBank.js` and `config.js` from Sections 5–6 above.
2. Build the state/store module and localStorage persistence (Section 4) before any UI — get save/restore working against a trivial test screen first.
3. Build Access Gate → Requestor Info → Questionnaire shell (section menu + Next/Back, no validation yet) so the full navigation skeleton works end to end.
4. Add per-question-type rendering and the Not Applicable toggle.
5. Add validation logic (Section 8) and wire it into the section menu's status indicators.
6. Build the Review screen, including inline edit/jump-to-section links.
7. Implement PDF generation (Section 9), then Markdown generation (Section 10); wire both download buttons, gated by validation.
8. Pass over accessibility (Section 11): labels, focus order, `aria-live` regions, contrast check.
9. Responsive pass across breakpoints.
10. Walk the full Acceptance Criteria list (Section 14) as a manual QA checklist before calling it done.

---

## 16. Deferred — Not Part of This Build

Documented here only so a future spec revision has context; **do not implement any of this now**:

- "Email me a copy" flow for the requestor (readable email, no attachment).
- Silent delivery of the generated `.md` specification as an email attachment to an internal address.
- Server-side email sending, provider selection, sender authentication, retry/failure handling.

---

**Note to the build agent:** if you hit a genuine ambiguity not covered above (not one of the flagged assumptions — those are decided), stop and ask rather than guessing. Everything else in this document is intended to be sufficient to build v1 without further clarification.
