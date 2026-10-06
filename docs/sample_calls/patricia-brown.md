# Demo Call Script
**Patient:** Patricia Brown (Date of Birth: 06/12/1988)

## PART 1: IVR Navigation

**Insurance - IVR**
"Thank you for calling Aetna. Your call may be recorded. For faster service, try our mobile app. Press 1 to continue."
> *Bot should press: 1*
---
**Insurance - IVR**
"For English, press 1. Para español, oprima 2. For Mandarin Chinese, press 3."
> *Bot should press: 1*
---
**Insurance - IVR**
"Are you a healthcare provider? Press 1 for yes, press 2 for no."
> *Bot should press: 1*
---
**Insurance - IVR**
"Provider services. Before we continue, please enter your 10-digit NPI followed by pound."
> *Bot should enter NPI*
---
**Insurance - IVR**
"Thank you. Your NPI is registered with Aetna. For eligibility and benefits, press 1. For claims, press 2. For prior auth— [static] —press 3. For credentialing, press 4. For network status, press 5."
> *Bot should press: 1 (eligibility despite minor static)*
---
**Insurance - IVR**
"Eligibility. For commercial plans, press 1. For Medicare Advantage, press 2. For Medicaid, press 3. For student health, press 4. If unsure, press 5."
> *Bot should press: 5 (let them determine plan type)*
---
**Insurance - IVR**
"Enter member ID."
> *Bot should enter member ID: AET556677889*
---
**Insurance - IVR**
"Member located: Aetna PPO plan. Commercial plan. For real-time benefits, press 1. To speak with representative, press 2."
> *Bot should press: 1 (try real-time benefits first)*
---
**Insurance - IVR**
"Active member. In-network benefits: $750 deductible, $483.27 met. Office visits: $45.50 copay. For CPT-specific coverage, enter 5-digit code. For representative, press 0."
> *Bot should enter CPT code: 99215*
---
**Insurance - IVR**
"CPT 99215: Covered. Specialist copay applies. Prior auth: Not required. For another code, enter it now. For auth requirements list, press 1. For representative, press 0."
> *Bot should press: 0 (want to confirm details with representative)*
---
**Insurance - IVR**
"Connecting to a benefits representative. Current wait: 6 minutes. Continue holding, or press 1 for callback."
> *Bot should wait*
---

## PART 2: Human Representative Conversation

**Insurance Representative**
"Thank you for holding. This is Jennifer with Aetna provider services. I see you were checking eligibility for a member. How can I help?"
> *Bot introduces itself and facility (Premier Health Associates)*
> *Bot should record: insurance_rep_first_name=Jennifer*
---
**Insurance Representative**
"Thank you. Can I get the tax ID?"
> *Bot provides: 99-0011223*
---
**Insurance Representative**
"And the member's name and date of birth?"
> *Bot provides: Patricia Brown, 06/12/1988*
---
**Insurance Representative**
"Let me pull that up... Okay, I have Patricia Brown. What do you need?"
> *Bot asks about eligibility/benefits verification for CPT 99215*
---

### Plan Information

**Insurance Representative**
*(When asked about network status)*
"Yes, Premier Health Associates is in network."
> *Bot should record: network_status=In-Network*
---
**Insurance Representative**
*(When asked about plan type)*
"PPO."
> *Bot should record: plan_type=PPO*
---
**Insurance Representative**
*(When asked about effective date)*
"April fifteenth, twenty twenty four."
> *Bot should record: plan_effective_date=04/15/2024*
---
**Insurance Representative**
*(When asked about term date)*
"No termination date."
> *Bot should record: plan_term_date=None*
---

### CPT Coverage Details

**Insurance Representative**
*(When asked about coverage for CPT 99215)*
"What's the date of service?"
> *Bot provides date*
"Let me check ninety-nine two fifteen... That's covered. Forty-five fifty copay, fifteen percent coinsurance, deductible applies, no PA, telehealth is covered."
> *Bot should record:*
> - *cpt_covered=Yes*
> - *copay_amount=45.50*
> - *coinsurance_percent=15*
> - *deductible_applies=Yes*
> - *prior_auth_required=No*
> - *telehealth_covered=Yes*
---

### Individual Accumulators

**Insurance Representative**
*(When asked about deductible)*
"The individual deductible is seven hundred fifty dollars. Four eighty-three twenty-seven has been met."
> **CRITICAL: Precise dollar amounts with cents. Bot must record exactly $483.27 — not rounded.**
> *Bot should record:*
> - *deductible_individual=750.00*
> - *deductible_individual_met=483.27*
---
**Insurance Representative**
*(When asked about out-of-pocket max)*
"Individual out-of-pocket max is forty-five hundred. Two thousand one forty-seven sixty-three has been applied."
> **CRITICAL: Bot must record exactly $2,147.63 — not rounded.**
> *Bot should record:*
> - *oop_max_individual=4500.00*
> - *oop_max_individual_met=2147.63*
---

### Family Accumulators

**Insurance Representative**
*(When asked about family deductible)*
"Family deductible is fifteen hundred. Nine sixty-six fifty-four has been met."
> **CRITICAL: Precise cents. Bot must record exactly $966.54.**
> *Bot should record:*
> - *deductible_family=1500.00*
> - *deductible_family_met=966.54*
---
**Insurance Representative**
*(When asked about family out-of-pocket max)*
"Family out-of-pocket max is nine thousand. Forty-two ninety-five twenty-six has been applied."
> **CRITICAL: Precise cents. Bot must record exactly $4,295.26.**
> *Bot should record:*
> - *oop_max_family=9000.00*
> - *oop_max_family_met=4295.26*
---

### Reference Number and Closing

**Insurance Representative**
*(When asked for reference number)*
"Reference is ATN-2025-EXACT-1234."
> *Bot should record: reference_number=ATN-2025-EXACT-1234*
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
| Effective Date | 04/15/2024 |
| Term Date | None |

### CPT Coverage
| Field | Expected Value |
|-------|----------------|
| CPT Covered | Yes |
| Prior Auth Required | No |
| Copay | 45.50 |
| Coinsurance | 15 |
| Deductible Applies | Yes |
| Telehealth Covered | Yes |

### Individual Accumulators
| Field | Expected Value |
|-------|----------------|
| Individual Deductible | 750.00 |
| Individual Deductible Met | 483.27 |
| Individual OOP Max | 4500.00 |
| Individual OOP Met | 2147.63 |

### Family Accumulators
| Field | Expected Value |
|-------|----------------|
| Family Deductible | 1500.00 |
| Family Deductible Met | 966.54 |
| Family OOP Max | 9000.00 |
| Family OOP Met | 4295.26 |

### Call Metadata
| Field | Expected Value |
|-------|----------------|
| Insurance Rep First Name | Jennifer |
| Reference Number | ATN-2025-EXACT-1234 |
