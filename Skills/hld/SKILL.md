---
name: hld-architect
description: >
  Generates a stakeholder-facing High-Level Design (HLD) document from a project
  requirements artefact (RTM JSON, PRD, or blueprint). Produces a single Markdown file
  containing the full HLD (architectural style, component overview, deployment topology,
  integration points, cross-cutting concerns, NFR mapping, ATAM-lite trade-off table) followed
  by the complete ADR log (ADR-001 through ADR-004) — all in one document. Trigger this skill
  whenever the user asks for an architecture document, solution design, HLD, high-level design,
  ADR log, architecture decision record, ATAM analysis, trade-off analysis, architectural style
  decision, or any combination thereof, especially when a requirements file, RTM, or project
  JSON is present in the conversation.
---

# HLD Architect Skill

Converts a project requirements artefact into a single Markdown file containing the complete
High-Level Design and all four ADRs, with ATAM-lite trade-offs woven in.

---

## 0. Prerequisites

Read the DOCX skill before generating any file:
```
/mnt/skills/public/docx/SKILL.md
```
Install the docx library if not already present:
```bash
npm list -g docx 2>/dev/null | grep -q docx || npm install -g docx
```

---

## 1. Inputs

### 1.1  Primary source — Cowork folder

The primary input is always the file(s) in the Cowork-configured folder, mounted at:

```
/mnt/user-data/uploads/
```

**Always start here.** Run this before anything else:

```bash
ls -lh /mnt/user-data/uploads/
```

Look for any of these file types and read accordingly:

| File type | Read command |
|-----------|-------------|
| `.json` (RTM / project JSON) | `cat /mnt/user-data/uploads/<file>.json` |
| `.md` / `.txt` (blueprint prose) | `cat /mnt/user-data/uploads/<file>.md` |
| `.docx` (Word brief) | `extract-text /mnt/user-data/uploads/<file>.docx` |
| `.pdf` (requirements doc) | see `/mnt/skills/public/pdf-reading/SKILL.md` |

If multiple files are present, read all of them — they are likely complementary (e.g. RTM JSON + blueprint markdown).

If `/mnt/user-data/uploads/` is **empty**, fall back in this order:
1. RTM/project JSON pasted directly in the conversation (`project`, `epics`, `features`, `requirements`, `stories` keys)
2. Free-text project description provided by the user

Do not proceed to extraction until at least one input source has been read.

### 1.2  Fields to extract

Extract these fields from the input before writing anything:

```
PROJECT_NAME   — project.project or inferred from title
VERSION        — project.version or "1.0"
DATE           — project.generated or today's date
EPICS          — list of epic titles
FEATURES       — list of features per epic
NFR_IDS        — all REQ-NF-* requirements (id + title + acceptance_criteria)
CONSTRAINT_IDS — all REQ-C-* requirements
INTEGRATION_IDS— all REQ-I-* requirements
ASSUMED_COUNT  — summary.by_status.ASSUMED
OPEN_ITEMS     — any OI-* references in notes fields
```

---

## 2. Architectural Style Decision

Before writing, select the **architectural style** from the table below using the decision tree.
This selection feeds ADR-001 and Section 3 of the HLD.

### Decision tree

```
Does the project have a separate frontend + backend + AI integration + external payments?
  YES →  Web-tier + API-tier + AI-proxy pattern
         Pick style: Modular Monolith (≤5,000 MAU target in v1) OR
                     Microservices (>50,000 MAU or multiple independent release cadences)

Does it have an explicit scalability NFR > 5,000 concurrent users?
  YES → lean toward Services/Event-driven
  NO  → lean toward Modular Monolith for v1 simplicity

Is the AI feature a core differentiator with independent SLA?
  YES → AI-Proxy Sidecar pattern (decoupled AI gateway)
  NO  → embed AI calls in main API layer
```

**STEMWidgets default** (derived from the seed RTM): **Modular Monolith + AI-Proxy Sidecar**
- Single deployable backend with internal module boundaries
- Dedicated AI Gateway module (own deployment unit if Claude/OpenAI SLA differs from web SLA)
- Stateless frontend (React SPA or equivalent) served via CDN

---

## 3. Document Structure

Generate the HLD `.docx` with these sections in order:

### 3.1 Cover & Document Control
- Title: `[PROJECT_NAME] — High-Level Solution Design`
- Version, date, status (Draft / For Review / Approved)
- Document control table: Version | Date | Author | Change Summary

### 3.2 Executive Summary (½ page)
- One paragraph: what the system does, who uses it, and the key architectural bet.
- Flag assumption count prominently: _"[N] requirements are currently ASSUMED and require
  stakeholder confirmation before detailed design."_

### 3.3 Architectural Goals & Constraints
Table with three columns: Goal/Constraint | Source (REQ-ID) | Implication for Design

