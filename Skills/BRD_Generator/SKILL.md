---
name: brd-generator
description: >
  Converts a product blueprint (.md) or rough product description into a full Business
  Requirements Document (BRD) with assigned REQ-IDs, and seeds a Requirements Traceability
  Matrix (RTM) as JSON. Triggers on: "generate a BRD", "turn this into requirements",
  "write a requirements document", "create a BRD from this blueprint", "assign REQ IDs",
  "seed an RTM", "write up requirements", or whenever the user has a product blueprint or
  description and wants formal requirements. Also triggers when the user uploads or pastes
  a blueprint .md and asks for any kind of requirements output. Handles both single-shot
  generation AND interactive refinement — the user can add, modify, remove, or promote
  requirements across multiple turns and the files are kept in sync automatically.
---

# BRD Generator

Converts a product blueprint (`.md`) or rough product description into a complete, gap-filled
Business Requirements Document with numbered REQ-IDs and a seeded RTM registry.

---

## What this skill produces

| Output | Format | Description |
|---|---|---|
| **BRD** | `.md` | Full Business Requirements Document — structured, gap-filled, REQ-IDs assigned |
| **RTM seed** | `.json` | Requirements Traceability Matrix registry — one entry per requirement |

Both files are presented via `present_files` for download. Both are updated live on every
subsequent interaction.

---

## REQ-ID Scheme

Use this scheme consistently across all outputs:

| Prefix | Meaning | Examples |
|---|---|---|
| `REQ-F-NNN` | Functional requirement | REQ-F-001, REQ-F-002 |
| `REQ-NF-NNN` | Non-functional requirement | REQ-NF-001, REQ-NF-002 |
| `REQ-C-NNN` | Constraint (tech, legal, business) | REQ-C-001, REQ-C-002 |
| `REQ-D-NNN` | Data requirement | REQ-D-001, REQ-D-002 |
| `REQ-I-NNN` | Integration requirement | REQ-I-001, REQ-I-002 |

NNN is zero-padded three digits, incrementing per prefix family. Numbers never reuse even
if a requirement is deleted (mark deleted ones as `status: "DELETED"`).

---

## Phase 1 — Parse & Gap Analysis

### Step 1: Extract from blueprint

Read the input (blueprint `.md` or pasted description) and extract:

- **Problem statement** (§1)
- **Users & stakeholders** (§2)
- **Value proposition** (§3)
- **Features in scope** (§4)
- **Features out of scope** (§4)
- **User goals / Jobs-to-be-done** (§5)
- **Business model** (§6)
- **Tech constraints** (§7)
- **Competitors / market** (§8)
- **Success metrics** (§9)
- **Risks & assumptions** (§10)
- **Open questions** (if present)

If the input doesn't have these sections, infer as much as possible and flag gaps explicitly.

### Step 2: Gap analysis

Before writing requirements, identify gaps — things a BRD needs that the blueprint doesn't
state. Common gaps:

- Auth & access control model (who can log in, how, SSO?)
- Data retention & privacy (GDPR, COPPA if students under 13?)
- Performance SLAs (page load, AI response time targets)
- Supported browsers / devices
- Error handling and fallback behaviour (e.g. if AI API is down)
- Pricing/billing specifics
- Audit & logging requirements
- Accessibility standards (WCAG level?)
- Internationalisation / language support
- Onboarding flow details

**Interaction rule:** If the blueprint has significant gaps that would materially affect
requirements (especially security, privacy, or compliance), ask the user to fill them
**before** generating. Present gaps as a concise numbered list, not a wall of questions.
Ask all gap questions in **one message** — never ask one at a time in a loop.

For minor gaps (e.g. exact pricing numbers, specific widget count), fill with a documented
assumption in the BRD and flag it with `[ASSUMED]` inline.

---

## Phase 2 — Generate BRD

Read `references/brd-template.md` for the full section structure before writing.

### Writing rules

1. **Every requirement gets a REQ-ID.** No exceptions.
2. **Each requirement is atomic.** One thing per REQ-ID. If you feel compelled to write
   "and", split into two requirements.
3. **Use SHALL for mandatory, SHOULD for recommended, MAY for optional.** This is standard
   requirements language — use it consistently.
4. **Fill every gap** — use `[ASSUMED]` where you've made a reasonable assumption, and add
   the assumption to the Assumptions Register (§A).
5. **Traceability** — every REQ-F requirement traces to at least one feature from the
   blueprint's in-scope list. Note the source feature in parentheses.
6. **Constraints from tech stack** — if the blueprint names a specific tech (e.g. SQLite,
   Vue 3, AWS S3), generate REQ-C entries for those decisions.
