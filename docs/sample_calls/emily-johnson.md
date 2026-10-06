# Demo Call Script
**Patient:** Emily Johnson (Date of Birth: 02/28/1975)

## PART 1: IVR Navigation

**Insurance - IVR**
"Thank you for calling UnitedHealth Group. For UnitedHealthcare, press 1. For Optum, press 2. For UnitedHealth corporate, press 3."
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
"Commercial plans. Please enter the member ID number followed by pound."
> *Bot should enter member ID*
---
**Insurance - IVR**
"Member found. Emily Johnson, date of birth February 28, 1975. Commercial HMO plan. Press 1 if correct, press 2 if this is not the member you're looking for."
> *Bot should press: 1*
---
**Insurance - IVR**
"For real-time benefit check, press 1. For detailed eligibility including accumulators, press 2. To speak with a benefits specialist, press 3."
> *Bot should press: 3*
---
**Insurance - IVR**
"Connecting you to a benefits specialist. Current wait time is 4 minutes."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

**Insurance Representative**
"UnitedHealthcare provider services, this is Robert. How can I help you?"
> *Bot introduces itself and facility (Advanced Therapy Center)*
> *Bot should record: insurance_rep_first_name=Robert*
---
**Insurance Representative**
"Thank you. Can I get the tax ID for the facility?"
> *Bot provides: 77-8899001*
---
**Insurance Representative**
"And the member's name and date of birth?"
> *Bot provides: Emily Johnson, 02/28/1975*
---
**Insurance Representative**
"Let me pull that up... Okay, I have Emily Johnson here. What do you need today?"
> *Bot asks about eligibility/benefits verification for CPT 97140*
---

### Plan Information

**Insurance Representative**
*(When asked about network status)*
"Yes, Advanced Therapy Center is participating."
> *Bot should record: network_status=In-Network*
---
**Insurance Representative**
*(When asked about plan type)*
"This is an HMO plan."
> *Bot should record: plan_type=HMO*
---
**Insurance Representative**
*(When asked about effective date)*
"Effective September first, twenty twenty four."
> *Bot should record: plan_effective_date=09/01/2024*
---
**Insurance Representative**
*(When asked about term date)*
"No termination date on file."
> *Bot should record: plan_term_date=None*
---

### CPT Coverage Details

**Insurance Representative**
*(When asked about coverage for CPT 97140)*
"Let me check that code... I'm sorry, that procedure is NOT covered under this member's benefit plan. It's a plan exclusion."
> **CRITICAL: CPT 97140 is NOT COVERED. Bot should record this and skip irrelevant benefit questions (copay, coinsurance, prior auth, telehealth).**
> *Bot should record: cpt_covered=No*
---
**Insurance Representative**
*(If bot asks about copay/coinsurance/prior auth/telehealth after being told not covered)*
"Since the code isn't covered, those benefit details don't apply."
> *Bot should NOT ask these questions for a non-covered code*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about individual deductible)*
"Individual deductible is seven fifty, four hundred has been met."
> *Bot should record:*
> - *deductible_individual=750.00*
> - *deductible_individual_met=400.00*
---
**Insurance Representative**
*(When asked about individual out-of-pocket max)*
"Individual out of pocket max is thirty-seven fifty, six hundred applied."
> *Bot should record:*
> - *oop_max_individual=3750.00*
> - *oop_max_individual_met=600.00*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family deductible)*
"The family deductible is fifteen hundred, eight hundred has been met."
> *Bot should record:*
> - *deductible_family=1500.00*
> - *deductible_family_met=800.00*
---
**Insurance Representative**
*(When asked about family out-of-pocket max)*
"Family out of pocket max is seventy-five hundred, twelve hundred applied."
> *Bot should record:*
> - *oop_max_family=7500.00*
> - *oop_max_family_met=1200.00*
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"Reference number is UHC-NC-2025-5432."
> *Bot should record: reference_number=UHC-NC-2025-5432*
---
**Insurance Representative**
*(When bot wraps up)*
"Is there anything else? Alright, have a good day."
> *Bot should say goodbye and end call*

---
## Verification Checklist
After the call, verify the bot collected these values correctly:

### Plan Information
| Field | Expected Value |
|-------|----------------|
| Network Status | In-Network |
| Plan Type | HMO |
| Effective Date | 09/01/2024 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | No (plan exclusion) |
| Prior Auth Required | N/A |
| Copay | N/A |
| Coinsurance | N/A |
| Deductible Applies | N/A |
| Telehealth Covered | N/A |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 750.00 |
| Individual Deductible Met | 400.00 |
| Individual OOP Max | 3750.00 |
| Individual OOP Met | 600.00 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 1500.00 |
| Family Deductible Met | 800.00 |
| Family OOP Max | 7500.00 |
| Family OOP Met | 1200.00 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Robert |
| Reference Number | UHC-NC-2025-5432 |