Include every REQ-C-* and every REQ-NF-* that has a direct architectural implication.
Common examples:
- REQ-C-005 (no native mobile) → responsive web only, no React Native
- REQ-C-004 (Statistics only v1) → content model scoped to one subject
- REQ-NF-004 (99.5% uptime) → multi-AZ deployment or equivalent
- REQ-NF-009 (10k concurrent) → horizontal scaling path required

### 3.4 Architectural Style
Sub-sections:
1. **Selected Style**: name the pattern chosen in §2 above and one-paragraph rationale.
2. **Key Architectural Principles**: bullet list (e.g. Stateless API, Privacy-by-design,
   No-evaluation-at-any-layer, AI-fallback-safe).
3. **ATAM-Lite Trade-Off Table** — see §4 below.

### 3.5 Component Overview
Describe each logical component in prose + a component diagram described textually:

```
COMPONENT TABLE
Name | Responsibility | Technology Assumptions | Owns Data?
-----|----------------|------------------------|------------
Web Frontend     | Deliver SPA, responsive UI          | React / Next.js (CDN-served)     | No
API Gateway      | Routing, auth middleware, rate-limit | Node/Express or equiv.            | No
Auth Service     | JWT, OAuth, SAML/OIDC SSO            | Auth0 / Cognito (TBC)            | User profiles
Widget Engine    | Serve interactive widget definitions | Static assets + API              | Widget metadata
AI Gateway       | Proxy to LLM API, prompt mgmt, scope| Thin Node service                 | No (REQ-D-003)
Subscription Svc | Stripe webhooks, tier management    | Stripe SDK                        | Subscription records
Analytics Engine | Ingest session events, dashboard    | Event pipeline → OLAP store      | Session/engagement
```

> Note: Add or remove rows to match the actual project's features.

### 3.6 Deployment Topology
Describe in prose (and optionally ASCII) the runtime topology:
- CDN → Load Balancer → App Servers (stateless) → DB / Cache
- AI Gateway as separate pod/service
- Data tier: primary DB, read replica, event store
- Third-party SaaS: Stripe, LLM provider, SSO IdP

Include one-paragraph note on environment strategy: local dev / staging / production.

### 3.7 Data Architecture Summary
Subsections:
- **Data entities**: list key entities (User, Session, Subscription, Widget, AIConversation)
- **Persistence choices**: rationale for relational vs. document vs. event store
- **Privacy constraints**: map REQ-D-003 (no AI persistence), REQ-D-004 (30-day purge),
  REQ-C-002 (GDPR), REQ-C-003 (COPPA) to data-layer controls
- **Analytics schema note**: reference REQ-F-019 / REQ-D-002 — no evaluation fields

### 3.8 Integration Architecture
Table: Integration | Direction | Protocol | Auth | Notes
- Stripe (outbound, REST webhooks, API key)
- LLM API / Claude API (outbound, REST/SSE streaming, API key, see ADR-003)
- Google OAuth (outbound, OIDC, client secret)
- Institution SSO (inbound, SAML 2.0 + OIDC, PKI)
- Google Colab (outbound, URL construction, none)

### 3.9 Cross-Cutting Concerns
For each concern, one short paragraph + design decision:

| Concern | Decision |
|---------|---------|
| Authentication & Authorisation | JWT + role enum (free / paid / institution / admin) |
| Observability | Structured logs + distributed trace IDs; no PII in logs |
| Error Handling | AI fallback per REQ-NF-008; graceful degradation hierarchy |
| Scalability | Horizontal stateless API; AI Gateway independently scalable |
| Accessibility | WCAG 2.1 AA as build constraint per REQ-NF-006 |
| Security | OWASP Top 10 baseline; no sensitive data in URL params |

### 3.10 Non-Functional Requirements Mapping
Table: NFR ID | Title | Target | Architectural Response | Validation Method
Pull every REQ-NF-* row from the input and map it here.

### 3.11 Risks & Open Items
Two sub-tables:

**Assumed Requirements Needing Confirmation**
Assumption Ref | Area | Risk if Wrong | Owner

**Open Items**
OI Ref | Description | Impact | Target Resolution Date

Populate from `notes` fields containing `A-0xx` and `OI-0xx` references.

### 3.12 ADR Summary
Single table: ADR-ID | Title | Status | Decision | Date
List ADR-001 through ADR-004 (detail in separate files).

### 3.13 Glossary
Short glossary of domain terms: Widget, Freemium, AI Advisor, SSO, ATAM, ADR, etc.

---

## 4. ATAM-Lite Trade-Off Table

Embed in Section 3.4 of the HLD. Evaluate the selected style against four quality attributes:

