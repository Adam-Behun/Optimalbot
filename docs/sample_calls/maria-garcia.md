# Demo Call Script
**Patient:** Maria Garcia (Date of Birth: 07/22/1978)

## PART 1: IVR Navigation

**Insurance - IVR**
"Thank you for calling Aetna. If you're a healthcare provider, press 1. If you're a member, press 2. For all other callers, press 3."
> *Bot should press: 1*
---
**Insurance - IVR**
"Provider services. For our automated eligibility system available 24/7, press 1. For prior authorization, press 2. For claims, press 3. For credentialing, press 4. To speak with a representative, press 0."
> *Bot should press: 1 (try automated eligibility first — faster if it works)*
---
**Insurance - IVR**
"Automated eligibility. Please enter the subscriber ID."
> *Bot should enter subscriber ID: AET987654321*
---
**Insurance - IVR**
"I found the member. Plan: Aetna PPO. Status: Active. Deductible: $1,000, $650 met. Out of pocket max: $8,000, $2,340 met. For more benefits, press 1. To verify CPT code coverage, press 2. To speak with a representative, press 3."
> *Bot should press: 2 (need CPT code verification)*
---
**Insurance - IVR**
"Enter the 5-digit CPT code."
> *Bot should enter CPT code: 70553*
---
**Insurance - IVR**
"CPT 70553 is covered. Prior authorization is required for this service. Estimated patient responsibility: $75 copay plus 20% coinsurance after deductible. To submit prior auth online, press 1. To speak with a prior auth specialist, press 2. To check another CPT code, press 3."
> *Bot should press: 2 (need PA specialist for complex authorization)*
---
**Insurance - IVR**
"Transferring to prior authorization. Please hold."
> *Bot should wait*
---
**Insurance - IVR**
"Prior authorization department. For status of existing auth, press 1. To initiate new authorization, press 2. For clinical review questions, press 3."
> *Bot should press: 2 (need to initiate new authorization)*
---
**Insurance - IVR**
"New authorization. Please hold for the next available clinical reviewer."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

**Insurance Representative**
"Aetna provider line, Marcus speaking. How can I help?"
> *Bot introduces itself and facility (Metro Imaging Center)*
> *Bot should record: insurance_rep_first_name=Marcus*
> *Bot should ask for last initial*
---
**Insurance Representative**
"Thanks. Can I get the facility name and tax ID?"
> *Bot provides: Metro Imaging Center, tax ID 45-6789012*
---
**Insurance Representative**
"And the member's name and date of birth?"
> *Bot provides: Maria Garcia, 07/22/1978*
---
**Insurance Representative**
"Okay, let me pull that up... Got it. What do you need today?"
> *Bot asks about eligibility/benefits verification for CPT 70553*
---

### Plan Information

**Insurance Representative**
*(When asked about network status)*
"Yeah, Metro Imaging is in network."
> *Bot should record: network_status=In-Network*
---
**Insurance Representative**
*(When asked about plan type)*
"PPO."
> *Bot should record: plan_type=PPO*
---
**Insurance Representative**
*(When asked about effective date)*
"March fifteenth twenty twenty four."
> *Bot should record: plan_effective_date=03/15/2024*
---
**Insurance Representative**
*(When asked about term date)*
"No term date."
> *Bot should record: plan_term_date=None*
---

### CPT Coverage Details

**Insurance Representative**
*(When asked about coverage for CPT 70553)*
"What's the date of service?"
> *Bot provides date: 01/15/2025*
"Let me check 70553.. Okay so that code is covered, seventy-five copay, twenty percent coinsurance, you'll need a PA on that, ded applies. Anything else?"
> **CRITICAL: Marcus buries "PA" (prior authorization) casually among other details in rapid-fire delivery. Bot must catch it.**
> *Bot should record:*
> - *cpt_covered=Yes*
> - *copay_amount=75.00*
> - *coinsurance_percent=20*
> - *deductible_applies=Yes*
> - *prior_auth_required=Yes (said as "PA" — bot must recognize this means prior authorization)*
---
**Insurance Representative**
*(When asked about telehealth)*
"Telehealth? Not applicable for imaging procedures."
> *Bot should record: telehealth_covered=N/A*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about individual deductible)*
"Individual ded five hundred, 375 met."
> *Bot should record:*
> - *deductible_individual=500.00*
> - *deductible_individual_met=375.00*
---
**Insurance Representative**
*(When asked about individual out-of-pocket max)*
"Individual OOP max four K, 1170 applied."
> *Bot should record:*
> - *oop_max_individual=4000.00*
> - *oop_max_individual_met=1170.00*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family deductible)*
"Family ded is a thousand, six fifty met."
> *Bot should record:*
> - *deductible_family=1000.00*
> - *deductible_family_met=650.00*
---
**Insurance Representative**
*(When asked about family out-of-pocket max)*
"OOP max is eight K, twenty-three forty applied."
> *Bot should record:*
> - *oop_max_family=8000.00*
> - *oop_max_family_met=2340.00*
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"Reference is ATN-PA-445566."
> *Bot should record: reference_number=ATN-PA-445566*
---
**Insurance Representative**
*(When bot wraps up)*
"Alright, anything else? No? Okay, take care."
> *Bot should say goodbye and end call*

---
## Verification Checklist
After the call, verify the bot collected these values correctly:

### Plan Information
| Field | Expected Value |
|-------|----------------|
| Network Status | In-Network |
| Plan Type | PPO |
| Effective Date | 03/15/2024 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | Yes |
| Copay | 75.00 |
| Coinsurance | 20 |
| Deductible Applies | Yes |
| Telehealth Covered | N/A |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 500.00 |
| Individual Deductible Met | 325.00 |
| Individual OOP Max | 4000.00 |
| Individual OOP Met | 1170.00 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 1000.00 |
| Family Deductible Met | 650.00 |
| Family OOP Max | 8000.00 |
| Family OOP Met | 2340.00 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Marcus |
| Reference Number | ATN-PA-445566 |
