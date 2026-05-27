---
name: solution-architecture
description: >
  Master technical reference skill — produces a Solution Architecture Document (SAD) from
  an RTM JSON plus any prior artefacts (HLD, Tier Map, Milestone Plan, TC Registry) found
  in the Cowork folder. Assigns permanent COMP-IDs to every deployable or logical component,
  generates component diagrams, six sequence diagrams, a deployment view, ADR-005 through
  ADR-008 (four SAD-level decisions not covered in the HLD ADR log), a scalability model,
  and a DR strategy. Enriches the RTM JSON with sad_component and adr_ids fields on every
  requirement. Output: one .md file. Trigger this skill whenever the user asks for a SAD,
  solution architecture document, component IDs, COMP-IDs, sequence diagrams, deployment
  view, DR strategy, scalability model, ADR-005, ADR-006, ADR-007, ADR-008, or a master
  technical reference. Always trigger when an RTM JSON is present and prior artefacts
  (HLD, tier map, milestone plan, or TC registry) are also in the Cowork folder.
---

# Solution Architecture Document (SAD) Skill

Reads all artefacts from the Cowork folder and produces the master technical reference:
1. **Component Registry** — every deployable/logical component with a permanent COMP-ID
2. **Component Diagram** — text-art showing inter-component relationships
3. **Six Sequence Diagrams** — key flows in ASCII UML notation
4. **Deployment View** — environment topology and networking
5. **ADR-005 through ADR-008** — four SAD-level decisions
6. **Scalability Model** — per-component scaling strategy and triggers
7. **DR Strategy** — RTO/RPO targets, backup cadence, failover runbook seeds
8. **Enriched RTM JSON** — `sad_component` and `adr_ids` on every requirement

All in a single `.md` output file.

---

## 0. Prerequisites

No additional libraries. Output is Markdown + JSON via standard Python.

---

## 1. Inputs

### 1.1  Primary source — Cowork folder

```bash
ls -lh /mnt/user-data/uploads/
```

Read all files present:

| File | Role |
|------|------|
| `*.json` (RTM) | **Required** — requirements, stories, categories |
| `*HLD*.md` | ATAM decisions, component overview, ADR-001–004 |
| `*tier-map*.md` | TIER-IDs, tier→requirement mapping |
| `*milestone*.md` | MS-IDs, entry/exit criteria |
| `*tc-registry*.md` | TC-IDs for cross-reference |

If only the RTM is present, derive everything from it directly.

### 1.2  What to extract

```
PROJECT_NAME, VERSION           — from RTM project metadata
ALL_REQUIREMENTS                — id, title, category, moscow, status, feat_id
TIER_REGISTRY                   — TIER-001 through TIER-NNN from tier map (if present)
EXISTING_ADRS                   — ADR-001–004 titles from HLD (to avoid duplication)
MILESTONE_IDS                   — from milestone plan (for cross-reference)
TC_IDS                          — from TC registry (for cross-reference)
```

---

## 2. COMP-ID System

### 2.1  Permanent ID format

```
COMP-NNN   where NNN is zero-padded integer from 001
```

IDs are **permanent** — never reassigned, never reused. Append for new components.

### 2.2  COMP-ID assignment rules

One COMP-ID per **independently named, deployable or logical component**. A component is
finer-grained than a TIER-ID — a single tier may contain multiple components.

**Component taxonomy:**

| Category | Examples |
|----------|---------|
| Client components | SPA bundle, widget module, snippet panel |
| Delivery components | CDN edge, load balancer |
| Backend service components | API gateway service, auth module, AI gateway service |
| Backend module components | Subscription module, widget engine module, analytics ingest module |
| Data components | Primary DB, read replica, event store, cache |
| Infrastructure components | CI/CD pipeline, secrets manager, observability stack |
| Integration components | Stripe integration, SSO federation service |
| Operational components | Purge job, scheduled materialisation job |

### 2.3  Standard component set (derive from project)

Check the HLD Component Overview and Tier Map for project-specific components.
Standard STEMWidgets components (COMP-001 through COMP-023) are defined in this skill's
reference section below.

---

## 3. Output: Component Registry

```markdown
## Component Registry

| COMP-ID | Component Name | TIER-ID | Category | Description | Technology |
|---------|---------------|---------|---------|-------------|-----------|
| COMP-001 | React SPA Bundle | TIER-001 | Client | ... | React / Next.js static |
...
```

Every component gets: COMP-ID, name, owning TIER-ID, category, one-sentence description,
and primary technology.

---

## 4. Output: Component Diagram

Text-art showing all components and their primary interactions.
Use box-and-arrow notation. Group by deployment boundary (browser, CDN, app cluster, data tier, external).