```
Quality Attribute | Benefit of Selected Style | Sensitivity Point | Trade-off
------------------|--------------------------|-------------------|----------
Performance       | CDN + stateless API → low latency for widgets | Widget state pushed to client | Client JS bundle size; mitigated by code-split
Scalability       | Stateless API scales horizontally | Shared DB is scaling bottleneck at high concurrency | Introduce read replicas + connection pooling before 5k MAU
Modifiability     | Module boundaries enable team parallelism | Intra-monolith coupling risk | Enforce module contracts; plan migration path to services post v1
Security/Privacy  | AI-proxy centralises prompt policy + PII control | Single point of AI policy failure | Prompt guard tests in CI; no PII in AI context by design
Reliability       | AI isolation means widget/code features survive AI outage (REQ-NF-008) | AI Gateway SPOF | Deploy AI Gateway with independent health check + circuit breaker
```

Adapt sensitivity points and mitigations to actual NFRs in the input.

---

## 5. ADR Files

Generate **one consolidated Markdown file** (`[project-slug]-ADR-log.md`) containing all four
ADRs in sequence, separated by horizontal rules. Do not create separate files per ADR.

Use this template for each:

```markdown
# ADR-NNN: [Title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded
**Deciders:** [Engineering Lead, Product, Architect]
**Supersedes:** —

## Context

[1–2 paragraphs: what is the architectural question, what forces are at play,
what requirements drive this decision — cite REQ-IDs]

## Decision

[1 paragraph: the decision made, stated clearly]

## Consequences

**Positive:**
- bullet list

**Negative / Risks:**
- bullet list

**Mitigation:**
- bullet list

## Alternatives Considered

| Alternative | Reason Rejected |
|------------|----------------|
| [Alt 1]    | [Why not]       |
| [Alt 2]    | [Why not]       |
```

### ADR-001: Architectural Style

**Context drivers:** Performance (REQ-NF-001, REQ-NF-002), Scalability (REQ-NF-009),
Time-to-market, Team size.
**Decision:** Modular Monolith with AI-Proxy Sidecar for v1.
**Key trade-off:** Faster delivery + simpler ops vs. service-level independent deployment.
Mitigation: enforce internal module contracts to enable extraction post-v1.

### ADR-002: Frontend Delivery Model

**Context drivers:** REQ-NF-001 (TTI < 3s), REQ-NF-005 (responsive web),
REQ-C-005 (no native mobile), REQ-F-005 (widget responsiveness ≤ 100ms).
**Decision:** React SPA served from CDN; widgets rendered client-side.
**Key trade-off:** Rich interactivity + offline-resilient widgets vs. SEO (not a priority for
authenticated learning tool) and initial bundle size.

### ADR-003: LLM API Provider Selection

**Context drivers:** REQ-I-002 (LLM integration), REQ-NF-003 (5s streaming SLA),
REQ-F-013 (no evaluative language), OI-004 (provider selection pending).
**Decision:** Defer final provider selection; build behind AI Gateway abstraction.
Current candidates: Anthropic Claude API, OpenAI API.
**Key trade-off:** Flexibility vs. provider lock-in. Abstraction adds one layer of latency.
Mitigation: adapter pattern + provider SLA comparison test before go-live.

### ADR-004: Data Persistence Strategy

**Context drivers:** REQ-D-003 (no AI conversation persistence), REQ-D-004 (30-day purge),
REQ-C-002 (GDPR), REQ-NF-009 (10k concurrent users), REQ-F-018 (analytics dashboard).
**Decision:** Relational DB for transactional data (users, subscriptions); append-only
event store for analytics; no AI conversation written to persistent storage.
**Key trade-off:** Operational simplicity of single DB vs. analytics query performance.
Mitigation: CQRS-lite — write events to append store, materialise dashboard views on schedule.

---

## 6. Output File

Deliver **one file** to `/mnt/user-data/outputs/`:

```
[project-slug]-HLD-v[version].md
```

Structure of the single file:
1. HLD content (Sections 1–13 as defined in §3 above)
2. A `---` horizontal rule
3. ADR log (all four ADRs in sequence, each separated by `---`)

Then call `present_files` with the single path.

---

## 7. Markdown Formatting Guide

Write the output as clean, portable Markdown:

- `#` for the document title
- `##` for top-level HLD sections (1. Executive Summary, 2. Scope, …)
- `###` for sub-sections and individual ADR titles
- Tables using standard GFM pipe syntax
- Fenced code blocks (``` ``` ```) for any code or command examples
- `---` as section separator between the HLD body and the ADR log, and between each ADR
- No HTML tags; no front-matter beyond a simple title line

---

## 8. Quality Checklist

Before presenting outputs, verify:

- [ ] Every REQ-NF-* has a row in Section 3.10
- [ ] Every REQ-C-* has a row in Section 3.3
- [ ] Every REQ-I-* has a row in Section 3.8
- [ ] ATAM table has ≥ 5 quality attributes evaluated
- [ ] Single output .md file contains both full HLD and all four ADRs separated by ---
- [ ] ADR-001 explicitly names the architectural style chosen
- [ ] Risks table lists all ASSUMED requirements with owner column
- [ ] Open Items table lists all OI-* references found in notes
- [ ] No scores, grades, or evaluation language anywhere in document
  (mirrors the product's own no-evaluation constraint)
- [ ] Document validates without errors