---
name: tech-stack
description: >
  Interactive full-technology-stack selection skill. Reads the RTM JSON, Tier Map, and SAD
  from the Cowork folder, collects all confirmed and TBC technology choices, presents
  structured trade-off tables for every undecided choice, and produces: (1) a locked
  Stack Lock JSON with every tier's final technology choice, (2) a test-runners map per
  tier with tool, command, and CI integration, and (3) a CI/CD tool confirmed with pipeline
  stages. All in a single .md output file with the JSON embedded. Trigger this skill
  whenever the user asks for a tech stack, technology choices, stack lock, stack decisions,
  test runners, CI/CD tool, tooling map, framework selection, library selection, or wants
  to finalise or review technology choices across tiers. Always trigger when a SAD or Tier
  Map is present in the Cowork folder and the user mentions technology or tooling.
---

# Tech Stack Skill

Reads prior artefacts from the Cowork folder, surfaces every unresolved technology choice as
a structured trade-off, and produces the locked stack + test runner map + CI/CD confirmation
in a single `.md` output file.

---

## 0. Prerequisites

No additional libraries required. Output is Markdown + JSON written with standard Python.

---

## 1. Inputs

### 1.1  Cowork folder

```bash
ls -lh /mnt/user-data/uploads/
```

Read all files present — priority order:

| File | Role |
|------|------|
| `*SAD*.md` | **Primary.** COMP-IDs, ADR log, confirmed + TBC technology mentions |
| `*tier-map*.md` | TIER-IDs, tier responsibilities, technology stack sections |
| `*.json` (RTM) | Requirements; category, status, milestone_id |
| `*milestone*.md` | MS-IDs for CI/CD stage mapping |
| `*tc-registry*.md` | TC-IDs and types (U/I/E/C/P/S) for test runner mapping |

### 1.2  What to extract

Scan every technology mention across all input files. Classify each as:

```
CONFIRMED   — mentioned as a definite choice (no "TBC", "OR", "TBD")
TBC         — marked with "TBC", "OR", "(OI-NNN)", "to be confirmed", "pending"
ASSUMED     — derived from RTM assumption flag (A-NNN)
```

Build two lists before generating output:
- `confirmed_stack`: technology decisions already locked in prior artefacts
- `open_decisions`: undecided choices needing trade-off presentation and selection

---

## 2. Open Decision Categories

For each open decision, present a trade-off card using this format:

```markdown
### STACK-NNN — [Decision Name]

**Context:** [why this choice matters; which TIER-IDs / COMP-IDs / REQ-IDs are affected]
**Constraint:** [any hard requirement that narrows the options]

| Option | Pros | Cons | Cost Signal | Best Fit When |
|--------|------|------|-------------|--------------|
| Option A | ... | ... | $ | ... |
| Option B | ... | ... | $$ | ... |

**Recommendation:** [recommended option with one-sentence rationale]
**Lock:** [the selected value — filled in after user confirms or skill applies recommendation]
```

### Standard open decision set for a web platform with these characteristics:

1. **STACK-001 — Cloud Provider** (AWS vs GCP)
2. **STACK-002 — Container Orchestration** (ECS vs Kubernetes / GKE)
3. **STACK-003 — Auth Provider** (Auth0 vs AWS Cognito vs self-hosted)
4. **STACK-004 — LLM Provider** (Anthropic Claude API vs OpenAI API)
5. **STACK-005 — CI/CD Tool** (GitHub Actions vs GitLab CI vs CircleCI)
6. **STACK-006 — Observability Backend** (Datadog vs Grafana+Prometheus+Loki)
7. **STACK-007 — Secrets Management** (AWS Secrets Manager vs HashiCorp Vault)
8. **STACK-008 — Frontend Test Runner** (Jest vs Vitest)
9. **STACK-009 — Analytics Scale Path** (stay on PostgreSQL vs migrate to ClickHouse)

Add or remove cards based on what is TBC in the specific project's artefacts.

---

## 3. Output: Stack Lock JSON

The locked stack is the canonical source of truth for all technology choices.

