# Demo Call Script
**Patient:** Christopher Lee (Date of Birth: 12/03/1970)

## PART 1: IVR Navigation

**Insurance - IVR**
"Gracias por llamar a Kaiser Permanente. Para español, oprima uno. For English, press 2."
> *Bot should press: 2*
---
**Insurance - IVR**
"Welcome to Kaiser Permanente. For appointments, press 1. For prescription refills, press 2. For billing questions, press 3. For medical advice, press 4. For all other services, press 5."
> *Bot should press: 5 (provider eligibility would be under "all other services")*
---
**Insurance - IVR**
"Other services. For medical records, press 1. For durable medical equipment, press 2. For transportation, press 3. For provider services, press 4. For member services, press 5."
> *Bot should press: 4*
---
**Insurance - IVR**
"Provider services. Are you a contracted Kaiser provider? Press 1 for yes, press 2 for no."
> *Bot should press: 2 (non-contracted provider calling about patient eligibility)*
---
**Insurance - IVR**
"For out-of-network claims, press 1. For patient eligibility verification, press 2. For authorization requests, press 3."
> *Bot should press: 2*
---
**Insurance - IVR**
"Patient eligibility. Please have the member's Kaiser ID number ready. Press 1 to continue."
> *Bot should press: 1*
---
**Insurance - IVR**
"Enter the member's 10-digit Kaiser ID."
> *Bot should enter member ID*
---
**Insurance - IVR**
"Member located. Active HMO plan. For benefit summary, press 1. For specific service authorization, press 2. To speak with eligibility staff, press 3."
> *Bot should press: 3 (need to speak with staff for PA and CPT questions)*
---
**Insurance - IVR**
"Transferring to eligibility department. Please hold."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

**Insurance Representative**
"Kaiser provider line, Michael speaking. How can I help?"
> *Bot introduces itself and facility (Wellness Medical Center)*
> *Bot should record: insurance_rep_first_name=Michael*
---
**Insurance Representative**
"Thank you. Can I get the facility's street address?"
> *Bot should say: I don't have that information.*
---
**Insurance Representative**
"No problem. Fax number?"
> *Bot should say: I don't have that information.*
---
**Insurance Representative**
"That's fine. Tax ID?"
> *Bot provides: 11-2233445*
---
**Insurance Representative**
"And your callback number?"
> *Bot provides: (555) 890-1234*
---
**Insurance Representative**
"Okay, and the member's name and date of birth?"
> *Bot provides: Christopher Lee, 12/03/1970*
---
**Insurance Representative**
"Let me pull that up... Okay, I have Christopher Lee. What do you need today?"
> *Bot asks about eligibility/benefits verification for CPT 99203*
---

### Plan Information

**Insurance Representative**
*(When asked about network status)*
"Yes, Wellness Medical Center is in-network."
> *Bot should record: network_status=In-Network*
---
**Insurance Representative**
*(When asked about plan type)*
"It's an HMO plan."
> *Bot should record: plan_type=HMO*
---
**Insurance Representative**
*(When asked about effective date)*
"January first, twenty twenty five."
> *Bot should record: plan_effective_date=01/01/2025*
---
**Insurance Representative**
*(When asked about term date)*
"No termination date."
> *Bot should record: plan_term_date=None*
---

### CPT Coverage Details

**Insurance Representative**
*(When asked about coverage for CPT 99203)*
"Let me check ninety-nine two oh three... Yes, that's covered. Thirty dollar copay, no coinsurance on this HMO, no deductible applies, no prior auth needed, telehealth is covered."
> *Bot should record:*
> - *cpt_covered=Yes*
> - *copay_amount=30.00*
> - *coinsurance_percent=None*
> - *deductible_applies=No*
> - *prior_auth_required=No*
> - *telehealth_covered=Yes*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about individual deductible and OOP)*
"This HMO has no deductible. The individual out-of-pocket max is fifteen hundred, two seventy has been used."
> *Bot should record:*
> - *deductible_individual=None (HMO — no deductible)*
> - *oop_max_individual=1500.00*
> - *oop_max_individual_met=270.00*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family OOP)*
"Family out-of-pocket max is three thousand, five forty has been used."
> *Bot should record:*
> - *deductible_family=None (HMO — no deductible)*
> - *oop_max_family=3000.00*
> - *oop_max_family_met=540.00*
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"Reference is KP-2025-HMO-8899."
> *Bot should record: reference_number=KP-2025-HMO-8899*
---
**Insurance Representative**
*(When bot wraps up)*
"Anything else? Alright, have a good day."
> *Bot should say goodbye and end call*

---
## Verification Checklist
After the call, verify the bot collected these values correctly:

### Plan Information
| Field | Expected Value |
|-------|----------------|
| Network Status | In-Network |
| Plan Type | HMO |
| Effective Date | 01/01/2025 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | No |
| Copay | 30.00 |
| Coinsurance | None |
| Deductible Applies | No |
| Telehealth Covered | Yes |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | None (HMO) |
| Individual OOP Max | 1500.00 |
| Individual OOP Met | 270.00 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | None (HMO) |
| Family OOP Max | 3000.00 |
| Family OOP Met | 540.00 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Michael |
| Reference Number | KP-2025-HMO-8899 |
