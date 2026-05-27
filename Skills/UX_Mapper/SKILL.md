---
name: ux-mapper
description: >
  Generates persona cards, empathy maps, and end-to-end user journey maps for every user
  type in any product, from a requirements JSON file. Outputs a single Markdown file written
  directly to a folder on the user's machine. Use this skill whenever the user wants to:
  create personas, build empathy maps, map user journeys, generate UX docs from a requirements
  JSON, understand who the users are and what they experience, or produce UX artefacts for
  any app. Trigger on: "create personas", "empathy map", "user journey", "journey map",
  "UX artefacts", "map the user experience", "who are our users", or whenever a requirements
  JSON is provided and UX output is requested. Always use this skill rather than ad-hoc persona writing.
---

# UX Mapper

Reads a requirements JSON, generates UX artefacts, and writes one Markdown file directly
to a folder on the user's machine using bash.

---

## Phase 0 — Resolve paths

Ask the user two things before doing anything else. Ask both in one message:

> 1. "Where is the requirements JSON file? (full path, e.g. `~/Projects/myapp/rtm.json`)"
> 2. "Which folder should I save the output to? (e.g. `~/Projects/myapp/`)"

If the user has already provided one or both of these in their message, skip asking for it.

Store both paths. Create the output folder if it doesn't exist:

```bash
mkdir -p "{output_folder}"
```

Confirm before proceeding:
> Reading: `{json_path}`
> Writing: `{output_folder}/{slug}-ux-artefacts.md`

---

## Phase 1 — Read the JSON

```bash
cat "{json_path}"
```

Parse the `requirements` array. Each entry needs at minimum:
`id`, `title`, `category`, `priority`, `status`, `acceptance_criteria`, `notes`

Adapt to whatever schema is present — the field names above are conventions, not requirements.

---

## Phase 2 — Extract user types

Scan every field of every requirement to identify distinct user types.

**Where to look:**

| Field | Signal |
|---|---|
| `title` | Subject of the action — "User registers", "Admin configures", "Institution provisions" |
| `acceptance_criteria` | The actor in each sentence — "A user can...", "An admin sees..." |
| `notes` | Tier restrictions ("paid-tier only"), role names, assumption/open-item tags |
| `category` | Constraint/Data reqs reveal compliance obligations that map to specific roles |

**Tier inference:**

| Language in the data | Tier |
|---|---|
| "unauthenticated", "free tier", "without paying" | FREE |
| "paid tier", "subscriber", "subscription", "premium" | PAID |
| "institution", "admin", "SSO", "seat", "licence", "bulk" | INSTITUTIONAL |
| "platform owner", "internal dashboard", "analytics for the team" | PLATFORM-ADMIN |
| No tier signal | GENERAL |

For each user type collect: role name, tier, all req-IDs where this user is the subject or beneficiary.

If two user types are ambiguous, ask ONE clarifying question before continuing.

---

## Phase 3 — Generate artefacts

Read `references/output-template.md` for exact structure and all formatting rules.
Read `references/journey-stages.md` for stage derivation method and emotion vocabulary.

### 3.1 Persona cards

One per user type. Derive every field from the requirements — no invented context.

| Field | Source |
|---|---|
| Fictional name + role | Name invented; role from user type extraction |
| Tier | Phase 2 tier inference |
| Age / context | Infer from role — one line only |
| Goal | The functional outcome this user's CONFIRMED requirements enable |
| Frustration | What Constraint/NF requirements protect against; what ASSUMED reqs leave unresolved |
| Quote | First-person sentence built from acceptance criteria language |
| Behaviour tags | Inferred from AC patterns: "50+ times" → `repeat-till-clear`; "without contacting support" → `self-serve` |
| Key req-IDs | Up to 5 — most central to this user's core value |

### 3.2 Empathy maps

One per user type. Six cells. 4–5 bullets each.
Every bullet must reference a specific requirement — no generic filler.

| Cell | Derive from |
|---|---|
| 🧠 Thinks | ASSUMED/DRAFT reqs and open-item notes — unresolved questions in the user's mind |
| ❤️ Feels | Non-Functional reqs — performance/reliability/accessibility thresholds produce emotional states |
| 💬 Says | Acceptance criteria rewritten in first person |
| 🤲 Does | Action verbs from acceptance criteria |
| ⚠️ Pains | ASSUMED/DRAFT reqs, constraints, reqs whose failure hurts this user |
| 🌱 Gains | CONFIRMED reqs that directly serve this user |

### 3.3 Journey maps

One table per user type. Columns: `Stage | Touchpoint | User action | Emotion | Tier | Req-IDs | Notes`

Derive stages from the requirements — not from a fixed list.
See `references/journey-stages.md` for the derivation method and emotion vocabulary.

---

## Phase 4 — Write the file

Build the complete markdown string following `references/output-template.md` exactly.

File name: `{project-slug}-ux-artefacts.md`
Slug derived from the `project` field in the JSON, or from the JSON filename — lowercased with hyphens.

Write directly to the user's folder:

```bash
cat > "{output_folder}/{slug}-ux-artefacts.md" << 'MDEOF'
{full markdown content}
MDEOF
echo "Saved: {output_folder}/{slug}-ux-artefacts.md"
```

Confirm in chat:
```
✅ Saved → {output_folder}/{slug}-ux-artefacts.md
   {N} personas · {N} empathy maps · {N} journey maps ({total stages} stages)
   {N} req-IDs linked · {N} [ASSUMED] flags
```

---

## Phase 5 — Live updates

After the file is written, the session stays open for changes.
Rewrite the file in place on every change — do not ask for permission:

```bash
cat > "{output_folder}/{slug}-ux-artefacts.md" << 'MDEOF'
{updated full markdown}
MDEOF
```

Confirm: *"Updated {persona name} — {what changed}. File overwritten at {path}."*

Handle:
- Add a persona → new full block + index row
- Update a journey stage → update that row
- Add/remove a req-ID → update row + index
- Change quote or tag → update persona card
- Promote an assumption → remove `[ASSUMED]` flag, update index status

---

## Reference files

- `references/output-template.md` — exact Markdown structure, frontmatter, all formatting rules
- `references/journey-stages.md` — lifecycle positions, stage derivation method, emotion vocabulary

---

## Checklist

- [ ] JSON path and output folder confirmed with user before starting
- [ ] Output folder created with `mkdir -p`
- [ ] JSON read via `cat`
- [ ] User types extracted, tiers inferred, req-IDs mapped per user
- [ ] `references/output-template.md` read
- [ ] `references/journey-stages.md` read
- [ ] All persona cards written (fields grounded in requirements)
- [ ] All empathy maps written (6 cells, 4–5 bullets, no generic filler)
- [ ] All journey maps written (stages derived from requirements)
- [ ] Req-ID index complete
- [ ] File written via `cat >` heredoc to user's folder
- [ ] Confirmation with full path printed in chat