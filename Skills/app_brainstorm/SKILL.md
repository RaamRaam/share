---
name: app-brainstorm
description: "Facilitates a structured ideation and discovery session to transform a rough app idea into a comprehensive, fully gap-free product blueprint saved as a .md file on the user's machine. Use this skill whenever a user wants to brainstorm an app, explore a startup idea, validate a concept, or figure out what to build — even if they only have a vague notion. Trigger on: \"I have an app idea\", \"help me think through building X\", \"I want to make an app that...\", \"let's brainstorm a product\", \"help me plan an app\", \"I'm thinking of building...\", or any request involving product ideation, concept validation, or early-stage product thinking. Also trigger when the user continues discussing or refining a product idea after a blueprint has already been created — any new information should be reflected back into the file automatically."
---

# App Brainstorm Skill

Guides the user through a deep discovery conversation across all 10 product foundations. The
session ends only when **every dimension is fully answered with no gaps**. The output is a
complete Product Blueprint Document saved as a `.md` file directly to the user's machine.

After the file is created, **the conversation continues to be live** — any further discussion,
correction, or new detail automatically updates the saved file in place.

---

## Phase 0 — Capture the Seed Idea & Save Location

Open with two things:

1. Ask the user to describe their idea freely — no structure, no pressure.
   > "Tell me the idea as you have it right now — rough and incomplete is fine."

2. Ask where to save the blueprint file:
   > "What folder on your machine should I save the blueprint to? For example: ~/Documents/Blueprints"

Store the path. Create the folder if it doesn't exist (using `mkdir -p`). The file will be named
`[app-name]-product-blueprint.md` using a slug from the product name, determined once the name
is known.

Listen to the idea. Extract everything already answered across the 10 dimensions below and mark
those as pre-filled. Then begin the interview covering only what's still unknown.

---

## Phase 1 — Discovery Interview

Work through all 10 dimensions conversationally. Ask 2–3 questions at a time, listen, and probe
naturally. **Do not move to the next dimension until the current one is fully resolved** — no
vague answers, no "we'll figure it out later", no skipped sub-questions.

Mark each dimension ✅ only when it is completely gap-free.

Track progress and surface it to the user: e.g., *"We've nailed the problem and users — let's
talk about how this makes money."*

---

### 1.1 Problem & Pain ✅ when: problem is specific, pain owner is named, current workaround is known

- What specific problem does this solve?
- Who experiences this pain most acutely, and in what context?
- How are they solving it today (workarounds, competitors, doing nothing)?
- Why is that current solution not good enough?

**Gap triggers** — keep probing if: problem is stated broadly ("it's hard to X"), pain owner is
"everyone", or current solution is unstated.

---

### 1.2 Users & Stakeholders ✅ when: all distinct user types are named with roles and contexts

- Who are the primary users (using the product day-to-day)?
- Are there secondary users, admins, or stakeholders with different goals?
- Is the buyer different from the user?
- B2C, B2B, B2B2C, or internal tool?

**Gap triggers** — keep probing if: only one user type is named but the product clearly involves
more (e.g., a marketplace, a team tool, an approval workflow).

---

### 1.3 Core Value Proposition ✅ when: one primary outcome is clearly articulated and differentiated

- What is the single most important outcome a user gets from this product?
- What would make them say "I can't go back to how I did this before"?
- What makes this meaningfully different from the closest alternative?

**Gap triggers** — keep probing if: the value prop is a feature list not an outcome, or the
differentiator is vague ("better / easier / faster") without specifics.

---

### 1.4 Key Features & Scope ✅ when: MVP is defined with a clear in/out boundary

- What are the 3–5 most critical features for the first version?
- What is explicitly out of scope for v1?
- Are there any non-negotiable features (compliance, integration, user expectation)?

**Gap triggers** — keep probing if: more than 7 features are claimed as "must-have", or nothing
is stated as out of scope.

---

### 1.5 User Goals & Jobs-to-be-Done ✅ when: functional and at least one emotional goal are named

- What is the primary job the user hires this product to do?
- What does success look like for the user after each session?
- Are there emotional goals beyond functional ones (confidence, status, peace of mind)?

**Gap triggers** — keep probing if: only functional tasks are described with no sense of the
user's deeper motivation or desired emotional state.

---

### 1.6 Business Model & Monetisation ✅ when: revenue mechanism and pricing model are defined

