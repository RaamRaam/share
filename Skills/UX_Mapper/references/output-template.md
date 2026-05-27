# Output Template

This is the exact scaffold for `[slug]-ux-artefacts.md`.
Copy it verbatim, then fill every `{placeholder}`.
Do not add extra sections, rename headings, or reorder blocks.

---

## Full file

````markdown
---
project: {Project Name}
document: ux-artefacts
version: "1.0"
generated: {YYYY-MM-DD}
source: {filename or "provided inline"}
user_types: ["{Role 1}", "{Role 2}"]
req_ids_total: {N}
req_ids_linked: {N}
---

# {Project Name} — UX Artefacts

> {N} user types · {N} journey stages · {N} req-IDs linked · Generated {YYYY-MM-DD}

| User type | Tier | Key req-IDs | Journey stages |
|---|---|---|---|
| {emoji} {Role} | {TIER} | `{ID}`, `{ID}`, `{ID}` | {N} |

---

## {emoji} {Fictional Name} — {Role Label}

### Persona card

**Tier:** {FREE \| PAID \| INSTITUTIONAL \| PLATFORM-ADMIN \| GENERAL}
**Age / context:** {age, role context — one line}
**Key req-IDs:** `{ID}`, `{ID}`, `{ID}`
**Behaviour tags:** `{tag}` · `{tag}` · `{tag}`

> "{First-person quote derived from acceptance criteria language}"

**Goal:** {One sentence — the functional outcome this user's confirmed requirements enable}

**Frustration:** {One sentence — what constraints or unresolved assumptions create friction for this user}

---

### Empathy map

#### 🧠 Thinks
- {Derived from ASSUMED/DRAFT reqs and open-item notes for this user}
- {bullet}
- {bullet}
- {bullet}

#### ❤️ Feels
- {Derived from Non-Functional requirements — performance/reliability/accessibility thresholds}
- {bullet}
- {bullet}
- {bullet}

#### 💬 Says
- {Derived from AC phrasing rewritten in first person}
- {bullet}
- {bullet}
- {bullet}

#### 🤲 Does
- {Derived from action verbs in acceptance criteria}
- {bullet}
- {bullet}
- {bullet}

#### ⚠️ Pains
- {Derived from ASSUMED/DRAFT reqs, constraints, requirements whose failure hurts this user}
- {bullet}
- {bullet}
- {bullet}

#### 🌱 Gains
- {Derived from CONFIRMED requirements that directly serve this user}
- {bullet}
- {bullet}
- {bullet}

---

### Journey map

| Stage | Touchpoint | User action | Emotion | Tier | Req-IDs | Notes |
|---|---|---|---|---|---|---|
| {stage} | {screen / email / system} | {what the user does — one sentence} | {word emoji} | {TIER} | `{ID}` | {AC snippet \| [ASSUMED: topic] \| OI: topic \| See {ID} \| —} |

---

{Repeat the full ## block for each additional user type}

---

## Req-ID Index

> All req-IDs referenced in the journey maps above.

| Req-ID | Title | Category | Status | Referenced by |
|---|---|---|---|---|
| `{ID}` | {title from JSON} | {category} | {CONFIRMED \| ASSUMED \| DRAFT} | {Role 1, Role 2} |

**Not referenced in any journey** (infrastructure / below journey layer):
{Comma-separated IDs with one-line reason each, or "None"}
````

---

## Formatting rules

### Frontmatter
- Always YAML, always first in the file
- `user_types` — YAML list, quoted strings
- `req_ids_total` — count of all IDs in the input JSON
- `req_ids_linked` — count of unique IDs appearing in at least one journey table row

### Section hierarchy
- `##` — one per user type; format: `## {emoji} {Fictional Name} — {Role Label}`
- `###` — Persona card / Empathy map / Journey map (three per user type block, in that order)
- `####` — one per empathy map cell (six per map)

### Persona card
- One field per line, `**Field:**` bold label
- Tier uses `\|` to escape the pipe character inside inline code option lists
- Key req-IDs: backtick each, comma-separated, on one line
- Behaviour tags: backtick each, separated by ` · ` (space · space)
- Quote: always a `>` blockquote on its own line, always first-person
- Goal and Frustration: plain sentences, no bullets, no sub-labels

### Empathy map
- 4–5 bullets per cell; no sub-bullets
- Every bullet must reference a specific product behaviour, requirement, or AC
- Do not write generic statements like "Wants to succeed" or "Worries about the future"
- Pains: cite the req-ID or assumption that causes the pain where possible
- Gains: cite the CONFIRMED req-ID that delivers the gain where possible

### Journey map table
- Emotion: exactly one word + one emoji from the approved vocabulary
- Tier column: all-caps — FREE / PAID / INSTITUTIONAL / ADMIN / GENERAL
- Req-IDs: backtick each; if multiple: `` `ID-1`, `ID-2` ``; if none: `—`
- Notes: one of the following only —
  - Short AC quote (≤10 words, in double quotes)
  - `[ASSUMED: brief topic]`
  - `OI: brief topic` (open item)
  - `See {ID}` (cross-reference)
  - `—` (nothing relevant)
- Every row must have either at least one req-ID or `—`, never blank

### Separators
- `---` between each `##` user type block
- `---` between Persona card and Empathy map within a block
- `---` between Empathy map and Journey map within a block
- `---` before the Req-ID Index section

### Emoji per user type
Assign one emoji per user type; use it consistently in the summary table, section header,
and index. Pick the closest fit:

| User type pattern | Emoji |
|---|---|
| Student / Learner | 🎓 |
| Individual user / Consumer | 👤 |
| Institutional buyer / Org admin | 🏫 |
| Platform / Internal ops admin | ⚙️ |
| Teacher / Educator / Trainer | 📚 |
| Developer / Technical user | 💻 |
| Manager / Decision-maker | 💼 |
| Healthcare / Clinical user | 🏥 |
| Customer / End consumer | 🛒 |
| Other / Unclassified | 🔬 |