# Demo Call Script
**Patient:** John Smith (Date of Birth: 03/15/1985)

## PART 1: IVR Navigation

**Insurance - IVR**
"Thank you for calling UnitedHealth Group. For Providers, press 1. For Members, press 2."
> *Bot should press: 1*
---
**Insurance - IVR**
"UnitedHealthcare. For individual and family plans, press 1. For employer-sponsored, press 2. For Medicare and retirement, press 3. For healthcare providers, press 4. For brokers, press 5."
> *Bot should press: 4*
---
**Insurance - IVR**
"Provider services. To continue, please enter your 10-digit NPI number followed by pound."
> *Bot should enter NPI*
---
**Insurance - IVR**
"Thank you. For contracting and credentialing, press 1. For claims and payment, press 2. For clinical programs, press 3. For eligibility and benefits, press 4. For prior authorization, press 5."
> *Bot should press: 4*
---
**Insurance - IVR**
"Eligibility and benefits. For commercial plans, press 1. For Medicare Advantage, press 2. For Medicaid and CHIP, press 3. If you don't know the plan type, press 4."
> *Bot should press: 1*
---
**Insurance - IVR**
"Connecting you to a benefits specialist. Current wait time is 4 minutes."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

**Insurance Representative**
"Provider services, this is Eliza."
> *Bot introduces itself and facility (Example Sleep Clinic)*
> *Bot should record: insurance_rep_first_name=Eliza*
> *Bot should ask for last initial*
---
**Insurance Representative**
"Tax ID and member ID?"
> *Bot provides: Tax ID 82-1234567 and member ID U123456789*
---
**Insurance Representative**
"Okay, they're active. POS plan, in network, effective January first twenty twenty five, no term date. What code are you looking at?"
> *Bot should record: network_status=In-network, plan_type=POS, plan_effective_date=01/01/2025, plan_term_date=None*
> *Bot provides CPT code: 95800*
---

### CPT Coverage Details

**Insurance Representative**
*(When bot provides CPT code)*
"Ninety-five eight hundred, that's covered. Fifty dollar copay, no coinsurance, ded doesn't apply, no auth, telehealth same benefit."
> *Bot should record:*
> - *cpt_covered=Yes*
> - *copay_amount=50.00*
> - *coinsurance_percent=None*
> - *deductible_applies=No*
> - *prior_auth_required=No*
> - *telehealth_covered=Yes*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about individual deductible and OOP)*
"Individual ded two fifty, fully met. Individual OOP max three K, five eighty-five thirty-seven applied."
> *Bot should record:*
> - *deductible_individual=250.00*
> - *deductible_individual_met=250.00*
> - *oop_max_individual=3000.00*
> - *oop_max_individual_met=585.37*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family deductible and OOP)*
"Family ded is five hundred, fully met. OOP max six K, eleven seventy point seven four applied."
> *Bot should record:*
> - *deductible_family=500.00*
> - *deductible_family_met=500.00*
> - *oop_max_family=6000.00*
> - *oop_max_family_met=1170.74*
---

### Reference Number and Closing

**Insurance Representative**
*(When bot finishes asking questions)*
"Anything else?"
> *Bot should say no*
---
**Insurance Representative**
"Reference is UHC-2025-789456. Have a good one."
> *Bot should record: reference_number=UHC-2025-789456*
> *Bot should say goodbye and end call*

---
## Verification Checklist
After the call, verify the bot collected these values correctly:

### Plan Information
| Field | Expected Value |
|-------|----------------|
| Network Status | In-network |
| Plan Type | POS |
| Effective Date | 01/01/2025 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | No |
| Copay | 50.00 |
| Coinsurance | None |
| Deductible Applies | No |
| Telehealth Covered | Yes |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 250.00 |
| Individual Deductible Met | 250.00 |
| Individual OOP Max | 3000.00 |
| Individual OOP Met | 585.37 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 500.00 |
| Family Deductible Met | 500.00 |
| Family OOP Max | 6000.00 |
| Family OOP Met | 1170.74 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Eliza |
| Reference Number | UHC-2025-789456 |
