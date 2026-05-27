---
name: fullstack-architect
description: >
  Operationalises an HLD into a concrete fullstack tier map. Reads the RTM JSON and HLD
  Markdown from the Cowork folder, assigns permanent TIER-IDs to every system layer
  (TIER-001 through TIER-NNN), populates tier_ids back into a enriched RTM JSON, and
  produces a single Markdown output file containing the tier map document plus the updated
  RTM summary. Trigger this skill whenever the user asks for a tier map, fullstack
  architecture, tier IDs, system layers, TIER-IDs, operationalise the HLD, concrete
  architecture, stack layers, or wants to lock down which tier owns which requirement.
  Always trigger when both an RTM JSON and an HLD document are present in the Cowork folder.
---

# Fullstack Architect Skill

Reads the HLD + RTM from the Cowork folder and produces:
1. A **Tier Map** — every system layer named, described, and assigned a permanent `TIER-ID`
2. An **enriched RTM JSON** — every requirement annotated with the `tier_ids` that implement it
3. A single `.md` output file containing both, delivered to `/mnt/user-data/outputs/`

---

## 0. Prerequisites

No additional libraries required. All output is Markdown + JSON written with standard bash/Python.

---

## 1. Inputs

### 1.1  Primary source — Cowork folder

Always start by listing the Cowork folder:

```bash
ls -lh /mnt/user-data/uploads/
```

Look for **two files**:

| File | Role | How to read |
|------|------|-------------|
| `*.json` (RTM) | Requirements, epics, features, stories | `cat /mnt/user-data/uploads/<file>.json` |
| `*.md` (HLD) | Architecture decisions, component overview, deployment topology | `cat /mnt/user-data/uploads/<file>.md` |

Read **both** before doing anything else. If only the RTM is present, derive tier map from it
directly (the HLD sections you need are: Component Overview, Deployment Topology, Integration
Architecture). If neither file is present, ask the user to add them to the Cowork folder.

### 1.2  What to extract from the RTM JSON

```
PROJECT_NAME      — project.project
VERSION           — project.version
ALL_REQUIREMENTS  — requirements[] — id, title, category, feat_id, notes
INTEGRATIONS      — requirements where category == "Integration"
NFR_LIST          — requirements where category == "Non-Functional"
CONSTRAINTS       — requirements where category == "Constraint"
DATA_REQS         — requirements where category == "Data"
EPICS             — epics[] titles
FEATURES          — features[] titles
```

### 1.3  What to extract from the HLD Markdown

```
COMPONENTS        — Component Overview table rows (name + responsibility)
DEPLOYMENT_NOTES  — Deployment Topology section (tier boundaries described)
INTEGRATIONS_HLD  — Integration Architecture table (name + protocol + direction)
CROSS_CUTTING     — Cross-Cutting Concerns section (auth, observability, security, etc.)
ADR_DECISIONS     — ADR Summary table (style, frontend, LLM, data)
```

---

## 2. TIER-ID System

### 2.1  Permanent ID format

```
TIER-NNN   where NNN is a zero-padded integer starting at 001
```

IDs are **permanent** — once assigned they never change, even if tiers are added or removed
in later versions. New tiers append to the sequence. Gaps are allowed (a removed tier leaves
its ID retired, not reused).

### 2.2  Standard tier taxonomy

Assign tiers in this canonical order. Every project gets all tiers that are relevant; omit
only tiers that have zero requirements or components mapped to them.

