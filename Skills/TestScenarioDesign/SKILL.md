---
name: test-scenario-design
description: >
  Core TDD skill — writes one test scenario per acceptance criterion BEFORE any code is
  written. Reads the RTM JSON and Milestone Plan MD from the Cowork folder, assigns a
  permanent TC-ID (typed U/I/E/C/P/S) to every acceptance criterion across all stories,
  produces a TC-Registry document with full Given/When/Then scenarios, a coverage matrix
  mapping every REQ-ID and MS-ID to its TCs, and an enriched RTM JSON with tc_ids
  populated on every story and requirement. Trigger this skill whenever the user asks for
  test scenarios, TDD, test cases, TC-IDs, test registry, acceptance test design, test
  coverage matrix, BDD scenarios, Given/When/Then, or wants to assign test IDs to
  requirements or stories. Always trigger when an RTM JSON is present and the user
  mentions testing, QA, or TDD.
---

# Test Scenario Design (TDD) Skill

Reads the RTM JSON (and optionally the Milestone Plan) from the Cowork folder and produces:
1. A **TC-Registry** — one test scenario per acceptance criterion, typed and permanently IDed
2. A **Coverage Matrix** — every REQ-ID and MS-ID mapped to its TC-IDs
3. An **enriched RTM JSON** — `tc_ids` populated on every story and requirement
4. A single `.md` output file delivered to `/mnt/user-data/outputs/`

**TDD contract:** TC-IDs are assigned and scenarios are written BEFORE implementation.
A TC-ID without a linked implementation is the correct starting state.

---

## 0. Prerequisites

No additional libraries required. Output is Markdown + JSON written with standard Python.

---

## 1. Inputs

### 1.1  Primary source — Cowork folder

Always start by listing the Cowork folder:

```bash
ls -lh /mnt/user-data/uploads/
```

Look for these files (read all that are present):

| File | Role | How to read |
|------|------|-------------|
| `*.json` (RTM) | **Required.** Stories with acceptance_criteria; requirements with req_ids | `cat /mnt/user-data/uploads/<file>.json` |
| `*milestone*.md` | Optional. Maps requirements to MS-IDs for coverage matrix | `cat /mnt/user-data/uploads/<file>.md` |
| `*tier-map*.md` | Optional. Maps requirements to TIER-IDs for test targeting | `cat /mnt/user-data/uploads/<file>.md` |

The RTM JSON is the only mandatory input. Fall back to conversation-pasted JSON only if the
Cowork folder is empty.

### 1.2  What to extract from the RTM JSON

```
PROJECT_NAME      — project.project
VERSION           — project.version
ALL_STORIES       — stories[].{story_id, feat_id, epic_id, req_ids, narrative, acceptance_criteria[]}
ALL_REQUIREMENTS  — requirements[].{id, title, category, moscow, status, feat_id, story_ids}
EPICS             — epics[].{epic_id, title}
FEATURES          — features[].{feat_id, title, epic_id}
```

Each `acceptance_criterion` has: `given`, `when`, `then`.
Each story has one or more ACs. **One TC-ID per AC — no exceptions.**

### 1.3  What to extract from the Milestone Plan (if present)

```
MILESTONE_IDS     — requirements[].milestone_id (MS-01 through MS-04)
```

Use `milestone_id` to populate the coverage matrix MS-ID column and group test scenarios
by milestone in the registry.

---

## 2. TC-ID System

### 2.1  Permanent ID format

```
TC-[TYPE]-[NNNN]   where TYPE is one letter and NNNN is zero-padded integer from 0001
```

IDs are **permanent** — once assigned they never change. New TCs append to the sequence
within their type. Gaps are allowed for retired TCs.

### 2.2  Type taxonomy

Assign the type that best describes **how this test is executed**, not what it tests:

| Type | Name | Definition | Tooling |
|------|------|-----------|---------|
| **U** | Unit | Tests a single function, class, or module in isolation; no I/O, no network | Jest, Vitest, pytest |
| **I** | Integration | Tests two or more modules or services interacting; may touch DB, API, or queue | Supertest, pytest + testcontainers |
| **E** | End-to-End | Tests a full user journey through the browser UI; driven by a real browser | Playwright, Cypress |
| **C** | Contract | Validates a data shape, schema, or API contract without executing business logic | Zod, Pydantic, JSON Schema, OpenAPI |
| **P** | Performance | Measures latency, throughput, Lighthouse score, or load under concurrency | k6, Lighthouse CI, Artillery |
| **S** | Security/Manual/Legal | Human-executed audit, red-team, legal review, or release checklist gate | Manual QA, Legal sign-off, axe-core |

