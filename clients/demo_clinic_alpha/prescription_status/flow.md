# Prescription Status Flow

**Clinic Type**: GLP-1 Weight Management
**Direction**: Dial-in
**Purpose**: Prescription status inquiries, refill requests

See `schema.py` for: status templates, medication aliases (MEDICATIONS dict).

---

## Entry Points

| Entry | Method | First Node |
|-------|--------|------------|
| Dial-in | `get_initial_node()` | `greeting` |
| Handoff (verified) | `create_handoff_entry_node(context)` | `status_*` or `medication_select` |
| Handoff (unverified) | `create_handoff_entry_node(context)` | `patient_lookup` |

---

## State Variables

| Variable | Type | Notes |
|----------|------|-------|
| `identity_verified` | bool | Set after DOB verification |
| `patient_id`, `first_name`, `last_name`, `date_of_birth`, `phone_number` | str | Identity fields |
| `prescriptions` | list | All patient prescriptions |
| `selected_prescription` | dict | Currently selected rx |
| `mentioned_medication` | str | Medication caller mentioned at greeting |
| `lookup_attempts` | int | Max 2, then transfer |
| `medication_select_attempts` | int | Max 2, then transfer |
| `routed_to` | str | Workflow routed to (for logging) |

---

## Flow Diagram

```
greeting ─┬─ proceed_to_prescription_status ──► patient_lookup ──► verify_dob ─┬─► status_* (single/matched)
          │                                           │                        └─► medication_select ──► status_*
          │                                           ▼
          │                                    patient_not_found ──► retry ──► patient_not_found_final ──► transfer
          └─ proceed_to_other ──► other_requests ──► route_to_workflow / request_staff

status_* ──► completion ──► end / check_another / route_to_workflow
Any node ──► request_staff ──► transfer_initiated ──► end
```

---

## Nodes

### `greeting`
**pre_action**: "Thank you for calling {org_name}. This is Jamie. How can I help you?"

Capture medication if mentioned → save to `mentioned_medication`.

| Intent | Function | Next |
|--------|----------|------|
| Prescription/refill | `proceed_to_prescription_status(mentioned_medication?)` | `patient_lookup` |
| Scheduling/labs | `proceed_to_other()` | `other_requests` |
| Human/billing | `request_staff(reason, patient_confirmed?)` | `transfer_initiated` |

---

### `other_requests`

| Intent | Function | Next |
|--------|----------|------|
| Scheduling | `route_to_workflow("scheduling", reason)` | handoff |
| Lab results | `route_to_workflow("lab_results", reason)` | handoff |
| Human/billing | `request_staff(...)` | `transfer_initiated` |
| Prescription | `proceed_to_prescription_status()` | `patient_lookup` |

---

### `patient_lookup`
Collect 10-digit phone, read back to confirm.

| Result | Function | Next |
|--------|----------|------|
| Found | `lookup_by_phone(phone_number)` | `verify_dob` |
| Not found (attempt < 2) | `lookup_by_phone(phone_number)` | `patient_not_found` |
| Not found (attempt = 2) | auto | `patient_not_found_final` |
| Caller doesn't know | `request_staff(...)` | `transfer_initiated` |

---

### `verify_dob`
**pre_action**: "I found your record. Can you confirm your date of birth?"

`verify_dob(date_of_birth)` → **software routing** (no LLM):

```python
if dob_mismatch:
    lookup_attempts += 1
    return patient_not_found if attempts < 2 else patient_not_found_final

# Mark verified, load domain data
if len(prescriptions) == 1:
    return status_node(prescriptions[0])
if mentioned_medication and match_found:
    return status_node(matched_rx)
return medication_select
```

---

### `patient_not_found`
**pre_action**: "I'm sorry, I couldn't find a record for that phone number and date of birth."

| Intent | Function | Next |
|--------|----------|------|
| New phone/dob | `retry_lookup(phone_number, date_of_birth?)` | `verify_dob` or `patient_not_found_final` |
| Want human | `request_staff(...)` | `transfer_initiated` |

---

### `patient_not_found_final`
**pre_action**: "I still couldn't find your record. Let me connect you with a colleague who can help."
**post_action**: SIP transfer + `end_conversation`

---

### `verification_failed`
**pre_action**: "I'm sorry, I wasn't able to verify your identity. For your security, I'll need to transfer you to a staff member. One moment please."
**post_action**: `end_conversation`

---

### `medication_select`
**Only reached when**: Multi-rx AND no `mentioned_medication` match
**pre_action**: "I see you have {meds} on file. Which one are you calling about?"

Max `medication_select_attempts` = 2.

| Result | Function | Next |
|--------|----------|------|
| Match found | `select_medication(medication_name)` | `status_*` |
| No match (< 2) | stay | Re-prompt |
| No match (= 2) | `request_staff("couldn't identify medication")` | `transfer_initiated` |