| TIER-ID | Layer Name | Canonical Responsibility |
|---------|-----------|--------------------------|
| TIER-001 | Client Layer | Browser-executed code: SPA shell, routing, page components |
| TIER-002 | Widget & Interaction Layer | Client-side interactive components; widget canvas; state machines |
| TIER-003 | Code Snippet & Tooling Layer | Syntax-highlighted code display; clipboard; external execution links |
| TIER-004 | CDN & Static Asset Layer | Static file delivery: JS bundles, CSS, widget definitions, snippet JSON |
| TIER-005 | API Gateway Layer | HTTP routing, auth middleware, rate-limiting, CORS, request validation |
| TIER-006 | Auth & Identity Layer | JWT issuance/validation, OAuth, SAML/OIDC SSO, age-gate logic |
| TIER-007 | Subscription & Billing Layer | Plan management, tier gating, Stripe integration, seat limits |
| TIER-008 | AI Gateway Layer | LLM API proxy, SSE streaming, prompt management, non-eval guard, scope restriction |
| TIER-009 | Analytics & Observability Layer | Event ingestion, session tracking, dashboard materialisation, structured logs |
| TIER-010 | Data Layer | Relational DB (transactional), event store (analytics), cache (rate-limit/JWT), purge jobs |
| TIER-011 | Integration & Messaging Layer | Third-party webhooks, outbound API calls, Stripe webhooks, Colab URL construction |
| TIER-012 | Infrastructure & Platform Layer | Cloud hosting, multi-AZ, load balancer, CI/CD pipeline, secrets management |
| TIER-013 | Compliance & Governance Layer | GDPR erasure, COPPA age-gate data, data retention policy, legal sign-off gates |

Add project-specific tiers after TIER-013 if the HLD or RTM reveals layers not covered above.
Document the addition in the tier map with a note: `[PROJECT-SPECIFIC]`.

### 2.3  Rules for tier assignment

- A requirement maps to **one primary tier** (the tier that implements it) and optionally one
  or more **secondary tiers** (tiers that must cooperate to satisfy it).
- Non-functional requirements (REQ-NF-*) often span multiple tiers — list all that apply.
- Integration requirements (REQ-I-*) map to TIER-011 as primary, plus the tier that consumes
  the integration (e.g. TIER-007 for Stripe, TIER-008 for LLM).
- Constraint requirements (REQ-C-*) map to the tier that enforces the constraint.
- Data requirements (REQ-D-*) map to TIER-010 as primary.
- Compliance requirements map to TIER-013 as primary, with secondary tiers for enforcement points.

---

## 3. Output: Tier Map Document

The tier map is the primary deliverable. Structure it exactly as follows.

### 3.1  Document header

```markdown
# [PROJECT_NAME] — Fullstack Tier Map

| Field | Value |
|---|---|
| Version | [VERSION] |
| Date | [TODAY] |
| Status | Locked — TIER-IDs are permanent |
| Source HLD | [HLD filename] |
| Source RTM | [RTM filename] |

> TIER-IDs assigned in this document are permanent identifiers.
> New tiers append to the sequence. Existing IDs are never reassigned.
```

### 3.2  Tier registry table

One row per tier. This is the locked reference table.

```markdown
## Tier Registry

| TIER-ID | Layer Name | Primary Technology | Scales Independently? | Owner Module |
|---------|-----------|-------------------|----------------------|-------------|
| TIER-001 | Client Layer | React SPA | No (CDN) | Frontend |
| TIER-002 | Widget & Interaction Layer | Client-side JS (in-browser) | No (client) | Frontend |
...
```

Populate `Primary Technology` from the HLD Component Overview / ADR decisions.
`Scales Independently?` = Yes if the HLD notes the tier can be scaled without scaling others.
`Owner Module` = the module name from the HLD Component Overview.

### 3.3  Tier detail cards

For each tier, write a detail card:

```markdown
---

### TIER-001 — Client Layer

**Responsibility:** [one sentence from component overview or derived from HLD]

**Technology stack:**
- [framework / library]
- [delivery mechanism]

**Requirements owned (primary):**
| REQ-ID | Title | Category |
|--------|-------|---------|
| REQ-F-005 | Widget Rendering | Functional |
...

**Requirements supported (secondary):**
| REQ-ID | Title | Primary Tier |
|--------|-------|-------------|
| REQ-NF-001 | Page Load Performance | TIER-004 |
...

**Interfaces:**
- Upstream: [what calls into this tier]
- Downstream: [what this tier calls]

**Key constraints / NFRs:**
- [bullet list of hard constraints that govern this tier's design]

**ADR references:** [list any ADRs that affect this tier]
```

Write a card for every tier in the registry.

### 3.4  Requirement-to-tier cross-reference table

After all tier cards, include a flat cross-reference:

```markdown
## Requirement → Tier Cross-Reference

| REQ-ID | Title | Category | Primary TIER-ID | Secondary TIER-IDs |
|--------|-------|---------|----------------|-------------------|
| REQ-F-001 | User Registration | Functional | TIER-006 | TIER-005, TIER-010 |
...
```