**Type assignment rules:**
- If the AC says "within Nms" or "p95" or "Lighthouse" → **P**
- If the AC says "Legal sign-off" or "QA audit" or "red-team review" or "content review" → **S**
- If the AC validates a schema has or lacks certain fields → **C**
- If the AC tests a complete user journey (register, buy, open widget) → **E**
- If the AC tests a server-side integration (Stripe webhook, LLM API, SSO) → **I**
- If the AC tests a pure function or business rule with no external dependencies → **U**
- When in doubt between E and I: if a browser is involved → **E**; if server-to-server → **I**

### 2.3  Numbering rule

Number sequentially **within each type**, across the entire project. Do not reset per story
or per milestone. Assign in story order (STORY-001-001 first, STORY-009-003 last).

---

## 3. Output: TC-Registry Document

### 3.1  Document header

```markdown
# [PROJECT_NAME] — Test Scenario Registry

| Field | Value |
|---|---|
| Version | [VERSION] |
| Date | [TODAY] |
| TDD Status | Pre-implementation — TC-IDs assigned before code |
| Total TCs | [N] |
| Source RTM | [filename] |
| Source Milestone Plan | [filename or "not provided"] |

> **TC-IDs are permanent.** One TC per acceptance criterion.
> Assigned before implementation. Implementation links added during sprint.

## TC-ID Type Key

| Type | Name | Tooling |
|------|------|---------|
| U | Unit | Jest / Vitest / pytest |
| I | Integration | Supertest / pytest + testcontainers |
| E | End-to-End | Playwright / Cypress |
| C | Contract | Zod / Pydantic / JSON Schema |
| P | Performance | k6 / Lighthouse CI / Artillery |
| S | Security / Manual / Legal | Manual QA / Legal / axe-core |

## TC Count Summary

| Type | Count |
|------|-------|
| E — End-to-End | N |
| I — Integration | N |
| S — Security/Manual/Legal | N |
| P — Performance | N |
| C — Contract | N |
| U — Unit | N |
| **Total** | **N** |
```

### 3.2  TC-Registry table

One row per TC (one per AC), grouped by Milestone:

```markdown
## TC Registry — MS-01: MVP Internal Proof

| TC-ID | Type | Story | REQ-IDs | Scenario Title | Given | When | Then | MS-ID | Status |
|-------|------|-------|---------|---------------|-------|------|------|-------|--------|
| TC-E-0001 | E | STORY-001-001 | REQ-F-001 | Registration — valid email flow | a visitor is on the registration page | they enter a valid email and password and submit the form | an account is created and they are redirected within 2 minutes | MS-01 | Pre-impl |
...
```

Keep `Given`/`When`/`Then` text verbatim from the RTM acceptance criteria.
`Scenario Title` = a short descriptive label (5–8 words).
`Status` = `Pre-impl` for all TCs in this document (implementation links added later).

Group rows by milestone (MS-01 table, then MS-02 table, etc.). Within each milestone,
order by story ID.

### 3.3  Scenario detail blocks (for non-trivial TCs)

For every TC with type **P**, **S**, or **C**, write a detail block after the table section:

```markdown
---

### TC-P-0001 — Widget Interaction Response Time

**Story:** STORY-003-001 | **REQ:** REQ-NF-002 | **MS:** MS-01
**Type:** Performance
**Tooling:** k6 or equivalent load testing tool

**Scenario:**
- **Given:** the widget is open and loaded in a browser
- **When:** the learner manipulates any interactive element 50 times consecutively
- **Then:** p95 interaction response time is ≤ 100ms across all measurements

**Execution notes:**
- Measure time from user input event to DOM update (not network round-trip — widget is client-side)
- Run against staging environment with at least 3 widget types
- Fail threshold: any single p95 measurement > 100ms

**Pre-implementation contract:**
The widget module must expose a performance measurement hook.
No implementation may ship without this test passing.
```

Write these blocks for all P, S, and C type TCs. E and I types are self-descriptive
from the table; only add detail blocks for them if the scenario is complex.

