# Journey Stages

## Core principle — derive stages from the requirements, not from a fixed list

Do not apply a standard stage template to every product. Instead:

1. Take all requirements that belong to this user type
2. Order them by when they occur in the user's lifecycle
3. Group into natural phases — each group is a stage
4. Name the stage from its lifecycle position

The result will be different for every product and every user type. A single-player game
has different stages from an enterprise SaaS admin. A freemium B2C app has different stages
from an API-first developer tool.

---

## Lifecycle positions to draw from

These are the positions a user can occupy in any product lifecycle. Not all apply to every
user type. Use them as prompts when grouping requirements — not as a checklist to fill.

### Before the product

| Position | What it covers |
|---|---|
| Awareness | First time the user hears about or discovers the product |
| Consideration | The user evaluates whether the product fits their need |
| Evaluation / Trial | Hands-on assessment; demo, pilot, or free tier |

### Getting started

| Position | What it covers |
|---|---|
| Onboarding | Account creation, first login, initial setup |
| Provisioning | Setting up access for others (admin / institutional role) |
| First value | The first moment the product delivers its core promise |

### Regular use

| Position | What it covers |
|---|---|
| Habitual loop | The repeated usage pattern that constitutes normal engagement |
| Power / deep use | Advanced features, integrations, or high-frequency usage |
| Expansion | Upgrading tier, adding seats, broadening scope of use |

### Friction and recovery

| Position | What it covers |
|---|---|
| Friction point | A requirement that can fail or a decision that is still unresolved |
| Support | The user encounters a problem and needs resolution |
| Workaround | The user finds a way around a missing feature |

### Ongoing operations (admin / ops roles)

| Position | What it covers |
|---|---|
| Monitoring | Regular review of dashboards, metrics, or system health |
| Compliance / audit | Periodic verification of policy, data, or security requirements |
| Reporting | Producing summaries for stakeholders or leadership |

### End of cycle

| Position | What it covers |
|---|---|
| Renewal / continuation | Decision to continue paying or using the product |
| Advocacy | Recommending the product to others |
| Exit / churn | Decision to stop using or cancel |

---

## How to map requirements to stages

For each requirement in this user's pool, ask:
*"When in the user's lifecycle does this requirement become active?"*

Then assign the requirement to the closest lifecycle position.
If a requirement spans multiple positions (e.g. a performance NFR that matters everywhere),
assign it to the position where its absence would cause the most noticeable harm.

Requirements that operate entirely below the user-visible layer (data retention policies,
infrastructure constraints, security hashing) go in the Req-ID Index under "not referenced
in any journey" — they do not need a journey row.

---

## Stage naming

Name stages clearly and concisely. Prefer the user's perspective over the product's:

| Avoid | Prefer |
|---|---|
| "Widget Interaction" | "First exploration" |
| "Stripe Checkout" | "Subscription purchase" |
| "SAML Configuration" | "SSO setup" |
| "Analytics Dashboard View" | "Usage monitoring" |

The stage name should describe what the **user** is doing, not which product feature is active.

---

## Emotion vocabulary

Use exactly one word and one emoji per journey row. Choose the emotion that best fits the
user's state given what the requirements say — not what feels generically right.

| Emotion | Emoji | When to use |
|---|---|---|
| Curious | 🔍 | Exploring, discovering, trying something for the first time |
| Excited | 🎉 | Achieving a goal, completing setup, unlocking access |
| Confused | 😕 | Unclear flow, missing guidance, ambiguous outcome |
| Anxious | 😰 | High stakes, unresolved compliance, waiting on something critical |
| Satisfied | ✅ | Task completed as expected, value delivered |
| Frustrated | 😤 | Something failed, a workaround is needed, blocked |
| Confident | 💪 | Repeating a known workflow, operating with expertise |
| Delighted | 🌟 | Unexpected positive outcome, exceeded expectation |
| Neutral | 😐 | Routine task, no strong feeling either way |
| Relieved | 😮‍💨 | A risk was resolved, a concern was addressed |
| Impatient | ⏳ | Waiting, slow response, too many steps |
| Sceptical | 🤨 | Evaluating, unconvinced, needs proof |

---

## Notes column rules

The Notes column in a journey table should contain exactly one of:

| Type | Format | When to use |
|---|---|---|
| AC snippet | `"≤10 words from acceptance_criteria"` | The AC directly describes success at this stage |
| Assumption flag | `[ASSUMED: brief topic]` | The stage depends on an ASSUMED or DRAFT requirement |
| Open item | `OI: brief topic` | An unresolved decision in the source data affects this stage |
| Cross-reference | `See {req-ID}` | Another requirement governs this stage more precisely |
| Empty | `—` | Nothing relevant to add |

Never leave the Notes column blank. Use `—` explicitly.

---

## Req-ID index rules

After all journey maps, append one index table covering every req-ID referenced across
all journey maps.

For each ID:
- Title, category, status: copy exactly from the JSON
- Referenced by: list the role labels (not fictional names) of every user type whose
  journey table contains this ID

After the table, list any IDs from the JSON that appear in **no** journey row, with a
one-line reason (e.g. "infrastructure constraint below journey layer", "compliance policy
not user-visible", "vendor-side requirement").

This index is the primary traceability link from UX artefacts back to the requirements.