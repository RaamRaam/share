---
name: milestone-plan
description: >
  Defines a locked milestone plan (MS-01 MVP through MS-04+) from an RTM JSON read from
  the Cowork folder. Assigns a permanent MS-ID to every requirement, writes entry and exit
  criteria plus test gate requirements for each milestone, and produces a single Markdown
  output file containing the milestone plan followed by an enriched RTM JSON with
  milestone_id populated on every requirement. Trigger this skill whenever the user asks
  for a milestone plan, release plan, MS-IDs, MVP definition, v1 scope, launch criteria,
  sprint milestones, test gates, entry/exit criteria, or wants to lock down which
  requirements belong to which release. Always trigger when an RTM JSON is present in the
  Cowork folder and the user mentions milestones, releases, or planning.
---

# Milestone Plan Skill

Reads the RTM JSON (and optionally the Tier Map MD) from the Cowork folder and produces:
1. A **Milestone Plan** — MS-01 through MS-04+ with full entry/exit criteria and test gates
2. An **enriched RTM JSON** — every requirement annotated with `milestone_id`
3. A single `.md` output file delivered to `/mnt/user-data/outputs/`

---

## 0. Prerequisites

No additional libraries required. All output is Markdown + JSON written with standard Python.

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
| `*.json` (RTM) | **Required.** Requirements, moscow, status, category, feat_id | `cat /mnt/user-data/uploads/<file>.json` |
| `*tier-map*.md` | Optional. Tier assignments enrich test gate targeting | `cat /mnt/user-data/uploads/<file>.md` |
| `*HLD*.md` | Optional. ADR decisions inform milestone ordering | `cat /mnt/user-data/uploads/<file>.md` |

The RTM JSON is the only mandatory input. If absent, ask the user to add it to the Cowork folder.
Fall back to conversation-pasted JSON only if the folder is empty.

### 1.2  Fields to extract from the RTM JSON

```
PROJECT_NAME   — project.project
VERSION        — project.version
ALL_REQS       — requirements[].{id, title, category, moscow, status, feat_id, notes}
ASSUMED_REQS   — requirements where status == "ASSUMED"
CONFIRMED_REQS — requirements where status == "CONFIRMED"
MUST_HAVE      — requirements where moscow == "M"
SHOULD_HAVE    — requirements where moscow == "S"
COULD_HAVE     — requirements where moscow == "C"
OPEN_ITEMS     — notes fields containing OI-* references
ASSUMPTIONS    — notes fields containing A-* references
```

---

## 2. MS-ID System

### 2.1  Permanent ID format

```
MS-NN   where NN is a zero-padded integer starting at 01
```

IDs are **permanent** — once assigned they never change. New milestones append to the sequence.
A retired milestone leaves its ID retired, not reused.

### 2.2  Standard milestone taxonomy

| MS-ID | Name | Purpose | Audience |
|-------|------|---------|---------|
| MS-01 | MVP — Internal Proof | Smallest runnable slice proving the core learning loop | Engineering team, internal stakeholders |
| MS-02 | v1 Public Launch | All CONFIRMED Must-Have requirements delivered and verified | General public, paying customers, institutions |
| MS-03 | v1.1 — Assumption Resolution | All ASSUMED Must-Have requirements resolved and delivered | Paying customers; closes all legal/compliance gates |
| MS-04 | v2 — Should-Have & Deferred | Should-Have requirements + deferred items from open items log | All users; scale and growth features |

Add MS-05+ for project-specific additional milestones. Document with `[PROJECT-SPECIFIC]` tag.

### 2.3  Assignment rules

Apply in strict order — a requirement is assigned to the **earliest** milestone it can enter:

1. **MS-01** — CONFIRMED, Must-Have, and belongs to the irreducible core learning loop:
   - The feature a user must complete to experience the primary value proposition
   - Minimum auth (email/password), one working widget, no-evaluation enforcement,
     snippet display, basic data persistence
   - No payments, no AI, no institution SSO, no analytics dashboard required

