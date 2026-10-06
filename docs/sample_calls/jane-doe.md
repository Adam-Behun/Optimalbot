# Demo Call Script
**Patient:** Jane Doe (Date of Birth: 05/22/1990)

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
> *Bot should enter subscriber ID: AET123456789*
---
**Insurance - IVR**
"I found the member. Plan: Aetna PPO. Status: Active. Deductible: $1,000, $500 met. Out of pocket max: $5,000, $1,200 met. For more benefits, press 1. To verify CPT code coverage, press 2. To speak with a representative, press 3."
> *Bot should press: 2 (need CPT code verification)*
---
**Insurance - IVR**
"Enter the 5-digit CPT code."
> *Bot should enter CPT code: 99213*
---
**Insurance - IVR**
"CPT 99213 is covered. No prior authorization required. Estimated patient responsibility: $40 copay plus 20% coinsurance after deductible. To submit prior auth online, press 1. To speak with a prior auth specialist, press 2. To check another CPT code, press 3."
> *Bot should press: 2 (need specialist for detailed verification)*
---
**Insurance - IVR**
"Transferring to prior authorization. Please hold."
> *Bot should wait*
---
**Insurance - IVR**
"Prior authorization department. For status of existing auth, press 1. To initiate new authorization, press 2. For clinical review questions, press 3."
> *Bot should press: 2*
---
**Insurance - IVR**
"New authorization. Please hold for the next available clinical reviewer."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

> **NOTE: This is a post-IVR entry. The bot has just navigated through the IVR. It should NOT re-introduce itself with a full greeting — it should ANSWER the rep's verification questions.**

**Insurance Representative**
"Provider services, this is Sarah. Who am I speaking with?"
> *Bot provides name and facility (Metro Health Clinic)*
> *Bot should record: insurance_rep_first_name=Sarah*
---
**Insurance Representative**
"And your tax ID?"
> *Bot provides: 12-3456789*
---
**Insurance Representative**
"Member's name and date of birth?"
> *Bot provides: Jane Doe, 05/22/1990*
---
**Insurance Representative**
"Let me pull that up... How can I help you today?"
> *Bot asks about eligibility/benefits verification for CPT 99213*
---

### Plan Information

**Insurance Representative**
*(When asked about network status)*
"Yes, Metro Health Clinic is in network."
> *Bot should record: network_status=In-Network*
---
**Insurance Representative**
*(When asked about plan type)*
"PPO."
> *Bot should record: plan_type=PPO*
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
*(When asked about coverage for CPT 99213)*
"What's the date of service?"
> *Bot provides date*
"Let me check ninety-nine two thirteen... Covered. Forty dollar copay, twenty percent coinsurance, deductible applies, no prior auth, telehealth is covered."
> *Bot should record:*
> - *cpt_covered=Yes*
> - *copay_amount=40.00*
> - *coinsurance_percent=20*
> - *deductible_applies=Yes*
> - *prior_auth_required=No*
> - *telehealth_covered=Yes*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about individual deductible)*
"Individual deductible is five hundred dollars, two fifty has been met."
> *Bot should record:*
> - *deductible_individual=500.00*
> - *deductible_individual_met=250.00*
---
**Insurance Representative**
*(When asked about individual out-of-pocket max)*
"Individual out of pocket max is twenty-five hundred, six hundred applied."
> *Bot should record:*
> - *oop_max_individual=2500.00*
> - *oop_max_individual_met=600.00*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family deductible)*
"Family deductible is one thousand dollars, and five hundred has been met."
> *Bot should record:*
> - *deductible_family=1000.00*
> - *deductible_family_met=500.00*
---
**Insurance Representative**
*(When asked about family out-of-pocket max)*
"Family out of pocket max is five thousand dollars, twelve hundred applied."
> *Bot should record:*
> - *oop_max_family=5000.00*
> - *oop_max_family_met=1200.00*
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"Reference is ATN-IVR-2025-001."
> *Bot should record: reference_number=ATN-IVR-2025-001*
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
| Plan Type | PPO |
| Effective Date | 01/01/2025 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | No |
| Copay | 40.00 |
| Coinsurance | 20 |
| Deductible Applies | Yes |
| Telehealth Covered | Yes |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 500.00 |
| Individual Deductible Met | 250.00 |
| Individual OOP Max | 2500.00 |
| Individual OOP Met | 600.00 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 1000.00 |
| Family Deductible Met | 500.00 |
| Family OOP Max | 5000.00 |
| Family OOP Met | 1200.00 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Sarah |
| Reference Number | ATN-IVR-2025-001 |
