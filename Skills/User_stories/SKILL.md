---
name: req-to-stories
description: >
  Converts a requirements document (BRD, RTM JSON, or plain requirements list) into a full
  MoSCoW-ranked agile backlog: Feature List, Epics with EPIC-IDs, User Stories with STORY-IDs,
  Acceptance Criteria, and a Story Map — all embedded directly into a single enriched RTM JSON
  written to a new file. Use this skill whenever the user asks to generate user stories, epics, or
  a backlog from requirements; phrases like "turn requirements into stories", "generate epics",
  "create a backlog", "write user stories for this BRD", "story map", or "break requirements into
  stories" should all trigger this skill. Also trigger when the user uploads or pastes a BRD, RTM,
  or requirements list and asks what to do next — this skill is the natural next step after a BRD
  or RTM exists. Reads inputs from the Cowork working directory; outputs a single enriched JSON.
---

# Req-to-Stories Skill

Transforms a requirements document — BRD markdown, RTM JSON, or a plain requirements list — into
a single enriched RTM JSON that contains everything: the original requirements plus epics,
features, user stories, acceptance criteria, and a story map index — all in one file.

---

## Step 0 — Locate Inputs

### Where to look (in order)

1. **Files already in context** — if the user pasted or uploaded a BRD or RTM, use that directly.
2. **Cowork working directory** — typically `~/Desktop` or `~/Documents`. List the directory:

```bash
ls ~/Desktop 2>/dev/null || ls ~/Documents 2>/dev/null || ls ~
```

Look for files matching: `*BRD*`, `*RTM*`, `*requirements*`, `*req*` (`.md`, `.json`, `.txt`).

3. **Ask** if nothing is found:
   > "I couldn't find a requirements file in your working folder. Where should I look, or would
   > you like to paste the requirements here?"

### Accepted input formats

| Format | What to extract |
|---|---|
| RTM JSON (like `stemwidgets-RTM-seed.json`) | `requirements[]` array — each item has `id`, `title`, `category`, `priority`, `status`, `acceptance_criteria`, `notes` |
| BRD Markdown | Parse `REQ-*` sections — extract ID, title, priority, description, acceptance criteria |
| Plain list | Infer IDs, categories, and priorities from context; flag assumptions |

Read the file:

```bash
cat ~/Desktop/<filename>
```

---

## Step 1 — Parse & Classify Requirements

For each requirement, extract and record:

| Field | Source |
|---|---|
| `req_id` | e.g. `REQ-F-001` |
| `title` | Requirement title |
| `category` | Functional / Non-Functional / Constraint / Data / Integration |
| `moscow` | Map from priority field: "Must Have" → M, "Should Have" → S, "Could Have" → C, "Won't Have" → W |
| `status` | CONFIRMED / ASSUMED |
| `acceptance_criteria` | Verbatim from source |

**MoSCoW mapping rules:**
- `Must Have` → **M** (no negotiation; in-scope v1)
- `Should Have` → **S** (strong intent; defer only if time-constrained)
- `Could Have` → **C** (nice to have; first cut if scope tightens)
- `Won't Have` → **W** (explicitly out of v1)
- If priority is absent, infer from category: Constraints default to M, Non-Functional to S unless
  the source text says otherwise.

---

## Step 2 — Build the Feature List

Group related requirements into named **Features** — logical product capabilities that sit above
individual requirements but below Epics.

**Naming convention:** `FEAT-NNN` (three-digit, zero-padded), descriptive title.

Example groupings from a typical STEM product:

```
FEAT-001  Authentication & Account Management   (REQ-F-001, REQ-F-002, REQ-F-004)
FEAT-002  Freemium & Subscription               (REQ-F-003, REQ-F-016, REQ-F-017)
FEAT-003  Interactive Widgets                   (REQ-F-005, REQ-F-006, REQ-F-007, REQ-F-008)
FEAT-004  Python Code Snippets                  (REQ-F-009, REQ-F-010, REQ-F-011)
FEAT-005  AI Concept Advisor                    (REQ-F-012 – REQ-F-015)
FEAT-006  Analytics Dashboard                   (REQ-F-018, REQ-F-019)
FEAT-007  Performance & Reliability             (REQ-NF-001 – REQ-NF-009)
FEAT-008  Compliance & Data Governance          (REQ-C-002, REQ-C-003, REQ-D-003, REQ-D-004)
FEAT-009  Integrations                          (REQ-I-001 – REQ-I-003)
```