7. **Non-functionals are not afterthoughts** — derive NFRs from success metrics (e.g. if
   the blueprint targets "session > 8 minutes", that implies performance and reliability NFRs).

### Minimum requirement counts (scale to product complexity)

| Category | Minimum for a typical SaaS product |
|---|---|
| REQ-F | 15 |
| REQ-NF | 8 |
| REQ-C | 4 |
| REQ-D | 3 |
| REQ-I | 2 |

### BRD file naming

`[project-slug]-BRD.md` — derive slug from product name (lowercase, hyphens).

---

## Phase 3 — Seed RTM JSON

After writing the BRD, generate the RTM seed file.

Read `references/rtm-schema.md` for the exact JSON structure.

**File naming:** `[project-slug]-RTM-seed.json`

Each requirement produces one RTM entry. Required fields: `id`, `title`, `category`,
`priority`, `status`, `source`, `acceptance_criteria`, `test_cases` (empty array at seed
time), `design_refs` (empty array), `notes`.

---

## Phase 4 — Output & Delivery

1. Write BRD to `/mnt/user-data/outputs/[project-slug]-BRD.md`
2. Write RTM seed to `/mnt/user-data/outputs/[project-slug]-RTM-seed.json`
3. Call `present_files` with **both files** in one call.
4. Print a summary table:

```
✅ BRD generated   — [N] REQ-F, [N] REQ-NF, [N] REQ-C, [N] REQ-D, [N] REQ-I  ([TOTAL] total)
✅ RTM seed ready  — [TOTAL] entries, 0 test cases linked (ready for QA to populate)
⚠️  Assumptions    — [N] assumptions made (see §A in BRD)
⚠️  Open items     — [N] gaps flagged for owner decision
```

5. End with: *"Add, change, or remove requirements in the next message and both files will
   update automatically."*

---

## Phase 5 — Interactive Refinement (Live Updates)

After initial generation, the session stays open for iterative changes. Handle these
interaction patterns:

### Adding a requirement

User says: *"Add a requirement for X"*

→ Assign the next REQ-ID in the appropriate family. Add to BRD in the correct section.
Add RTM entry. Re-present both files. Confirm: *"Added REQ-F-0NN — [title]."*

### Modifying a requirement

User says: *"Change REQ-F-005 to also cover Y"* or *"REQ-F-005 should be SHOULD not SHALL"*

→ Update in place in BRD. Update RTM entry. Bump `updated_at` timestamp in RTM.
Re-present both files. Confirm: *"Updated REQ-F-005."*

### Removing a requirement

User says: *"Remove REQ-NF-003"*

→ Do NOT delete the ID. Set `status: "DELETED"` in RTM. Strike through or annotate in BRD
with `~~REQ-NF-003~~ [DELETED]`. Confirm reason if the user gave one; if not, note as
*"Removed per owner request."*

### Promoting an assumption

User says: *"Confirm that WCAG 2.1 AA is required"*

→ Remove `[ASSUMED]` tag. Promote to confirmed requirement. Update RTM status from
`ASSUMED` to `CONFIRMED`. Confirm: *"REQ-NF-007 confirmed as WCAG 2.1 AA — [ASSUMED] tag removed."*

### Bulk changes

User pastes a list of changes or says *"Here are my edits:"*

→ Process all changes in one pass. Re-present both files once. Print a change log:
```
REQ-F-012  ADDED    — Two-factor authentication
REQ-NF-003 DELETED  — Offline support removed from scope
REQ-C-001  MODIFIED — SQLite → PostgreSQL constraint updated
```

### Re-numbering policy

**Never re-number existing IDs.** If REQ-F-007 is deleted, the next new functional
requirement is REQ-F-016 (or whatever the next unused number is). Gaps in numbering are
intentional and fine.

---

## Save location

All outputs go to `/mnt/user-data/outputs/`. The user downloads them via `present_files`.

If the user mentions a specific save path (e.g. *"save to ~/Documents/Project"*), note that
Claude delivers files via download link — they can save locally from there.

---

## Reference files

Read these before writing for the first time:

- `references/brd-template.md` — Full BRD section structure with instructions per section
- `references/rtm-schema.md` — RTM JSON schema with field definitions and example entry

---

## Quick-start checklist

- [ ] Blueprint or description received
- [ ] Gap analysis done — gaps asked or assumptions documented
- [ ] `references/brd-template.md` read
- [ ] `references/rtm-schema.md` read
- [ ] BRD written with all REQ-IDs assigned
- [ ] RTM seed JSON generated
- [ ] Both files presented via `present_files`
- [ ] Summary table printed
- [ ] User invited to iterate