```
Browser
  [COMP-001: React SPA]
    ├── [COMP-002: Widget Module]
    └── [COMP-003: Snippet Panel]
         │ HTTPS
         ▼
[COMP-004: CDN Edge] ──▶ (static assets to browser)
         │ HTTPS (API calls)
         ▼
[COMP-005: Load Balancer]
    │
    ├──▶ [COMP-006: API Gateway] ──▶ [COMP-007: Auth Module]
    │         ├──▶ [COMP-008: Subscription Module] ──▶ [COMP-019: Stripe Integration]
    │         ├──▶ [COMP-009: Widget Engine Module]
    │         ├──▶ [COMP-010: Analytics Ingest] ──▶ [COMP-015: Event Store]
    │         └──▶ [COMP-013: PostgreSQL Primary]
    │
    └──▶ [COMP-011: AI Gateway] ──▶ [COMP-012: LLM Adapter] ──▶ LLM API (external)

Data Tier
  [COMP-013: PostgreSQL Primary] ──replica──▶ [COMP-014: Read Replica]
  [COMP-015: Event Store]
  [COMP-016: Redis Cache]

Infrastructure (wraps all)
  [COMP-021: CI/CD] [COMP-022: Secrets Manager] [COMP-023: Observability Stack]

Operational
  [COMP-018: Purge Job] ──▶ [COMP-013] (erasure)

External SaaS
  Stripe ◀──▶ [COMP-019]
  LLM API ◀── [COMP-012]
  Institution IdP ◀──▶ [COMP-020: SSO Federation]
  Google Colab ◀── [COMP-003] (URL redirect only)
```

---

## 5. Output: Sequence Diagrams

Write six sequence diagrams in ASCII UML. Format:

```
Participant A    Participant B    Participant C
     │                │                │
     │──[action]─────▶│                │
     │                │──[action]─────▶│
     │                │◀──[response]───│
     │◀──[response]───│                │
```

### Required sequences:

1. **SEQ-001** — User Registration (email/password)
   Participants: Browser, CDN, API Gateway, Auth Module, PostgreSQL

2. **SEQ-002** — Widget Load & Client-Side Interaction
   Participants: Browser, CDN, API Gateway, Widget Engine Module, PostgreSQL
   (shows zero server round-trip during interaction — key architectural property)

3. **SEQ-003** — AI Advisor Query (paid tier, SSE streaming)
   Participants: Browser, API Gateway, Auth Module, AI Gateway, LLM Adapter, LLM API

4. **SEQ-004** — Subscription Purchase (Stripe flow)
   Participants: Browser, API Gateway, Subscription Module, Stripe Integration, Stripe API, PostgreSQL

5. **SEQ-005** — AI Gateway Circuit Breaker (fallback flow)
   Participants: Browser, API Gateway, AI Gateway, (LLM API — unavailable)
   (shows graceful degradation per REQ-NF-008)

6. **SEQ-006** — Account Deletion + 30-day PII Purge
   Participants: Browser, API Gateway, Auth Module, PostgreSQL, Purge Job
   (two-phase: immediate soft-delete + scheduled hard purge)

---

## 6. Output: Deployment View

### 6.1  Environment topology

Three environments: `local`, `staging`, `production`.
For each, describe:
- What is deployed
- Networking and access controls
- Data tier (real vs. mocked)
- External integrations (live vs. sandbox)

### 6.2  Production networking diagram

```
Internet
    │
[WAF / DDoS protection]
    │
[CDN Edge — COMP-004]  ──▶  [Static assets: SPA, widgets, snippets]
    │ (dynamic requests only)
[Load Balancer — COMP-005]  (HTTPS termination, health checks)
    │               │
[API Gateway     [AI Gateway
 Pod(s)           Pod]
 COMP-006]        COMP-011
    │                  │
[Shared Data Tier]   [LLM API - external]
  COMP-013 (Primary)
  COMP-014 (Replica)
  COMP-015 (Event Store)
  COMP-016 (Redis)

[Operational]
  COMP-018 Purge Job (cron)
  COMP-023 Observability (exporter sidecars)

[External]
  Stripe API
  Institution IdPs
  Google OAuth
```

### 6.3  Multi-AZ strategy

Describe how the production environment spans availability zones for REQ-NF-004 (99.5% uptime).

---

## 7. Output: ADR-005 through ADR-008

Use the same ADR template as ADR-001–004 (from HLD):

```markdown
### ADR-NNN: [Title]

**Date:** YYYY-MM-DD
**Status:** Accepted | Proposed
**Deciders:** [roles]
**Supersedes:** —

#### Context
[what is the decision, what forces apply, which REQ-IDs drive it]

#### Decision
[the decision, stated clearly in one paragraph]

#### Consequences
**Positive:** bullet list
**Negative / Risks:** bullet list
**Mitigation:** bullet list

#### Alternatives Considered
| Alternative | Reason Rejected |
|------------|----------------|
```

**Four required ADRs:**

- **ADR-005: API Protocol & Communication Patterns**
  Context: REST vs GraphQL vs tRPC for server API; SSE vs WebSocket for AI streaming.
  Must address: REQ-NF-002 (100ms widget), REQ-NF-003 (5s AI streaming), REQ-NF-008 (fallback).

- **ADR-006: Authentication Token Strategy**
  Context: Where to store JWT (memory vs localStorage vs httpOnly cookie);
  silent refresh mechanism; SSO token binding.
  Must address: REQ-F-001, REQ-F-002, REQ-C-002 (GDPR), REQ-C-003 (COPPA).