For each Feature produce:
- `FEAT-ID`, `Feature Name`, `MoSCoW` (inherit highest-priority child requirement's MoSCoW),
  `Req-IDs covered`, `Status` (CONFIRMED if all children confirmed; ASSUMED if any child is assumed)

---

## Step 3 — Define Epics

Group Features into **Epics** — major delivery themes spanning one or more sprints.

**Naming convention:** `EPIC-NNN` (three-digit, zero-padded).

Recommended epic structure:

| EPIC-ID | Epic Name | Features | MoSCoW |
|---|---|---|---|
| EPIC-001 | User Identity & Access | FEAT-001, FEAT-002 | M |
| EPIC-002 | Core Learning Experience | FEAT-003, FEAT-004 | M |
| EPIC-003 | AI Advisor | FEAT-005 | M |
| EPIC-004 | Platform Operations | FEAT-006, FEAT-007 | M |
| EPIC-005 | Compliance & Integrations | FEAT-008, FEAT-009 | M |

Adjust epics to fit the actual requirements found — don't force a rigid structure if the input
doesn't match.

---

## Step 4 — Write User Stories

For every **Functional requirement** (REQ-F-*) and Integration requirement (REQ-I-*), write at
least one User Story. For Non-Functional, Constraint, Data, and Compliance requirements, write
**Enabling Stories** (technical stories owned by engineering).

### Story naming convention

```
STORY-[FEAT-ID]-[NNN]
e.g. STORY-001-001, STORY-001-002
```

### Story template

```
As a [user type],
I want to [action],
So that [outcome / value].

Acceptance Criteria:
  - Given [context], when [action], then [expected result].
  - (repeat for each distinct scenario)

MoSCoW: M / S / C / W
Req-IDs: REQ-F-XXX, ...
EPIC: EPIC-NNN
Status: CONFIRMED | ASSUMED
```

### User type vocabulary

Derive from the requirements source. Common types: `Free Learner`, `Paid Learner`,
`Institution Admin`, `Platform Admin`, `System` (for non-functional / enabling stories).

### Writing rules

1. One story per distinct user action or system behaviour. Split if a requirement covers multiple
   actors or flows.
2. Each story is independently testable — no story depends on another for its ACs to pass.
3. ASSUMED requirements → add a `⚠️ Assumption: [A-NNN]` note after the ACs.
4. For a requirement with multiple acceptance criteria bullet points, each bullet becomes a
   separate Given/When/Then AC line.
5. Enabling stories for REQ-NF, REQ-C, REQ-D: format as
   `As the System, I must [behaviour] so that [compliance / quality goal].`

---

## Step 5 — Assemble the Enriched RTM JSON

Everything — epics, features, stories, and the story map index — goes into **one JSON file**.
Never produce separate markdown files. Never overwrite the source.

### Output file naming

```
[original-filename]-stories.json
```

Example: `stemwidgets-RTM-seed.json` → `stemwidgets-RTM-seed-stories.json`

---

### Top-level JSON structure

```json
{
  "project": "...",
  "version": "...",
  "generated": "YYYY-MM-DD",
  "source_rtm": "[original-filename].json",

  "epics": [ ... ],
  "features": [ ... ],
  "requirements": [ ... ],
  "stories": [ ... ],
  "story_map": { ... },

  "summary": { ... }
}
```

---

### `epics` array

```json
"epics": [
  {
    "epic_id": "EPIC-001",
    "title": "User Identity & Access",
    "moscow": "M",
    "feature_ids": ["FEAT-001", "FEAT-002"]
  }
]
```

---

### `features` array

```json
"features": [
  {
    "feat_id": "FEAT-001",
    "title": "Authentication & Account Management",
    "epic_id": "EPIC-001",
    "moscow": "M",
    "status": "CONFIRMED",
    "req_ids": ["REQ-F-001", "REQ-F-002", "REQ-F-004"]
  }
]
```

`status` is `"CONFIRMED"` if all linked requirements are confirmed; `"ASSUMED"` if any are assumed.

---

### `requirements` array — enriched originals

Keep every original field unchanged. Add three new fields:

```json
{
  "id": "REQ-F-001",
  "title": "User Registration",
  "category": "Functional",
  "priority": "Must Have",
  "status": "CONFIRMED",
  "source": "Blueprint §2, §7",
  "acceptance_criteria": "...",
  "test_cases": [],
  "design_refs": [],
  "notes": "...",

  "moscow": "M",
  "feat_id": "FEAT-001",
  "story_ids": ["STORY-001-001", "STORY-001-002"]
}
```

---

### `stories` array

Each story is a self-contained object:

```json
"stories": [
  {
    "story_id": "STORY-001-001",
    "feat_id": "FEAT-001",
    "epic_id": "EPIC-001",
    "req_ids": ["REQ-F-001"],
    "moscow": "M",
    "status": "CONFIRMED",
    "assumption_flag": false,
    "assumption_refs": [],

    "narrative": {
      "as_a": "New user",
      "i_want": "to register with my email and password",
      "so_that": "I can access a learning session within 2 minutes"
    },

    "acceptance_criteria": [
      {
        "given": "a user lands on the registration page",
        "when": "they submit a valid email and password",
        "then": "an account is created and they are redirected to their first session within 2 minutes"
      },
      {
        "given": "a user submits an email already in use",
        "when": "they attempt to register",
        "then": "a clear error message is shown and no duplicate account is created"
      }
    ]
  }
]
```

Rules:
- `assumption_flag: true` and `assumption_refs: ["A-001"]` for any story derived from an ASSUMED
  requirement.
- Enabling stories (REQ-NF, REQ-C, REQ-D): set `"as_a": "System"`.
- One story per distinct actor/flow. Split requirements that cover multiple actors.
- Each AC item is a separate object — not concatenated strings.

---

### `story_map` object

A navigable index — epics → features → story IDs. No prose, just the cross-reference structure:

```json
"story_map": {
  "EPIC-001": {
    "title": "User Identity & Access",
    "features": {
      "FEAT-001": {
        "title": "Authentication & Account Management",
        "stories": ["STORY-001-001", "STORY-001-002", "STORY-001-003", "STORY-001-004"]
      },
      "FEAT-002": {
        "title": "Freemium & Subscription",
        "stories": ["STORY-002-001", "STORY-002-002", "STORY-002-003"]
      }
    }
  },
  "EPIC-002": { ... }
}
```

---

### `summary` block — updated counts

```json
"summary": {
  "total": 40,
  "by_category": { ... },
  "by_status": { ... },
  "assumptions_count": 12,
  "open_items_count": 6,
  "epics_count": 5,
  "features_count": 9,
  "stories_count": 42,
  "assumed_stories_count": 14,
  "test_cases_linked": 0,
  "design_refs_linked": 0
}
```

---

### Writing the file

Use Python to write the JSON (handles escaping and large payloads reliably):

```python
import json, pathlib

src = pathlib.Path("~/Desktop/stemwidgets-RTM-seed.json").expanduser()
out = src.with_name(src.stem + "-stories.json")

data = { ... }  # fully assembled dict

out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
print(f"Written: {out}")
```

After writing, confirm to the user:

> "Done — `[filename]-stories.json` written to [directory].
> Contains [N] epics · [N] features · [N] stories across [N] requirements."

Then call `present_files` (if available) so the file is immediately downloadable.

---

## Output Quality Checklist

Before writing, verify internally:

- [ ] Every `REQ-F-*` and `REQ-I-*` has at least one story in `stories[]`
- [ ] Every `REQ-NF-*`, `REQ-C-*`, `REQ-D-*` has at least one enabling story (`as_a: "System"`)
- [ ] Every story has at least one structured `given/when/then` AC object
- [ ] Every ASSUMED requirement → `assumption_flag: true` on its stories
- [ ] Every requirement object has `moscow`, `feat_id`, and `story_ids` populated
- [ ] Every story ID appears in `story_map` under the correct epic + feature
- [ ] `summary.stories_count` equals `stories[].length`
- [ ] Output filename ≠ source filename — source is never overwritten

---

## Error Handling

| Situation | Action |
|---|---|
| Input file not found | Ask user for path or offer to accept pasted content |
| Requirement has no acceptance criteria | Derive AC from title + description; flag with `⚠️ AC derived` |
| Priority field missing or ambiguous | Default to `Should Have` (S); flag with a note |
| Category unclear | Infer from ID prefix (REQ-F → Functional, REQ-NF → Non-Functional, etc.) |
| RTM has fewer than 5 requirements | Proceed; note that epics may be thin |
| RTM has more than 100 requirements | Warn user this will produce a large backlog; ask if they want a summary mode (epics + features only, no individual stories) |

---

## Reference: ID Prefixes Summary

| ID type | Format | Example |
|---|---|---|
| Requirement | `REQ-[CAT]-[NNN]` | `REQ-F-001` |
| Feature | `FEAT-[NNN]` | `FEAT-003` |
| Epic | `EPIC-[NNN]` | `EPIC-002` |
| Story | `STORY-[FEAT-NNN]-[NNN]` | `STORY-003-002` |