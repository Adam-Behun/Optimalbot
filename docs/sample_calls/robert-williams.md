# Demo Call Script
**Patient:** Robert Williams (Date of Birth: 11/30/1965)

## PART 1: IVR Navigation

**Insurance - IVR**
"Thank you for calling BlueCross BlueShield. For English, press 1. Para español, oprima 2."
> *Bot should press: 1*
---
**Insurance - IVR**
"Please listen carefully as our menu options have changed. For individual and family plans, press 1. For group and employer plans, press 2. For Medicare, press 3. For healthcare providers, press 4."
> *Bot should press: 4*
---
**Insurance - IVR**
"Provider services. For member eligibility and benefits, press 1. For claims status, press 2. For pharmacy, press 3. To speak with a provider representative, press 0."
> *Bot should press: 0 (NOT 1 — that's for members checking their own benefits)*
---
**Insurance - IVR**
"All representatives are currently assisting other callers. Your estimated wait time is 25 minutes. To continue holding, press 1. To receive a callback, press 2."
> *Bot should press: 1 (under 30 min threshold)*
---
**Insurance - IVR**
"Thank you for holding. Your estimated wait time is now 18 minutes."
> *Bot should wait*
---
**Insurance - IVR**
"Your estimated wait time is now 8 minutes. Thank you for your patience."
> *Bot should wait*
---
**Insurance - IVR**
"You are next in queue. A representative will be with you shortly."
> *Bot should wait*
---
**Insurance - IVR**
"[Hold music] Thank you for your patience. A representative will be with you shortly."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

**Insurance Representative**
"Blue Cross Blue Shield, this is Diana. May I have your name and the facility you're calling from?"
> *Bot introduces itself and facility (Specialty Surgery Associates)*
> *Bot should record: insurance_rep_first_name=Diana*
---
**Insurance Representative**
"Thank you. And what's the tax ID for Specialty Surgery Associates?"
> *Bot provides: 33-4455667*
---
**Insurance Representative**
"Got it. And the member's name and date of birth?"
> *Bot provides: Robert Williams, 11/30/1965*
---
**Insurance Representative**
"Let me pull that up... Okay, I have Robert Williams here. How can I help you today?"
> *Bot asks about eligibility/benefits verification for CPT 27447*
---

### Plan Information

**Insurance Representative**
"Let me check... That facility is **non-par**."
> *If bot asks to clarify:* "Right, they're not contracted with us. Not participating."
> *Bot should recognize non-par = Out-of-Network*
> *Bot should record: network_status=Out-of-Network*
---
**Insurance Representative**
*(When asked about plan type)*
"This is an HMO plan."
> *Bot should record: plan_type=HMO*
---
**Insurance Representative**
*(When asked about effective date)*
"July first, twenty twenty four."
> *Bot should record: plan_effective_date=07/01/2024*
---
**Insurance Representative**
*(When asked about term date)*
"Term date is June thirtieth, twenty twenty five."
> *Bot should record: plan_term_date=06/30/2025*
---

### CPT Coverage Details

**Insurance Representative**
*(When asked about coverage for CPT 27447)*
"What's the date of service for this procedure?"
> *Bot provides date*
"Let me check the non-par benefits for that code... The code is covered under non-par benefits. No copay, but the member's responsibility is forty percent coinsurance. The separate deductible for non-participating providers does apply. You'll need prior auth for this."
> *Bot should record:*
> - *cpt_covered=Yes*
> - *copay_amount=None*
> - *coinsurance_percent=40*
> - *deductible_applies=Yes*
> - *prior_auth_required=Yes*
---
**Insurance Representative**
*(When asked about telehealth)*
"Telehealth isn't available for this type of procedure."
> *Bot should record: telehealth_covered=No*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about individual deductible)*
"For the non-par side, the individual deductible is twenty-five hundred. Nothing's been applied to the non-par accumulators yet."
> *Bot should record:*
> - *deductible_individual=2500.00*
> - *deductible_individual_met=0.00*
---
**Insurance Representative**
*(When asked about individual out-of-pocket max)*
"The individual non-par OOP max is ten thousand. Zero applied so far on the non-par side."
> *Bot should record:*
> - *oop_max_individual=10000.00*
> - *oop_max_individual_met=0.00*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family deductible)*
"Family non-par deductible is five thousand. Nothing applied on the family side either."
> *Bot should record:*
> - *deductible_family=5000.00*
> - *deductible_family_met=0.00*
---
**Insurance Representative**
*(When asked about family out-of-pocket max)*
"Family non-par OOP max is twenty thousand, also zero applied."
> *Bot should record:*
> - *oop_max_family=20000.00*
> - *oop_max_family_met=0.00*
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"Reference number is BCBS-OON-2025-1234."
> *Bot should record: reference_number=BCBS-OON-2025-1234*
---
**Insurance Representative**
*(When bot wraps up)*
"Anything else I can help with? Alright, have a good day."
> *Bot should say goodbye and end call*

---
## Verification Checklist
After the call, verify the bot collected these values correctly:

### Plan Information
| Field | Expected Value |
|-------|----------------|
| Network Status | Out-of-Network |
| Plan Type | HMO |
| Effective Date | 07/01/2024 |
| Term Date | 06/30/2025 |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | Yes |
| Copay | None |
| Coinsurance | 40 |
| Deductible Applies | Yes |
| Telehealth Covered | No |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 2500.00 |
| Individual Deductible Met | 0.00 |
| Individual OOP Max | 10000.00 |
| Individual OOP Met | 0.00 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 5000.00 |
| Family Deductible Met | 0.00 |
| Family OOP Max | 20000.00 |
| Family OOP Met | 0.00 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Diana |
| Reference Number | BCBS-OON-2025-1234 |