**Matching**: Check `medication_name`, `generic_name`, and all `aliases` (case-insensitive).

---

## Status Nodes

All status nodes share pattern:
- **pre_action**: TTS from status template
- **functions**: `proceed_to_completion`, `check_another_medication`, `request_staff`

### Status Key Mapping

| Status String | Node |
|---------------|------|
| sent, sent to pharmacy | `status_sent` |
| pending, pending prior auth, pending doctor approval, awaiting prior auth | `status_pending` |
| ready, ready for pickup | `status_ready` |
| too early, too early to refill | `status_too_early` |
| renewal, needs renewal, expired | `status_renewal` |
| active, refills, refills available, OR refills_remaining > 0 | `status_refills` |
| (default) | `status_pending` |

---

### `status_sent`
| Intent | Function | Next |
|--------|----------|------|
| Satisfied | `proceed_to_completion()` | `completion` |
| Questions | `request_staff("pharmacy questions")` | `transfer_initiated` |
| Another med | `check_another_medication()` | `medication_select` |

---

### `status_pending`
| Intent | Function | Next |
|--------|----------|------|
| Satisfied | `proceed_to_completion()` | `completion` |
| Urgent/expedite | `request_staff("expedite prior auth")` | `transfer_initiated` |
| Another med | `check_another_medication()` | `medication_select` |

---

### `status_ready`
| Intent | Function | Next |
|--------|----------|------|
| Satisfied | `proceed_to_completion()` | `completion` |
| Pharmacy issues | `request_staff("pharmacy issues")` | `transfer_initiated` |
| Another med | `check_another_medication()` | `medication_select` |

---

### `status_too_early`
| Intent | Function | Next |
|--------|----------|------|
| Accepts | `proceed_to_completion()` | `completion` |
| Exception needed | `request_staff("early refill exception")` | `transfer_initiated` |
| Another med | `check_another_medication()` | `medication_select` |

---

### `status_refills`
| Intent | Function | Next |
|--------|----------|------|
| Yes, send | `submit_refill()` | `completion` |
| No thanks | `proceed_to_completion()` | `completion` |
| Pharmacy change | `request_staff("pharmacy change")` | `transfer_initiated` |
| Another med | `check_another_medication()` | `medication_select` |

---

### `status_renewal`
| Intent | Function | Next |
|--------|----------|------|
| Yes, submit | `submit_renewal_request()` | `completion` |
| No thanks | `proceed_to_completion()` | `completion` |
| Dosage change | `request_staff("dosage change request")` | `transfer_initiated` |
| Another med | `check_another_medication()` | `medication_select` |

---

### `completion`
**pre_action**: "Is there anything else I can help you with today?"

NOTE: "Thank you" alone is NOT goodbye—wait for "that's all" or explicit farewell.

| Intent | Function | Next |
|--------|----------|------|
| Goodbye / "that's all" | `end_call()` | `end` |
| Another medication | `check_another_medication()` | `medication_select` or stay (single-rx) |
| Scheduling | `route_to_workflow("scheduling", reason)` | handoff |
| Lab results | `route_to_workflow("lab_results", reason)` | handoff |
| Human/billing | `request_staff(...)` | `transfer_initiated` |

---

### `transfer_initiated`
**pre_action**: "Transferring you now, please hold."
**post_action**: `end_conversation`

---

### `transfer_failed`
**pre_action**: "I apologize, the transfer didn't go through."

| Intent | Function | Next |
|--------|----------|------|
| Accept alternative / goodbye | `end_call()` | `end` |

---

### `end`
**post_action**: `end_conversation`

LLM generates warm goodbye.

---

## Functions Reference

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `end_call` | - | `end` | End call (explicit goodbye only) |
| `request_staff` | `reason: str`, `patient_confirmed?: bool` | `transfer_initiated` | Transfer to human |
| `route_to_workflow` | `workflow: str`, `reason: str` | handoff | Route to scheduling/lab_results |
| `lookup_by_phone` | `phone_number: str` | `verify_dob` / `patient_not_found` | Lookup by 10-digit phone |
| `verify_dob` | `date_of_birth: str` | `status_*` / `medication_select` / `patient_not_found` | Verify DOB, software-route |
| `retry_lookup` | `phone_number: str`, `date_of_birth?: str` | `verify_dob` / `patient_not_found_final` | Retry lookup |
| `select_medication` | `medication_name: str` | `status_*` | Match via aliases |
| `submit_refill` | - | `completion` | Submit to pharmacy |
| `submit_renewal_request` | - | `completion` | Submit to physician |
| `check_another_medication` | - | `medication_select` / `completion` | Multi-rx: select. Single-rx: stay |
| `proceed_to_prescription_status` | `mentioned_medication?: str` | `patient_lookup` | Route to rx flow |
| `proceed_to_other` | - | `other_requests` | Route to other handler |
| `proceed_to_completion` | - | `completion` | Route to completion |