Every requirement from the RTM must appear exactly once as the primary owner.

### 3.5  Tier interaction diagram (text)

```markdown
## Tier Interaction Diagram

```
[TIER-001: Client Layer]
    │ HTTP/S (REST + SSE)
    ▼
[TIER-005: API Gateway]
    ├──▶ [TIER-006: Auth & Identity]
    ├──▶ [TIER-007: Subscription & Billing] ──▶ [TIER-011: Integration] ──▶ Stripe
    ├──▶ [TIER-008: AI Gateway] ──▶ [TIER-011: Integration] ──▶ LLM API
    ├──▶ [TIER-009: Analytics] ──▶ [TIER-010: Data Layer]
    └──▶ [TIER-010: Data Layer]

[TIER-004: CDN] ──▶ [TIER-001: Client]
                ──▶ [TIER-002: Widget assets]
                ──▶ [TIER-003: Snippet assets]

[TIER-012: Infrastructure] wraps all deployed tiers
[TIER-013: Compliance] cross-cuts TIER-006, TIER-008, TIER-010
```
```

Adapt the diagram to the actual tier set derived from the project.

---

## 4. Output: Enriched RTM JSON

After the tier map document, produce an **enriched RTM JSON block** — the original RTM
`requirements` array with `tier_ids` added to every requirement object.

Format:

```json
{
  "project": "...",
  "version": "...",
  "tier_map_version": "1.0",
  "tier_map_date": "YYYY-MM-DD",
  "requirements": [
    {
      "id": "REQ-F-001",
      "title": "User Registration",
      "category": "Functional",
      "tier_ids": {
        "primary": "TIER-006",
        "secondary": ["TIER-005", "TIER-010"]
      },
      ...all original fields preserved...
    }
  ]
}
```

Rules:
- Every requirement gets a `tier_ids` object with `primary` (string) and `secondary` (array,
  may be empty).
- All original requirement fields are preserved unchanged.
- Output the full `requirements` array — do not truncate.
- Also add a `tier_registry` top-level key listing all TIER-IDs and their names.

---

## 5. Output File

Deliver **one file** to `/mnt/user-data/outputs/`:

```
[project-slug]-tier-map-v[version].md
```

Structure of the single file:

```
# [Project] — Fullstack Tier Map          ← Section 1: document header
## Tier Registry                           ← Section 2: locked registry table
---                                        ← separator
### TIER-001 — Client Layer               ← Section 3: one card per tier
...
### TIER-NNN — ...
---                                        ← separator
## Requirement → Tier Cross-Reference     ← Section 4: flat cross-reference
---                                        ← separator
## Tier Interaction Diagram               ← Section 5: text diagram
---                                        ← separator
## Enriched RTM (tier_ids populated)      ← Section 6: heading
```json                                    ← fenced JSON block
{ enriched RTM JSON }
```
```

Then call `present_files` with the single path.

---

## 6. Markdown Formatting Guide

- `#` for the document title
- `##` for top-level sections (Tier Registry, Cross-Reference, etc.)
- `###` for individual tier cards (TIER-001 — Client Layer, etc.)
- GFM pipe tables for all tabular data
- Fenced code blocks for the interaction diagram and the enriched RTM JSON
- `---` as separator between major sections
- No HTML tags

---

## 7. Quality Checklist

Before calling `present_files`, verify:

- [ ] Every component from the HLD Component Overview maps to exactly one primary tier
- [ ] Every REQ-* from the RTM appears exactly once in the cross-reference table as primary owner
- [ ] Every tier in the registry has a detail card
- [ ] TIER-IDs are contiguous from TIER-001 with no gaps (unless a tier was explicitly retired)
- [ ] Enriched RTM JSON contains `tier_ids` on every requirement object
- [ ] `tier_registry` key present at the top level of the enriched JSON
- [ ] No requirement is left with an empty `primary` tier
- [ ] Integration requirements (REQ-I-*) all have TIER-011 as primary or secondary
- [ ] Data requirements (REQ-D-*) all have TIER-010 as primary
- [ ] Compliance/constraint requirements map to TIER-013 or the enforcing tier
- [ ] Output is a single `.md` file