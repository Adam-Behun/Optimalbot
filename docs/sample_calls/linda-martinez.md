# Demo Call Script
**Patient:** Linda Martinez (Date of Birth: 08/15/1983)

## PART 1: IVR Navigation

**Insurance - IVR**
"Thank you for calling Cigna. For faster service, visit cigna.com. To continue by phone, press 1."
> *Bot should press: 1*
---
**Insurance - IVR**
"For medical, press 1. For dental, press 2. For pharmacy, press 3. For behavioral health, press 4."
> *Bot should press: 1*
---
**Insurance - IVR**
"Medical services. For personal health insurance, press 1. For employer plans, press 2. For healthcare professionals, press 3."
> *Bot should press: 3*
---
**Insurance - IVR**
"One moment while we transfer you."
> *Bot should wait*
---
**Insurance - IVR**
"Cigna Dental provider services. For credentialing, press 1. For claims, press 2. For fee schedules, press 3. To return to main menu, press star."
> *Bot should press: * (Wrong department! Transferred to dental instead of medical. Go back.)*
---
**Insurance - IVR**
"Main menu. For medical, press 1. For dental, press 2. For pharmacy, press 3."
> *Bot should press: 1*
---
**Insurance - IVR**
"Medical. For members, press 1. For employers, press 2. For providers, press 3."
> *Bot should press: 3*
---
**Insurance - IVR**
"Provider services. For eligibility and benefits, press 1. For claims, press 2. For prior authorization, press 3. For network status, press 4."
> *Bot should press: 1*
---
**Insurance - IVR**
"Eligibility. For automated lookup, press 1. To speak with a representative, press 2."
> *Bot should press: 2 (need representative for complex verification)*
---
**Insurance - IVR**
"Please hold for the next available representative. Wait time is approximately 6 minutes."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

**Insurance Representative**
"Cigna provider services, this is Lisa. How can I help you?"
> *Bot introduces itself and facility (City Health Partners)*
> *Bot should record: insurance_rep_first_name=Lisa*
---
**Insurance Representative**
"Thank you. Can I get the facility name and tax ID?"
> *Bot provides: City Health Partners, 66-7788990*
---
**Insurance Representative**
"And the member's name and date of birth?"
> *Bot provides: Linda Martinez, 08/15/1983*
---
**Insurance Representative**
"Let me pull that up... Okay, I have Linda Martinez. What do you need?"
> *Bot asks about eligibility/benefits verification for CPT 99212*
---

### Plan Information

**Insurance Representative**
*(When asked about network status)*
"Yes, City Health Partners is in-network."
> *Bot should record: network_status=In-Network*
---
**Insurance Representative**
*(When asked about plan type)*
"PPO plan."
> *Bot should record: plan_type=PPO*
---
**Insurance Representative**
*(When asked about effective date)*
"May first, twenty twenty four."
> *Bot should record: plan_effective_date=05/01/2024*
---
**Insurance Representative**
*(When asked about term date)*
"No termination date."
> *Bot should record: plan_term_date=None*
---

### CPT Coverage Details

**Insurance Representative**
*(When asked about coverage for CPT 99212)*
"Let me check ninety-nine two twelve... Yes, that's covered. Twenty-five dollar copay, twenty percent coinsurance, deductible applies, no prior auth, telehealth is covered."
> **NOTE: Lisa made a MISTAKE here — she said $25 copay. The correct copay is $50. She will correct this later.**
> *Bot should record (initial values):*
> - *cpt_covered=Yes*
> - *copay_amount=25.00 (INCORRECT — will be corrected)*
> - *coinsurance_percent=20*
> - *deductible_applies=Yes*
> - *prior_auth_required=No*
> - *telehealth_covered=Yes*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about individual deductible)*
"Individual deductible is five hundred, three fifty met."
> *Bot should record:*
> - *deductible_individual=500.00*
> - *deductible_individual_met=350.00*
---
**Insurance Representative**
*(When asked about individual out-of-pocket max)*
"Individual out-of-pocket max is three thousand, seven fifty applied."
> *Bot should record:*
> - *oop_max_individual=3000.00*
> - *oop_max_individual_met=750.00*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family deductible)*
"Family deductible is one thousand, seven hundred has been met."
> *Bot should record:*
> - *deductible_family=1000.00*
> - *deductible_family_met=700.00*
---
**Insurance Representative**
*(When asked about family out-of-pocket max)*
"Family out-of-pocket max is six thousand, fifteen hundred has been used."
> *Bot should record:*
> - *oop_max_family=6000.00*
> - *oop_max_family_met=1500.00*
---

### Copay Correction

**Insurance Representative**
*(Unprompted, after providing accumulators)*
"Oh wait, before we continue — I need to correct something. I gave you the wrong copay earlier. It should be FIFTY dollars, not twenty-five. Can you update that?"
> **CRITICAL: Bot must UPDATE the previously recorded copay from $25 to $50.**
> *Bot should acknowledge the correction and update: copay_amount=50.00*
---
**Insurance Representative**
*(After bot acknowledges)*
"Great, thank you for catching that."
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"Reference is CIG-CORR-2025-3456."
> *Bot should record: reference_number=CIG-CORR-2025-3456*
---
**Insurance Representative**
*(When bot wraps up)*
"Is there anything else I can help with? Alright, have a good day."
> *Bot should say goodbye and end call*

---
## Verification Checklist
After the call, verify the bot collected these values correctly:

### Plan Information
| Field | Expected Value |
|-------|----------------|
| Network Status | In-Network |
| Plan Type | PPO |
| Effective Date | 05/01/2024 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | No |
| Copay | 50.00 |
| Coinsurance | 20 |
| Deductible Applies | Yes |
| Telehealth Covered | Yes |

> **NOTE:** The copay must be **50.00** (the CORRECTED value), not 25.00 (the initial mistake). This tests the bot's ability to update previously recorded data.

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 500.00 |
| Individual Deductible Met | 350.00 |
| Individual OOP Max | 3000.00 |
| Individual OOP Met | 750.00 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 1000.00 |
| Family Deductible Met | 700.00 |
| Family OOP Max | 6000.00 |
| Family OOP Met | 1500.00 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Lisa |
| Reference Number | CIG-CORR-2025-3456 |