```json
{
  "project": "...",
  "version": "...",
  "stack_lock_version": "1.0",
  "stack_lock_date": "YYYY-MM-DD",
  "status": "LOCKED",
  "tiers": {
    "TIER-001": {
      "name": "Client Layer",
      "framework": "React 18 + Next.js 14 (static export)",
      "language": "TypeScript",
      "styling": "CSS Modules + Tailwind utility classes",
      "bundler": "Next.js (Webpack/Turbopack)",
      "deployment": "Cloudflare Pages / Vercel",
      "key_libraries": ["react-router-dom (if CRA)", "next/router (if Next.js)", "prism-react-renderer"]
    },
    "TIER-002": {
      "name": "Widget & Interaction Layer",
      "runtime": "Browser (client-side JS)",
      "language": "TypeScript",
      "key_libraries": ["React 18 component per widget", "d3.js or recharts for visualisation"],
      "lazy_loading": "next/dynamic or React.lazy"
    },
    ... (one object per TIER-ID)
  },
  "infrastructure": {
    "cloud": "AWS | GCP",
    "region_primary": "...",
    "region_dr": "...",
    "container_orchestration": "ECS Fargate | GKE Autopilot | Kubernetes",
    "load_balancer": "AWS ALB | GCP Cloud LB",
    "cdn": "Cloudflare | CloudFront",
    "secrets": "AWS Secrets Manager | HashiCorp Vault"
  },
  "integrations": {
    "auth_provider": "Auth0 | AWS Cognito",
    "llm_provider": "Anthropic Claude API | OpenAI API",
    "payment_provider": "Stripe",
    "sso_protocols": ["SAML 2.0", "OIDC"]
  },
  "observability": {
    "instrumentation": "OpenTelemetry SDK",
    "backend": "Datadog | Grafana + Prometheus + Loki",
    "uptime_monitoring": "BetterUptime | Datadog Synthetics"
  },
  "open_decisions_resolved": {
    "STACK-001": "...",
    "STACK-002": "...",
    ...
  }
}
```

---

## 4. Output: Test Runners Map Per Tier

One row per tier, one row per test type relevant to that tier.

```markdown
## Test Runners Map

| TIER-ID | Tier Name | TC Types | Test Runner | Run Command | CI Stage | Config File |
|---------|-----------|---------|------------|-------------|---------|------------|
| TIER-001 | Client Layer | E (Playwright), S (axe-core), P (Lighthouse CI) | Playwright; axe-core (via Playwright plugin); Lighthouse CI | `npx playwright test`, `npx lhci autorun` | `test:e2e`, `test:a11y`, `test:perf` | `playwright.config.ts`, `lighthouserc.js` |
...
```

Include for every tier:
- All TC types from the TC registry that touch that tier
- The specific tool for each type
- The npm/yarn/python command to run locally
- The CI stage name
- The config file name

---

## 5. Output: CI/CD Pipeline Definition

The CI/CD confirmation documents the full pipeline with stages, triggers, and tool.

```markdown
## CI/CD Pipeline

**Tool:** [GitHub Actions | GitLab CI]
**Config file:** `.github/workflows/ci.yml` | `.gitlab-ci.yml`
**Repository strategy:** Monorepo (API + AI Gateway + Frontend in one repo, separate deploy targets)

### Pipeline Stages

| Stage | Name | Trigger | Jobs | Fail Behaviour |
|-------|------|---------|------|---------------|
| 1 | Lint & Type Check | Every push | ESLint, TypeScript tsc, Python mypy | Block merge |
| 2 | Unit Tests | Every push | Jest/Vitest (frontend), Jest (API modules) | Block merge |
| 3 | Schema Lint | Every push | Analytics schema no-eval field check; Zod schema validation | Block merge |
| 4 | Integration Tests | Every push to main/dev | Supertest (API); testcontainers (DB); Stripe test mode | Block merge |
| 5 | E2E Tests | Every push to main/dev | Playwright (core flows on Chrome) | Block merge |
| 6 | Accessibility Gate | Every push to main/dev | axe-core via Playwright — zero critical violations | Block merge |
| 7 | Performance Gate | Every push to main/dev | Lighthouse CI — score ≥ 80, TTI < 3s | Block merge |
| 8 | Security Scan | Every push to main | npm audit, Snyk or similar | Warn on new high; block on critical |
| 9 | Build & Push | On merge to main | Docker build; push to container registry | Block deploy |
| 10 | Deploy to Staging | On merge to main | Deploy API + AI Gateway pods; invalidate CDN cache | Block prod deploy |
| 11 | Staging Smoke Tests | After staging deploy | 5-minute Playwright smoke suite; AI Gateway health check | Block prod deploy |
| 12 | Deploy to Production | Manual approval gate | Rolling deploy to production pods; CDN invalidation | Rollback on health check failure |
```

