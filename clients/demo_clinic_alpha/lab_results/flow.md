# Lab Results Flow

## State Variables

All in `flow_manager.state`. Populated from DB after phone lookup + DOB verification.

| Category | Fields |
|----------|--------|
| Identity | `patient_id`, `patient_name`, `first_name`, `last_name`, `date_of_birth`, `phone_number` |
| Lab Results | `test_type`, `test_date`, `ordering_physician`, `results_status`, `results_summary`, `provider_review_required`, `callback_timeframe` |
| Flags | `identity_verified`, `results_communicated`, `routed_to`, `callback_confirmed` |

---

## Entry Points

| Entry | Method | → First Node |
|-------|--------|--------------|
| Dial-in | `get_initial_node()` | `greeting` |
| Handoff (not verified) | `create_handoff_entry_node(context)` | `patient_lookup` |
| Handoff (verified) | `create_handoff_entry_node(context)` | `results_ready` / `results_pending` / `provider_review` (based on status) |

**Bridge node** (`_create_post_workflow_node`): When routing to scheduling/prescription after verification, creates transition with TTS message before handoff.

---

## Flow Diagram

```
greeting ──┬── proceed_to_lab_results ──► patient_lookup ──► verify_dob ──┬── results_ready ──► completion ──► end
           │                                    │                         ├── results_pending ──────┘
           │                                    │                         ├── provider_review ───────┘
           │                                    │                         ├── no_results (auto-transfer)
           │                                    ▼                         └── patient_not_found (retry once)
           │                             patient_not_found ──► retry_lookup ──┬── verify_dob (if found)
           │                                                                  └── patient_not_found_final (auto-transfer)
           │
           └── proceed_to_other ──► other_requests ──► scheduling/prescription flows or transfer
```

---

## Nodes

### `greeting`
- **pre_action**: "Hello, this is {org_name} laboratory results. How can I help you?"

Route silently (no speech):
- Lab results → `proceed_to_lab_results` → `patient_lookup`
- Anything else → `proceed_to_other` → `other_requests`

---

### `other_requests`
- *(no pre/post actions)*

Route based on intent:
- Scheduling → `route_to_workflow(workflow="scheduling")`
- Prescriptions → `route_to_workflow(workflow="prescription_status")`
- Human/billing → `request_staff`
- Changed mind, wants results → `proceed_to_lab_results`

---

### `patient_lookup`
- **pre_action**: "Sounds good! What's the phone number on your account?"

Collect phone, read back to confirm, then:
- `lookup_by_phone(phone_number)` → `verify_dob` if found, `patient_not_found` if not
- `request_staff` if caller doesn't know

---

### `verify_dob`
- **pre_action**: "Can you confirm your date of birth please?"
- **post_action**: "Let me pull up your account." *(gives LLM time to verify)*

`verify_dob(date_of_birth)` routes based on match + results status:
- ready + has summary → `results_ready`
- `provider_review_required=True` → `provider_review`
- pending/processing → `results_pending`
- no results on file → `no_results`
- DOB mismatch → `patient_not_found`

---

### `patient_not_found`
- **pre_action**: "I'm sorry, I couldn't find a record for {phone_number} with date of birth {dob}."

First attempt - allow retry:
- New phone/dob → `retry_lookup(phone_number, date_of_birth)` → `verify_dob` if found, `patient_not_found_final` if not
- Want human → `request_staff`

---

### `patient_not_found_final`
- **pre_action**: "I still couldn't find your record. Let me connect you with a colleague who can help."
- **post_action**: initiate SIP transfer

Auto-transfers after message plays.

---

### `no_results`
- **pre_action**: "I found your record, but I don't see any pending lab results. Let me connect you with a colleague who can help."
- **post_action**: initiate SIP transfer

Auto-transfers after message plays.

---

### `results_ready`
- **pre_action**: "Thank you, {first_name}. Your {test_type} results are in. Would you like me to read them for you?"

**Requires**: `identity_verified=True`

- Yes → `read_results` → `completion`
- No → `proceed_to_completion` → `completion`
- Human → `request_staff`

**`read_results` behavior**: Scripted TTS only. No LLM interpretation. Reads `results_summary` exactly as stored, with no additions, no omissions, no commentary.

---

### `results_pending`
- **pre_action**: "Thank you, {first_name}. Your {test_type} is still being processed. Would you like us to call you when they're ready?"

- Yes + confirm number → `confirm_callback(confirmed=true)`
- Yes + new number → `confirm_callback(confirmed=true, new_number="...")`
- No → `confirm_callback(confirmed=false)`

---

### `provider_review`
- **pre_action**: "Thank you, {first_name}. Your {test_type} results are in, but {ordering_physician} needs to review them before we can share the details. The doctor will call you within {callback_timeframe}. Is {phone_last4} still a good number?"

**CRITICAL**: Never share results when `provider_review_required=True`.

- Confirm/new number → `confirm_callback`
- Anxious caller → empathize, then `confirm_callback`

---

### `completion`
- **pre_action**: "Is there anything else I can help with?"

- Repeat results → `read_results` (scripted TTS, no deviation)
- Goodbye → `end_call`
- "Thank you" alone → NOT goodbye, ask "Anything else?"
- Scheduling → `route_to_workflow(workflow="scheduling")`
- Prescriptions → `route_to_workflow(workflow="prescription_status")`
- Billing/human → `request_staff`
- New callback number → `update_callback_number(new_number)`

**Note**: Results are NOT read proactively. Only read when patient asks.

---

### `transfer_failed`
- **pre_action**: "I apologize, the transfer didn't go through. Let me try again."

- Retry → `retry_transfer`
- Schedule/prescriptions → `route_to_workflow`
- Goodbye → `end_call`

---

### `transfer_initiated`
- **pre_action**: "Transferring you now, please hold."
- **post_action**: `end_conversation`

---

### `end`
- *(no pre_action - LLM says warm goodbye)*
- **post_action**: `end_conversation`

---

## Shared Functions

| Function | Description |
|----------|-------------|
| `end_call` | End call. Use for goodbye, NOT just "thank you" |
| `request_staff(reason)` | Transfer to human. For explicit requests or billing |
| `route_to_workflow(workflow, reason)` | Handoff to scheduling or prescription_status |
| `lookup_by_phone(phone_number)` | Look up patient by phone digits |
| `verify_dob(date_of_birth)` | Verify patient DOB against record |
| `confirm_callback(confirmed, new_number?)` | Confirm callback number for pending/review |
| `update_callback_number(new_number)` | Update callback number in completion |
| `retry_transfer` | Retry failed SIP transfer |
| `proceed_to_lab_results` | Route to patient_lookup |
| `proceed_to_other` | Route to other_requests |
| `read_results` | Scripted TTS of results_summary. No LLM interpretation. |
| `proceed_to_completion` | Skip reading results, go to completion |
| `retry_lookup(phone, dob)` | Retry phone+DOB lookup from patient_not_found |
