# Demo Call Script
**Patient:** David Kim (Date of Birth: 09/05/1982)

## PART 1: IVR Navigation

**Insurance - IVR**
"Thank you for calling Humana. For English, press 1. Para español, oprima 2."
> *Bot should press: 1*
---
**Insurance - IVR**
"For faster service, visit humana.com/providers. For Medicare Advantage, press 1. For commercial plans, press 2. For Medicaid, press 3."
> *Bot should press: 2*
---
**Insurance - IVR**
"Commercial plans. For claims, press 1. For prior authorization, press 2. For eligibility, press 3. For credentialing, press 4."
> *Bot should press: 3*
---
**Insurance - IVR**
"Eligibility verification for commercial plans is now available exclusively through our online provider portal at availity.com. For portal registration help, press 1. To return to main menu, press star."
> *Bot should press: * (eligibility is web-only — need alternate path)*
---
**Insurance - IVR**
"Commercial plans. For claims, press 1. For prior authorization, press 2. For eligibility, press 3. For credentialing, press 4."
> *Bot should press: 2 (try prior authorization — reps there can help with eligibility too)*
---
**Insurance - IVR**
"Prior authorization. For status of pending auth, press 1. To initiate new auth, press 2. For clinical questions, press 3. To speak with a representative, press 0."
> *Bot should press: 0 (representative can help with both eligibility and PA)*
---
**Insurance - IVR**
"All representatives are busy. Expected wait: 8 minutes. To continue holding, press 1. For callback, press 2."
> *Bot should press: 1 (8 minutes is reasonable — continue holding)*
---
**Insurance - IVR**
"[Hold music] Your call is important to us."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

**Insurance Representative**
"Thank you for holding. This is Sandra with prior authorization. How can I assist you?"
> *Bot introduces itself and facility (Central Medical Group)*
> *Bot should record: insurance_rep_first_name=Sandra*
---
**Insurance Representative**
"Thank you. May I have the facility name?"
> *Bot provides: Central Medical Group*
---
**Insurance Representative**
"And the tax ID for Central Medical Group?"
> *Bot provides: 55-6677889*
---
**Insurance Representative**
"Thank you. And the member's name and date of birth?"
> *Bot provides: David Kim, 09/05/1982*
---
**Insurance Representative**
"Let me pull that up... one moment please."
> *Bot should wait patiently*

**Insurance Representative**
"I apologize, my system is running slow today. Still loading..."
> *Bot should wait patiently*

**Insurance Representative**
"Okay, I have David Kim here. What can I help you with?"
> *Bot asks about eligibility/benefits verification for CPT 99214*
---

### Plan Information

**Insurance Representative**
*(When asked about network status)*
"Let me check that for you... can you hold for just a moment?"
> *Bot should wait patiently*

"Still pulling it up... I apologize for the delay."
> *Bot should wait patiently*

"Okay, Central Medical Group is in-network."
> *Bot should record: network_status=In-Network*
---
**Insurance Representative**
*(When asked about plan type)*
"That's a POS plan."
> *Bot should record: plan_type=POS*
---
**Insurance Representative**
*(When asked about effective date)*
"Let me verify... one second."
> *Bot should wait patiently*

"January first, twenty twenty five."
> *Bot should record: plan_effective_date=01/01/2025*
---
**Insurance Representative**
*(When asked about term date)*
"No termination date on file."
> *Bot should record: plan_term_date=None*
---

### CPT Coverage Details

**Insurance Representative**
*(When asked about coverage for CPT 99214)*
"What's the date of service for that visit?"
> *Bot provides: 01/20/2025*

"Okay, let me check ninety-nine two fourteen..."
> *Bot should wait patiently*

"Please hold, I need to pull up the benefits screen."
> *Bot should wait patiently*

"The system is taking a moment... I appreciate your patience."
> *Bot should wait patiently*

"Almost there..."
> *Bot should wait patiently*

"Got it. That code is covered. Thirty-five dollar copay."
> *Bot should record: cpt_covered=Yes, copay_amount=35.00*
---
**Insurance Representative**
*(When asked about coinsurance)*
"No coinsurance for this service."
> *Bot should record: coinsurance_percent=None*
---
**Insurance Representative**
*(When asked about deductible applies)*
"Let me verify that... hold on."
> *Bot should wait patiently*

"Yes, the deductible does apply."
> *Bot should record: deductible_applies=Yes*
---
**Insurance Representative**
*(When asked about prior auth)*
"No prior authorization required."
> *Bot should record: prior_auth_required=No*
---
**Insurance Representative**
*(When asked about telehealth)*
"Yes, telehealth is covered for this code."
> *Bot should record: telehealth_covered=Yes*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about individual deductible)*
"Let me pull up the individual numbers... one moment."
> *Bot should wait patiently*

"Individual deductible is three hundred, two hundred has been met."
> *Bot should record:*
> - *deductible_individual=300.00*
> - *deductible_individual_met=200.00*
---
**Insurance Representative**
*(When asked about individual out-of-pocket max)*
"Checking..."
> *Bot should wait patiently*

"Individual OOP max is twenty-two fifty, four forty-five applied."
> *Bot should record:*
> - *oop_max_individual=2250.00*
> - *oop_max_individual_met=445.00*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family deductible)*
"I need to pull up a different screen for that. Bear with me."
> *Bot should wait patiently*

"Still loading the accumulator information..."
> *Bot should wait patiently*

"Okay, the family deductible is six hundred dollars, four hundred has been met."
> *Bot should record:*
> - *deductible_family=600.00*
> - *deductible_family_met=400.00*
---
**Insurance Representative**
*(When asked about family out-of-pocket max)*
"Let me check..."
> *Bot should wait patiently*

"Family out of pocket max is forty-five hundred, eight ninety applied."
> *Bot should record:*
> - *oop_max_family=4500.00*
> - *oop_max_family_met=890.00*
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"The reference number is HUM-SLOW-2025-777."
> *Bot should record: reference_number=HUM-SLOW-2025-777*
---
**Insurance Representative**
*(When bot wraps up)*
"Thank you for your patience today. Is there anything else? Alright, have a good day."
> *Bot should say goodbye and end call*

---
## Verification Checklist
After the call, verify the bot collected these values correctly:

### Plan Information
| Field | Expected Value |
|-------|----------------|
| Network Status | In-Network |
| Plan Type | POS |
| Effective Date | 01/01/2025 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | No |
| Copay | 35.00 |
| Coinsurance | None |
| Deductible Applies | Yes |
| Telehealth Covered | Yes |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 300.00 |
| Individual Deductible Met | 200.00 |
| Individual OOP Max | 2250.00 |
| Individual OOP Met | 445.00 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 600.00 |
| Family Deductible Met | 400.00 |
| Family OOP Max | 4500.00 |
| Family OOP Met | 890.00 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Sandra |
| Reference Number | HUM-SLOW-2025-777 |