- **ADR-007: Observability Stack**
  Context: Structured logging, distributed tracing, metrics, alerting.
  Must address: REQ-NF-004 (uptime monitoring), REQ-D-003 (no AI content in logs), REQ-NF-008.

- **ADR-008: Disaster Recovery & Backup Strategy**
  Context: RTO/RPO targets, DB backup cadence, multi-AZ failover, AI Gateway recovery.
  Must address: REQ-NF-004 (99.5% uptime), REQ-D-004 (data retention), REQ-D-001 (user profile integrity).

---

## 8. Output: Scalability Model

Table per component with current capacity, scale trigger, and scale mechanism:

```markdown
## Scalability Model

| COMP-ID | Component | Current Capacity (v1) | Scale Trigger | Scale Mechanism | Scale Limit |
|---------|----------|----------------------|--------------|-----------------|------------|
| COMP-004 | CDN Edge | Effectively unlimited (CDN) | — | CDN auto-scales | — |
| COMP-006 | API Gateway | 2 pods × 512MB | p95 latency > 200ms OR CPU > 70% | Add pod (horizontal) | DB connection pool |
...
```

Populate for all COMP-IDs. Include the MS-04 load test target (10,000 concurrent — REQ-NF-009)
as a calibration point.

---

## 9. Output: DR Strategy

### 9.1  RTO / RPO targets

| Tier | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|------|------------------------------|-------------------------------|
| Transactional DB (COMP-013) | 15 minutes | 5 minutes (WAL streaming) |
| Event Store (COMP-015) | 30 minutes | 1 hour (daily snapshot) |
| Static Assets (COMP-004) | Near-zero (CDN multi-region) | N/A (rebuilt from CI/CD) |
| AI Gateway (COMP-011) | 5 minutes (pod restart) | N/A (stateless) |
| Redis (COMP-016) | 10 minutes (cold restart) | N/A (rate limits are transient) |

### 9.2  Backup cadence

| Data Store | Backup Type | Frequency | Retention | Location |
|-----------|-------------|-----------|-----------|---------|
| PostgreSQL Primary | WAL archiving | Continuous | 7 days | Cross-region object store |
| PostgreSQL Primary | Full snapshot | Daily | 30 days | Cross-region object store |
| Event Store | Snapshot | Daily | 90 days | Same region object store |

### 9.3  Failover runbook seeds

Write brief runbook seeds for:
- DB primary failure (promote read replica)
- AI Gateway pod crash (circuit breaker auto-triggers; manual pod restart)
- CDN outage (fallback to origin serving)
- Stripe webhook backlog (replay from Stripe dashboard)

---

## 10. Output: Enriched RTM JSON

Add two fields to every requirement:

```json
{
  "id": "REQ-F-001",
  "sad_component": "COMP-007",       ← primary COMP-ID that implements this requirement
  "adr_ids": ["ADR-001", "ADR-006"], ← all ADRs (001-008) that govern this requirement
  ...original fields preserved...
}
```

Rules:
- `sad_component` = the single COMP-ID most directly responsible for implementing the requirement
- `adr_ids` = array of all ADR-IDs (from both the HLD and this SAD) that apply
- Preserve all original fields

---

## 11. Output File

One file to `/mnt/user-data/outputs/`:

```
[project-slug]-SAD-v[version].md
```

Structure:
```
# [Project] — Solution Architecture Document
## 1. Component Registry
---
## 2. Component Diagram
---
## 3. Sequence Diagrams (SEQ-001 through SEQ-006)
---
## 4. Deployment View
---
## 5. ADR-005 through ADR-008
---
## 6. Scalability Model
---
## 7. DR Strategy
---
## 8. Enriched RTM (sad_component + adr_ids populated)
```json
{ enriched RTM JSON }
```
```

Call `present_files` with the single path.

---

## 12. Quality Checklist

- [ ] All 23 COMP-IDs (or project-specific count) have registry entries
- [ ] Every COMP-ID maps to a TIER-ID
- [ ] All 6 sequence diagrams present with correct participants
- [ ] SEQ-002 explicitly shows zero server round-trips during widget interaction
- [ ] SEQ-005 shows circuit breaker open and graceful degradation
- [ ] Deployment view covers all three environments
- [ ] ADR-005 through ADR-008 all present with context, decision, consequences, alternatives
- [ ] ADR-005 explicitly addresses SSE for AI streaming (REQ-NF-003)
- [ ] ADR-006 explicitly addresses JWT storage and REQ-C-002 / REQ-C-003
- [ ] ADR-007 explicitly states no AI content in log lines (REQ-D-003)
- [ ] ADR-008 specifies RTO/RPO numbers tied to REQ-NF-004
- [ ] Scalability model covers every COMP-ID
- [ ] DR strategy includes RTO/RPO table and backup cadence
- [ ] Every requirement in enriched JSON has `sad_component` and `adr_ids`
- [ ] Output is a single `.md` file