---

## 4. Output: Coverage Matrix

After the registry, produce two cross-reference tables.

### 4.1  Requirement → TC coverage

```markdown
## Coverage Matrix — Requirement → Test Cases

| REQ-ID | Title | MS-ID | Category | TC-IDs |
|--------|-------|-------|---------|--------|
| REQ-F-001 | User Registration | MS-01 | Functional | TC-E-0001, TC-E-0002, TC-E-0003 |
...
```

Every REQ-ID must appear. TC-IDs listed are those from stories linked to that requirement.
If a requirement has no stories (rare), list `— (no stories linked)`.

### 4.2  Milestone → TC coverage

```markdown
## Coverage Matrix — Milestone → Test Cases

| MS-ID | Name | Req Count | TC Count | TC-IDs |
|-------|------|-----------|----------|--------|
| MS-01 | MVP Internal Proof | 11 | N | TC-E-0001, TC-E-0002, ... |
...
```

---

## 5. Output: Enriched RTM JSON

After the coverage matrix, produce an enriched RTM JSON block with `tc_ids` added to
every **story** and every **requirement**.

```json
{
  "project": "...",
  "version": "...",
  "tc_registry_version": "1.0",
  "tc_registry_date": "YYYY-MM-DD",
  "tc_type_key": {
    "U": "Unit", "I": "Integration", "E": "End-to-End",
    "C": "Contract", "P": "Performance", "S": "Security/Manual/Legal"
  },
  "tc_summary": { "E": N, "I": N, "P": N, "C": N, "S": N, "U": N, "total": N },
  "stories": [
    {
      "story_id": "STORY-001-001",
      "tc_ids": ["TC-E-0001", "TC-E-0002", "TC-E-0003"],
      ...all original story fields preserved...
    }
  ],
  "requirements": [
    {
      "id": "REQ-F-001",
      "tc_ids": ["TC-E-0001", "TC-E-0002", "TC-E-0003", "TC-E-0004", "TC-E-0005"],
      ...all original requirement fields preserved...
    }
  ]
}
```

Rules:
- Story `tc_ids` = TCs assigned to that story's ACs (one per AC, in AC order)
- Requirement `tc_ids` = union of all `tc_ids` from all stories that reference that requirement
- Preserve all original fields on both stories and requirements
- Output full arrays — do not truncate

---

## 6. Output File

Deliver **one file** to `/mnt/user-data/outputs/`:

```
[project-slug]-tc-registry-v[version].md
```

Structure:

```
# [Project] — Test Scenario Registry      ← header, type key, count summary
---
## TC Registry — MS-01                    ← registry table per milestone
## TC Registry — MS-02
## TC Registry — MS-03
## TC Registry — MS-04
---
### TC-P-0001 — [title]                   ← detail blocks for P, S, C types
### TC-S-0001 — [title]
...
---
## Coverage Matrix — Requirement → TCs    ← REQ-ID coverage table
## Coverage Matrix — Milestone → TCs      ← MS-ID coverage table
---
## Enriched RTM (tc_ids populated)        ← heading
```json
{ enriched JSON }
```
```

Then call `present_files` with the single path.

---

## 7. Markdown Formatting Guide

- `#` document title
- `##` for registry sections, coverage matrices
- `###` for individual TC detail blocks
- GFM pipe tables for registry and coverage tables
- Fenced JSON block for enriched RTM
- `---` separators between major sections
- No HTML tags

---

## 8. Quality Checklist

Before calling `present_files`, verify:

- [ ] Every acceptance criterion from every story has exactly one TC-ID
- [ ] TC-IDs are sequential within each type (E-0001, E-0002...; no gaps in assignments)
- [ ] Every TC-ID in the registry table is also in the enriched JSON story `tc_ids`
- [ ] Every REQ-ID appears in the coverage matrix
- [ ] Every MS-ID appears in the milestone coverage table
- [ ] All P, S, and C type TCs have detail blocks with execution notes
- [ ] Story `tc_ids` in JSON match the count of ACs for that story
- [ ] Requirement `tc_ids` = union of all linked story `tc_ids` (no duplicates)
- [ ] `tc_summary` counts in JSON match the registry table counts
- [ ] `Status` = `Pre-impl` on all TCs (not `Pass`, `Fail`, or any implementation state)
- [ ] Output is a single `.md` file