# RTM JSON Schema

The RTM seed file is a JSON object with two top-level keys: `meta` and `requirements`.

---

## Top-level structure

```json
{
  "meta": {
    "project": "string — product name",
    "version": "string — e.g. 1.0",
    "created": "ISO date string",
    "updated": "ISO date string",
    "total_requirements": 0,
    "counts": {
      "REQ-F": 0,
      "REQ-NF": 0,
      "REQ-C": 0,
      "REQ-D": 0,
      "REQ-I": 0
    }
  },
  "requirements": [
    { ...entry }
  ]
}
```

---

## Entry schema

```json
{
  "id": "REQ-F-001",
  "title": "Short descriptive title (5–10 words)",
  "category": "FUNCTIONAL | NON-FUNCTIONAL | CONSTRAINT | DATA | INTEGRATION",
  "priority": "HIGH | MEDIUM | LOW",
  "status": "DRAFT | CONFIRMED | ASSUMED | IN_PROGRESS | IMPLEMENTED | VERIFIED | DELETED",
  "moscow": "MUST | SHOULD | COULD | WONT",
  "description": "Full requirement statement as written in BRD (one sentence, SHALL/SHOULD/MAY)",
  "source": {
    "document": "Blueprint §4 / Stakeholder input / Gap analysis / etc.",
    "feature": "Name of the feature or section this traces to"
  },
  "acceptance_criteria": [
    "Given [X], when [Y], then [Z].",
    "Additional AC if needed."
  ],
  "test_cases": [],
  "design_refs": [],
  "implementation_refs": [],
  "assumptions": [],
  "notes": "Any clarifying notes, links to open items, etc.",
  "created": "ISO date string",
  "updated": "ISO date string"
}
```

---

## Field notes

- `id` — Never reuse. Deleted entries keep their ID with `status: "DELETED"`.
- `status` — Start all generated entries at `DRAFT`. If blueprint confirms something
  explicitly, use `CONFIRMED`. If inferred, use `ASSUMED`.
- `moscow` — Derive from the SHALL/SHOULD/MAY in the requirement text:
  - SHALL → MUST
  - SHOULD → SHOULD
  - MAY → COULD
  - Out of scope → WONT (include in RTM for completeness when explicitly called out)
- `test_cases` — Empty array at seed time. QA team populates later.
- `design_refs` — Empty array at seed time. Design team populates with Figma/Lucid links.
- `acceptance_criteria` — At least one AC per requirement. Use Given/When/Then format.

---

## Example entry

```json
{
  "id": "REQ-F-007",
  "title": "Contextual AI tutor per widget session",
  "category": "FUNCTIONAL",
  "priority": "HIGH",
  "status": "CONFIRMED",
  "moscow": "MUST",
  "description": "The system SHALL provide an AI assistant that receives the current widget context (topic, parameters, user interactions) as part of its prompt, enabling context-aware responses.",
  "source": {
    "document": "Blueprint §4 — In Scope v1",
    "feature": "AI Assistant (Concept Advisor)"
  },
  "acceptance_criteria": [
    "Given a user is on the Normal Distribution widget, when they ask the AI 'what does this mean?', then the AI response SHALL reference the normal distribution concept and the current parameter values.",
    "Given the AI API is unavailable, when a user sends a message, then the system SHALL display a graceful error and offer to retry."
  ],
  "test_cases": [],
  "design_refs": [],
  "implementation_refs": [],
  "assumptions": [],
  "notes": "Context injection handled via system prompt prefix. See REQ-I-001 for API integration constraint.",
  "created": "2026-05-25",
  "updated": "2026-05-25"
}
```

---

*End of RTM schema*