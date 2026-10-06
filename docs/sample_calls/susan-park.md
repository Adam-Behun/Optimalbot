# Demo Call Script
**Patient:** Susan Park (Date of Birth: 04/18/1990)

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
"Cigna provider line, this is Kevin. How can I help you today?"
> *Bot introduces itself and facility (Family Health Clinic)*
> *Bot should record: insurance_rep_first_name=Kevin*
---
**Insurance Representative**
"Thanks. Can I get the tax ID for the facility?"
> *Bot provides: 22-3344556*
---
**Insurance Representative**
"And you said the facility name is Family Health Clinic?"
> *Bot confirms*
---
**Insurance Representative**
"Great. And the member's name?"
> *Bot provides: Susan Park*
---
**Insurance Representative**
"Susan Park. And the date of birth?"
> *Bot provides: 04/18/1990*
---
**Insurance Representative**
"April eighteenth, nineteen ninety. Let me pull that up..."
> *Bot should wait*
---
**Insurance Representative**
"Okay, I have Susan here. And you're calling about eligibility verification?"
> *Bot confirms*
---

### Plan Information

**Insurance Representative**
"Alright. Is the provider in network? Let me check... Yes, Family Health Clinic is in network."
> *Bot should record: network_status=In-Network*
---
**Insurance Representative**
"Are you looking for the plan type as well?"
> *Bot confirms*
---
**Insurance Representative**
"This is an EPO plan. Effective February first twenty twenty five. No termination date on file."
> *Bot should record: plan_type=EPO, plan_effective_date=02/01/2025, plan_term_date=None*
---

### CPT Coverage Details

**Insurance Representative**
"What CPT code are you looking at?"
> *Bot provides: 99213*
---
**Insurance Representative**
"Ninety-nine two thirteen. And what's the date of service?"
> *Bot provides date (or says not yet determined)*
---
**Insurance Representative**
"That's okay, I can use today's date. And the place of service?"
> *Bot provides: Office*
---
**Insurance Representative**
"Office visit. Let me check the benefits..."
> *Bot should wait*
---
**Insurance Representative**
"Okay, that code is covered."
> *Bot should record: cpt_covered=Yes*
---
**Insurance Representative**
"The copay is forty dollars."
> *Bot should record: copay_amount=40.00*
---
**Insurance Representative**
"Coinsurance is ten percent."
> *Bot should record: coinsurance_percent=10*
---
**Insurance Representative**
"Deductible does not apply for this service."
> *Bot should record: deductible_applies=No*
---
**Insurance Representative**
*(When asked about prior auth)*
"No prior authorization required for this code."
> *Bot should record: prior_auth_required=No*
---
**Insurance Representative**
*(When asked about telehealth)*
"Yes, telehealth is covered with the same benefits."
> *Bot should record: telehealth_covered=Yes*
---

### Individual Accumulators

**Insurance Representative**
"Do you need the deductible and out-of-pocket information as well?"
> *Bot confirms*
---
**Insurance Representative**
"Sure. The individual deductible is three hundred seventy-five dollars, also fully met. Individual out-of-pocket max is twenty-five hundred, with nine hundred applied."
> *Bot should record:*
> - *deductible_individual=375.00*
> - *deductible_individual_met=375.00*
> - *oop_max_individual=2500.00*
> - *oop_max_individual_met=900.00*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family accumulators)*
"The family deductible is seven hundred fifty dollars, and it's been fully met. The family out-of-pocket max is five thousand, with eighteen hundred applied so far."
> *Bot should record:*
> - *deductible_family=750.00*
> - *deductible_family_met=750.00*
> - *oop_max_family=5000.00*
> - *oop_max_family_met=1800.00*
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"Let me get that for you... The reference number is CIG-2025-CLR-4567."
> *Bot should record: reference_number=CIG-2025-CLR-4567*
---
**Insurance Representative**
"Is there anything else I can help with today?"
> *Bot says no*
"Alright, have a great day!"
> *Bot should say goodbye and end call*

---
## Verification Checklist
After the call, verify the bot collected these values correctly:

### Plan Information
| Field | Expected Value |
|-------|----------------|
| Network Status | In-Network |
| Plan Type | EPO |
| Effective Date | 02/01/2025 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | No |
| Copay | 40.00 |
| Coinsurance | 10 |
| Deductible Applies | No |
| Telehealth Covered | Yes |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 375.00 |
| Individual Deductible Met | 375.00 |
| Individual OOP Max | 2500.00 |
| Individual OOP Met | 900.00 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 750.00 |
| Family Deductible Met | 750.00 |
| Family OOP Max | 5000.00 |
| Family OOP Met | 1800.00 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Kevin |
| Reference Number | CIG-2025-CLR-4567 |