### Environment-specific job matrix

```markdown
| Job | Local | Staging | Production |
|-----|-------|---------|-----------|
| Unit tests | ✓ (always) | ✓ | — |
| Integration tests | ✓ (testcontainers) | ✓ (real DBs) | — |
| E2E | ✓ (headed browser) | ✓ (headless) | — |
| Load test | Manual | ✓ (k6) | — |
| Smoke test | — | ✓ | ✓ (post-deploy) |
| Lighthouse CI | ✓ | ✓ | — |
```

---

## 6. Output File

One file to `/mnt/user-data/outputs/`:

```
[project-slug]-stack-lock-v[version].md
```

Structure:

```
# [Project] — Technology Stack Lock

## 1. Confirmed Stack (from prior artefacts)   ← table of already-locked choices
---
## 2. Open Decisions & Trade-offs              ← STACK-001 through STACK-NNN cards
---
## 3. Stack Lock JSON                          ← fenced JSON block
---
## 4. Test Runners Map Per Tier               ← table per TIER-ID
---
## 5. CI/CD Pipeline                          ← pipeline stages table
---
## 6. Package Manifest Seeds                  ← package.json / requirements.txt seeds
```

Call `present_files` with the single path.

---

## 7. Package Manifest Seeds

Include starter package manifest seeds for each repo in the monorepo:

### `apps/frontend/package.json` (TIER-001, TIER-002, TIER-003)
```json
{
  "dependencies": {
    "next": "^14.x", "react": "^18.x", "react-dom": "^18.x",
    "prism-react-renderer": "^2.x"
  },
  "devDependencies": {
    "typescript": "^5.x", "jest": "^29.x | vitest": "^1.x",
    "@playwright/test": "^1.x", "axe-playwright": "^2.x",
    "@lhci/cli": "^0.13.x", "eslint": "^8.x"
  }
}
```

### `apps/api/package.json` (TIER-005, TIER-006, TIER-007, TIER-009, TIER-010, TIER-011)
```json
{
  "dependencies": {
    "fastify": "^4.x", "stripe": "^14.x",
    "@opentelemetry/sdk-node": "^1.x",
    "pg": "^8.x", "ioredis": "^5.x", "zod": "^3.x"
  },
  "devDependencies": {
    "typescript": "^5.x", "jest": "^29.x", "supertest": "^6.x",
    "@testcontainers/postgresql": "^10.x"
  }
}
```

### `apps/ai-gateway/package.json` (TIER-008, TIER-011)
```json
{
  "dependencies": {
    "fastify": "^4.x", "opossum": "^8.x",
    "@anthropic-ai/sdk": "^0.x | openai": "^4.x",
    "@opentelemetry/sdk-node": "^1.x", "zod": "^3.x"
  },
  "devDependencies": {
    "typescript": "^5.x", "jest": "^29.x", "supertest": "^6.x"
  }
}
```

---

## 8. Quality Checklist

- [ ] Every TIER-ID from the tier map has an entry in the Stack Lock JSON
- [ ] Every TBC decision from the SAD has a trade-off card (STACK-NNN)
- [ ] Every trade-off card has a Recommendation and Lock value
- [ ] Test runner map covers all TIER-IDs; TC types match the TC registry
- [ ] CI/CD tool is confirmed (not "GitHub Actions OR GitLab CI")
- [ ] CI pipeline has stages covering: lint, unit, schema-lint, integration, E2E, a11y, perf, security, build, staging deploy, smoke, prod deploy
- [ ] Package manifest seeds include all dependencies mentioned in the confirmed stack
- [ ] Stack Lock JSON is valid JSON (no trailing commas, properly quoted keys)
- [ ] Output is a single `.md` file