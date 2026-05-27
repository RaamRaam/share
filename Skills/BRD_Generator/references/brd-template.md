# BRD Section Template

Use this structure for every BRD. Populate every section — no section may be left empty.
Use `[ASSUMED]` inline for inferred values, and record them in §A.

---

## Document Header

```
# [Product Name] — Business Requirements Document
Version: 1.0  |  Status: DRAFT  |  Date: [YYYY-MM-DD]
Owner: [name or TBD]  |  Prepared by: Claude (STEMWidgets BRD Generator skill)
```

---

## §0 — Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | DRAFT |
| Created | [date] |
| Last Updated | [date] |
| Owner | [TBD or name] |
| Reviewers | [TBD] |

**Change log** (table, updated on every revision):
| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | [date] | Claude | Initial generation from blueprint |

---

## §1 — Executive Summary

2–4 sentence summary: what the product is, who it serves, and the single most important
business goal.

---

## §2 — Business Context

### 2.1 Problem Statement
Restate from blueprint (refined, not copy-pasted). Include quantified pain where possible.

### 2.2 Opportunity
Market size, timing, why now.

### 2.3 Proposed Solution
One paragraph. What the product does and how it solves the problem.

---

## §3 — Stakeholders & Users

Table of all user types and stakeholders. For each:
- Type (Primary User / Secondary User / Buyer / Admin / Regulator etc.)
- Description
- Primary goal on the platform
- Pain point being solved

---

## §4 — Scope

### 4.1 In Scope (v1)
Bulleted list of features/capabilities included.

### 4.2 Out of Scope (v1)
Bulleted list of explicitly excluded features. Important: out-of-scope items prevent scope
creep and inform future phase planning.

### 4.3 Future Phases (indicative)
Brief notes on what's planned for v2+ based on blueprint signals.

---

## §5 — Functional Requirements

Group by feature area (e.g. 5.1 Widget Engine, 5.2 AI Assistant, 5.3 Subscriptions, etc.)

Each requirement follows this format:
```
**REQ-F-NNN** — [Title]
The system SHALL/SHOULD/MAY [verb] [object] [condition/constraint].
Priority: HIGH / MEDIUM / LOW
Source: [feature name from blueprint §4]
```

Include acceptance criteria inline where the requirement is complex:
```
Acceptance: Given [X], when [Y], then [Z].
```

---

## §6 — Non-Functional Requirements

Group by quality attribute: Performance, Reliability, Security, Usability, Accessibility,
Scalability, Maintainability.

Each requirement follows:
```
**REQ-NF-NNN** — [Title]
The system SHALL [quality attribute statement with measurable threshold].
Priority: HIGH / MEDIUM / LOW
Rationale: [why this matters — link to business goal or metric where possible]
```

---

## §7 — Constraints

Tech stack constraints, legal/compliance constraints, business constraints.

```
**REQ-C-NNN** — [Title]
The system SHALL be built using / comply with / operate within [constraint].
Type: TECHNICAL / LEGAL / BUSINESS
```

---

## §8 — Data Requirements

Data entities, storage, retention, privacy classification.

```
**REQ-D-NNN** — [Title]
The system SHALL [store / retain / protect / delete] [data entity] [condition].
Privacy class: PUBLIC / INTERNAL / CONFIDENTIAL / RESTRICTED
```

---

## §9 — Integration Requirements

External systems, APIs, SSO, payment, analytics.

```
**REQ-I-NNN** — [Title]
The system SHALL integrate with [external system] to [purpose].
Interface type: REST API / SSO / Webhook / SDK / etc.
```

---

## §10 — Success Metrics & Acceptance Criteria

North star metric, funnel metrics, and measurable launch criteria. Map each metric to the
relevant requirements. Include the 6-month targets from the blueprint.

---

## §11 — Risks & Mitigations

Carry over from blueprint §10. Add any new risks surfaced during requirements analysis.
Each risk: description, likelihood (H/M/L), impact (H/M/L), mitigation, owner.

---

## §A — Assumptions Register

Every `[ASSUMED]` value in the document is listed here with:
- ID (ASM-NNN)
- The assumption made
- The requirement(s) it affects
- How to validate/confirm
- Status: ASSUMED / CONFIRMED / REJECTED

---

## §B — Glossary

Define domain-specific terms, acronyms, and abbreviations used in the document.

---

## §C — Open Items

Items that require owner decision before the BRD can be finalised.

| # | Item | Owner | Due | Status |
|---|---|---|---|---|
| OI-001 | [description] | TBD | TBD | OPEN |

---

*End of BRD template*