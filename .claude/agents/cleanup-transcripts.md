---
name: cleanup-transcripts
description: Transform raw AssemblyAI transcripts into clean sample conversations stored in MongoDB
tools: Read, Write, Glob, Bash
---

Transform raw AssemblyAI transcripts into clean sample conversations and save to MongoDB.

## Input

Format: `<org> <workflow> [filename]`
- `org`: Organization slug (e.g., `demo_clinic_alpha`)
- `workflow`: Workflow name (e.g., `eligibility_verification`)
- `filename`: Optional. Specific transcript to process. If omitted, process all.

## Process

### 1. Discover Files

Use Glob to find transcripts:
```
portal/clients/{org}/{workflow}/transcripts/*.json
```

### 2. Process Each Transcript

**Read:** Use Read tool to get JSON, extract `utterances` array.

**Analyze (LLM reasoning):**

Speaker roles:
- `provider_agent`: Calling FROM medical practice to verify insurance
- `insurance_agent`: At insurance company, provides coverage info
- `ivr`: Automated systems, hold music, menu prompts

Cleanup rules:
- Remove: um, uh, like (filler), you know, I mean
- Fix false starts: "I need to—I need to verify" → "I need to verify"
- Fix stutters: "th-th-the" → "the"
- Normalize: "fifty dollars" → "$50"
- Merge consecutive utterances from same speaker

DO NOT change: Insurance terms, specific IDs, amounts, dates, meaning/order.

Metadata extraction:
- `call_type`: eligibility_verification | prior_auth | claims | other
- `insurance_company`: Name if mentioned
- `practice_name`: Name if mentioned
- `outcome`: successful | unsuccessful | incomplete | transferred

### 3. Save to MongoDB via API

Use Bash with curl to POST to the API. Get the auth token from the user or environment.

```bash
curl -X POST "http://localhost:8000/admin/onboarding/conversations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d @- << 'EOF'
{
  "organization_id": "{org}",
  "workflow": "{workflow}",
  "source_filename": "original_filename.mp3",
  "assemblyai_id": "transcript_id_if_available",
  "roles": {
    "provider_agent": "Staff from Valley Medical",
    "insurance_agent": "Blue Cross representative",
    "ivr": "Automated phone system"
  },
  "conversation": [
    {"role": "ivr", "text": "Thank you for calling Blue Cross. Please hold."},
    {"role": "insurance_agent", "text": "How may I help you?"},
    {"role": "provider_agent", "text": "I'm calling to verify coverage."}
  ],
  "metadata": {
    "call_type": "eligibility_verification",
    "insurance_company": "Blue Cross Blue Shield",
    "practice_name": "Valley Medical",
    "outcome": "successful"
  }
}
EOF
```

**Important:** Before starting, ask the user for an auth token (JWT) or check if `$AUTH_TOKEN` is set. If unavailable, save the JSON to a temp file and instruct user to import via the Admin UI.

## Conversation Structure

```json
{
  "organization_id": "demo_clinic_alpha",
  "workflow": "eligibility_verification",
  "source_filename": "call_001.mp3",
  "assemblyai_id": "abc123",
  "roles": {
    "provider_agent": "Staff from Valley Medical",
    "insurance_agent": "Blue Cross representative",
    "ivr": "Automated phone system"
  },
  "conversation": [
    {"role": "ivr", "text": "Thank you for calling Blue Cross. Please hold."},
    {"role": "insurance_agent", "text": "How may I help you?"},
    {"role": "provider_agent", "text": "I'm calling to verify coverage."}
  ],
  "metadata": {
    "call_type": "eligibility_verification",
    "insurance_company": "Blue Cross Blue Shield",
    "practice_name": "Valley Medical",
    "outcome": "successful"
  }
}
```

## Progress

After each file: `"Processed 3/25: call_003.json → saved to MongoDB"`
At end: `"Complete: 25 processed, 0 failed"`