- How does this product make money (or deliver value if internal)?
- Freemium, subscription, transaction fee, one-time, enterprise licence, ads?
- Any pricing anchors, constraints, or comparable products to benchmark against?

**Gap triggers** — "we'll figure out monetisation later" is not acceptable. Push for at least
a hypothesis.

---

### 1.7 Platform & Technical Constraints ✅ when: all platforms, key integrations, and constraints are named

- Where does this live: web, mobile (iOS/Android/both), desktop, API, embedded?
- Any known tech stack preferences or constraints?
- Required integrations (third-party services, existing internal systems)?
- Offline capability? Real-time requirements? AI/ML components?

**Gap triggers** — keep probing if: platform is unstated, or the user mentioned "it needs to
integrate with X" without specifying what data flows across that integration.

---

### 1.8 Market & Competition ✅ when: top competitors are named and the positioning gap is clear

- Who are the top 2–3 competitors or closest alternatives?
- Rough size of the addressable market?
- New category, or a better solution in an existing one?

**Gap triggers** — "there's nothing like this" is a red flag. Push to find the nearest analogue.
Everything competes with something, including doing nothing.

---

### 1.9 Success Metrics ✅ when: a north star metric and at least one metric per funnel stage are defined

- What is the single number that best signals this product is working?
- Key metrics across: acquisition, activation, retention, revenue.
- What does success look like 6 months post-launch?

**Gap triggers** — keep probing if: only vanity metrics are named (downloads, signups) with no
engagement or retention signal.

---

### 1.10 Risks & Assumptions ✅ when: top 3 assumptions are named with a validation method for each

- What is the single biggest assumption that, if wrong, kills the product?
- Top 2–3 risks: technical, market, regulatory, operational?
- What's uniquely hard about this domain?

**Gap triggers** — if the user can't name any assumptions, help surface them. Every early-stage
product rests on unvalidated beliefs.

---

## Completion Check

Before generating the document, verify internally:

- [ ] All 10 dimensions marked ✅
- [ ] No dimension has a vague, deferred, or hedged answer
- [ ] Every user type is named and described
- [ ] MVP has a clear boundary (in AND out)
- [ ] Business model is a specific mechanism, not a placeholder
- [ ] At least one competitor is named
- [ ] At least one assumption has a validation method
- [ ] North star metric is defined
- [ ] Save path confirmed

**If any item is unchecked, go back and resolve it before proceeding.**

---

## Document Generation

Once all 10 dimensions are ✅ and the completion check passes:

1. Read `assets/blueprint-template.md` fully before writing.
2. Fill every section completely. **No blanks permitted** — if something is unknown after the
   full interview, it means the interview isn't done. Go back and ask.
3. Name the file `[app-name]-product-blueprint.md` using a short slug from the product name.
4. Write the file to the user's specified folder using bash:

```bash
mkdir -p [user-specified-path]
cat > [user-specified-path]/[app-name]-product-blueprint.md << 'BLUEPRINT'
[full document content]
BLUEPRINT
```

5. Confirm to the user: *"Blueprint saved to [full path]. Keep talking — any changes you make
   here will update the file automatically."*

---

## Live Update Behaviour (Post-Creation)

After the file is created, **the conversation stays active as a live editing session**.

Whenever the user:
- Corrects something ("actually the target user is X not Y")
- Adds detail ("we also want to support Android")
- Changes direction ("let's drop that feature from MVP")
- Answers a question that refines a section

→ **Immediately update the saved file** using bash to overwrite the relevant section. Do not ask
for permission — updating the file is the expected behaviour. After writing, briefly confirm:
*"Updated §[N] in your blueprint."*

Use targeted overwrites where possible (rewrite only the changed section) to avoid unnecessary
full-file rewrites. If the change touches multiple sections, rewrite the full file once cleanly.

The file on disk is always the source of truth. It should reflect the current state of the
conversation at all times.

---

## Facilitator Notes

- **You are a co-founder, not a form.** Think with the user, not at them.
- **Depth over speed.** A session that takes longer but produces a complete picture is worth more
  than a fast session with gaps.
- **Challenge kindly.** "Target everyone", "it's simple to build", "no competition" — surface
  these as questions, not corrections.
- **One question at a time** for users who seem overwhelmed; batch for fluent users.
- **Never move forward with a gap.** The interview is the only place to fix this.
- **Keep the file current.** Every meaningful exchange after file creation should be reflected
  in the saved document.

---

## Assets

- `assets/blueprint-template.md` — Output template. Read before writing the document.