2. **MS-02** — CONFIRMED, Must-Have, but not in MS-01:
   - Everything confirmed that is needed for a public launch
   - Includes: subscription/billing (confirmed), AI advisor (confirmed), SSO (confirmed),
     analytics dashboard (confirmed), platform reliability (confirmed NFRs),
     account lifecycle, AI fallback

3. **MS-03** — ASSUMED, Must-Have (any category):
   - All requirements still carrying ASSUMED status
   - These depend on external decisions (Legal sign-off, provider selection, pricing model)
   - Must not block MS-02 launch; delivered in the sprint cycle immediately after launch

4. **MS-04** — Should-Have or Could-Have (any status):
   - Scalability stretch targets, deferred features, v2 roadmap items

**Override rule:** If an ASSUMED requirement is a hard legal gate (GDPR, COPPA), it is still
MS-03 but flagged `⚠ Legal gate — must resolve before MS-02 can receive Legal sign-off`.
MS-02 exit criteria explicitly require Legal sign-off as a checkpoint even if the full
implementation is MS-03.

---

## 3. Output: Milestone Plan Document

### 3.1  Document header

```markdown
# [PROJECT_NAME] — Milestone Plan

| Field | Value |
|---|---|
| Version | [VERSION] |
| Date | [TODAY] |
| Status | Locked — MS-IDs are permanent |
| Source RTM | [RTM filename] |

> MS-IDs assigned in this document are permanent release identifiers.
> New milestones append to the sequence. Existing IDs are never reassigned.

## Milestone Registry

| MS-ID | Name | Scope | Req Count | Status |
|-------|------|-------|-----------|--------|
| MS-01 | MVP — Internal Proof | Core learning loop, confirmed reqs only | N | Planned |
| MS-02 | v1 Public Launch | All confirmed Must-Have | N | Planned |
| MS-03 | v1.1 Assumption Resolution | All assumed Must-Have | N | Planned |
| MS-04 | v2 — Should-Have & Deferred | Should-Have + open items | N | Roadmap |
```

### 3.2  Milestone detail blocks

Write one block per milestone using this exact structure:

```markdown
---

## MS-NN — [Name]

**Purpose:** [one sentence]
**Audience:** [who verifies/accepts this milestone]
**Estimated sprint position:** [Sprint N–M or relative to MS-NN]

### Entry Criteria

> All of the following must be true before MS-NN work begins.

- [ ] [criterion]
- [ ] [criterion]

### Requirements in Scope

| REQ-ID | Title | Category | MoSCoW | Status | TIER-ID (primary) |
|--------|-------|---------|--------|--------|------------------|
| REQ-F-001 | ... | Functional | M | CONFIRMED | TIER-006 |
...

### Exit Criteria

> All of the following must be true before MS-NN is declared complete.

- [ ] [criterion — measurable, binary pass/fail]
- [ ] [criterion]

### Test Gate Requirements

> Tests that must pass (not just exist) before exit is granted.

| Gate ID | Gate Name | Test Type | Pass Condition | Tier Under Test |
|---------|-----------|-----------|---------------|----------------|
| TG-NN-01 | [name] | [Unit / Integration / E2E / Load / Manual / Legal] | [specific pass condition] | TIER-NNN |
...
```

Include `TIER-ID (primary)` column only if a tier map is available. If no tier map, omit.
Include `TG-NN-NN` gate IDs — these are also permanent identifiers that will be referenced
by the test plan in a later sprint.

### 3.3  Post-milestone notes

After all four blocks, add:

