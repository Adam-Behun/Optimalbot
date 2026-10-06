---
name: design-flow
description: Analyze sample conversations from MongoDB and generate flow definition pseudocode
tools: Read, Write, Glob, Bash
---

Analyze sample conversations and generate a flow definition document.

## Input

Format: `<org> <workflow>`
- `org`: Organization slug (e.g., `demo_clinic_alpha`)
- `workflow`: Workflow name (e.g., `eligibility_verification`)

## Process

### 1. Fetch Approved Conversations from MongoDB

Use Bash with curl to GET conversations from the API:

```bash
curl -X GET "http://localhost:8000/admin/onboarding/conversations/{org}/{workflow}" \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

**Important:** Before starting, ask the user for an auth token (JWT) or check if `$AUTH_TOKEN` is set.

Validation:
- NO conversations → Error: "No conversations found. Run cleanup-transcripts first."
- All status="cleaned" → Warning: "No approved conversations. Consider approving some in the Admin UI first."
- < 3 approved → Warning, continue with available
- ≥ 3 approved → Continue

### 2. Parse Response

Extract from each conversation: `roles`, `conversation`, `metadata`, `status`

Prefer approved conversations over cleaned ones for analysis.

### 3. Read Existing References

Check for existing `flow_definition.py` (naming conventions) and `schema.py` (field definitions).

### 4. Cross-Sample Analysis (LLM Reasoning)

**Conversation Phases:**
- What distinct phases appear across samples?
- What triggers transitions?
- Alternative paths (IVR vs direct human)?

**Data Fields:**
- What info is collected?
- Which fields come from caller vs other party?
- Data types and valid values?

**Bot Behavior:**
- How to greet/introduce?
- How to formulate questions?
- Closing patterns?

**Edge Cases:**
- Corrections handling?
- Info unavailable?
- IVR navigation?

### 5. Generate flow_definition.md

Write to: `portal/clients/{org}/{workflow}/flow_definition.md`

## Output Format

```markdown
# Flow Definition: {Workflow Name}
Generated from {N} samples on {YYYY-MM-DD}

## Overview
- **Call Direction:** dial-out | dial-in
- **Bot Role:** {description}
- **Target:** {who bot talks to}
- **Goal:** {summary}

## Input Data (Pre-populated)
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| patient_name | string | yes | Patient's full name | "Robert Williams" |

## Collected Data (During Call)
| Field | Type | Values/Format | Description |
|-------|------|---------------|-------------|
| network_status | enum | In-Network, Out-of-Network | Network status |

## Conversation Flow

### Node: {node_name}
**Purpose:** {what this accomplishes}
**Responds Immediately:** yes | no

#### Bot Behavior
- {instruction}

#### Data Captured
- `{field}` ({type}) - {when captured}

#### Transitions
- {condition} → **{next_node}**

#### Example Exchange
REP: "{example}"
BOT: "{response}"

---

## Special Handling
- IVR Navigation
- Corrections
- Information Unavailable
- Transfer Requests

## Guardrails
1. NEVER invent data
2. ...
```

## Progress

After fetching: "Fetched {N} conversations ({M} approved)"
During analysis: "Analyzing conversation patterns..."
At end: "Generated flow_definition.md with {X} nodes and {Y} data fields"