```markdown
---

## Cross-Milestone Dependencies

| Dependency | From | To | Risk if Late |
|-----------|------|----|-------------|
| Legal sign-off on GDPR/COPPA | MS-03 resolution | MS-02 exit gate | Cannot launch without Legal approval |
| LLM provider selected (OI-004) | MS-03 resolution | MS-02 AI feature delivery | AI Concept Advisor blocked |
| Stripe confirmed (A-004) | MS-03 resolution | MS-02 subscription delivery | Payment flow blocked |
...

## Open Items Blocking MS-02

List every OI-* reference from the RTM notes that, if unresolved, would delay MS-02 launch.

| OI Ref | Description | Impact | Required By |
|--------|-------------|--------|------------|
...

## Assumption Resolutions Required Before MS-03 Close

List every A-* assumption that must be confirmed and implemented to close MS-03.

| Assumption | Area | Resolution Required | Target |
|-----------|------|---------------------|--------|
...
```

---

## 4. Output: Enriched RTM JSON

After the milestone plan, produce an **enriched RTM JSON block** — the original RTM
`requirements` array with `milestone_id` added to every requirement object.

Format:

```json
{
  "project": "...",
  "version": "...",
  "milestone_plan_version": "1.0",
  "milestone_plan_date": "YYYY-MM-DD",
  "milestone_registry": {
    "MS-01": "MVP — Internal Proof",
    "MS-02": "v1 Public Launch",
    "MS-03": "v1.1 Assumption Resolution",
    "MS-04": "v2 — Should-Have & Deferred"
  },
  "requirements": [
    {
      "id": "REQ-F-001",
      "title": "User Registration",
      "milestone_id": "MS-01",
      ...all original fields preserved...
    }
  ]
}
```

Rules:
- Every requirement gets exactly one `milestone_id` string.
- All original requirement fields are preserved unchanged.
- Output the full `requirements` array — do not truncate.
- Add `milestone_registry` and `milestone_plan_version` at top level.

---

## 5. Output File

Deliver **one file** to `/mnt/user-data/outputs/`:

```
[project-slug]-milestone-plan-v[version].md
```

Structure:

```
# [Project] — Milestone Plan           ← document header + registry table
---
## MS-01 — MVP Internal Proof          ← milestone detail block
---
## MS-02 — v1 Public Launch
---
## MS-03 — v1.1 Assumption Resolution
---
## MS-04 — v2 Should-Have & Deferred
---
## Cross-Milestone Dependencies        ← dependency + OI + assumption tables
---
## Enriched RTM (milestone_id populated)
```json
{ enriched RTM JSON }
```
```

Then call `present_files` with the single path.

---

## 6. Markdown Formatting Guide

- `#` for the document title
- `##` for milestone blocks and cross-milestone sections
- `###` for Entry Criteria, Requirements in Scope, Exit Criteria, Test Gate Requirements
- GFM pipe tables for all tabular data
- Fenced code block for the enriched RTM JSON
- `---` as separator between milestone blocks and the JSON section
- Checklist items `- [ ]` for all entry and exit criteria
- No HTML tags

---

## 7. Quality Checklist

Before calling `present_files`, verify:

- [ ] Every REQ-* from the RTM appears in exactly one milestone's requirements table
- [ ] Every milestone block has Entry Criteria, Requirements in Scope, Exit Criteria, and Test Gates
- [ ] MS-01 contains only CONFIRMED requirements
- [ ] MS-02 contains only CONFIRMED requirements not already in MS-01
- [ ] MS-03 contains all ASSUMED Must-Have requirements (and no CONFIRMED ones)
- [ ] MS-04 contains all Should-Have and Could-Have requirements
- [ ] Every exit criterion is binary pass/fail (no "good enough" language)
- [ ] Every test gate has a Gate ID (TG-NN-NN), test type, and specific pass condition
- [ ] Legal gate requirements (GDPR, COPPA) appear in both MS-02 exit criteria and MS-03 scope
- [ ] All OI-* references from RTM notes appear in the Open Items Blocking MS-02 table
- [ ] All A-* references from RTM notes appear in the Assumption Resolutions table
- [ ] Enriched RTM JSON contains `milestone_id` on every requirement object
- [ ] `milestone_registry` key present at the top level of the enriched JSON
- [ ] Output is a single `.md` file