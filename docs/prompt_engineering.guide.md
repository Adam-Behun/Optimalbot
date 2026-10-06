### Prompt Engineering Best Practices (Apply to ALL Nodes)

The following principles from enterprise conversational AI must be applied to every node:

#### 1. Separate Instructions into Clean Sections

Use markdown headings within task_messages to help the model prioritize instructions:

```python
task_messages=[{
    "role": "system",
    "content": """# Goal
Gather basic plan information from the representative.

# Questions to Ask
Ask these questions naturally, one at a time...

# Response Handling
When the rep answers, record the information immediately...

# Edge Cases
If put on hold: "Thank you, I'll wait."
If info unavailable: record as "Unknown" and continue."""
}]
```

#### 2. Be Concise - Remove Filler Words

Every instruction should be short, clear, and action-based.

**Less effective:**
```
When the representative tells you about the network status, you should carefully listen to what they say and then make sure to call the record_network_status function with the appropriate value based on their response.
```

**Recommended:**
```
When rep confirms network status → call record_network_status immediately.
```

#### 3. Emphasize Critical Instructions

Add "This step is important." at the end of critical lines. Repeat the most important 1-2 instructions.

```python
"""# Goal
Record each piece of information IMMEDIATELY when the rep provides it. This step is important.
Never track information in memory—always call the recording function right away.

# Guardrails
Record information immediately via function calls. This step is important."""
```

#### 4. Character Normalization (Spoken vs Written Formats)

Insurance reps speak dollar amounts and percentages naturally. Define how to normalize these:

```python
"""# Data Normalization

**Dollar amounts** (spoken → written):
- "fifty dollars" or "50 dollars" → "$50"
- "one thousand one hundred seventy dollars and seventy four cents" → "$1,170.74"
- "five hundred" → "$500"

**Percentages** (spoken → written):
- "twenty percent" or "20 percent" → "20%"
- "zero percent" → "0%"
- "eighty percent coinsurance" → "80%"

**Dates** (spoken → written):
- "January first twenty twenty five" → "01/01/2025"
- "oh one oh one twenty five" → "01/01/2025"

Always convert to written format before calling recording functions."""
```

#### 5. Provide Clear Examples

Include examples of natural conversation flow:

```python
"""# Example Conversation Flow

You: "Is Example Sleep Clinic participating in the network?"
Rep: "Yes, for checking this facility is in network."
→ call record_network_status with "In-Network"

You: "What type of plan is this? PPO, HMO, or POS?"
Rep: "It's a POS plan."
→ call record_plan_type with "POS"

You: "What is the copay for this service?"
Rep: "That would be fifty dollars per service."
→ call record_copay with "$50"

You: "Is there a coinsurance?"
Rep: "No coinsurance for this service."
→ call record_coinsurance with "None" """
```

#### 6. Dedicate a Guardrails Section

Models pay extra attention to `# Guardrails` headings:

```python
"""# Guardrails

- NEVER guess or assume information—only record what the rep explicitly states.
- NEVER track information in memory—call the recording function immediately.
- If the rep is unclear, ask for clarification: "I'm sorry, could you repeat that?"
- If information is unavailable, record as "Unknown" and continue.
- Stay on topic—only ask eligibility/benefits questions."""
```

#### 7. Describe Tools Precisely with When/How/Error Guidance

Function descriptions should explain WHEN to use them:

```python
FlowsFunctionSchema(
    name="record_copay",
    description="""Record copay amount when rep states it.

WHEN TO USE: After rep provides copay information.
HOW TO FORMAT: Convert spoken amount to written format (e.g., "fifty dollars" → "$50").
VALID VALUES: Dollar amount (e.g., "$50"), "None", "Unknown", "N/A".

EXAMPLES:
- Rep says "fifty dollars per service" → call with "$50"
- Rep says "no copay" → call with "None"
- Rep says "I don't have that information" → call with "Unknown" """,
    properties={
        "amount": {
            "type": "string",
            "description": "Copay amount in written format: '$50', 'None', or 'Unknown'"
        }
    },
    required=["amount"],
    handler=self._record_copay_handler
)
```

#### 8. Handle Tool Call Failures Gracefully

Include error handling in prompts:

```python
"""# Error Handling

If recording fails (you get an error message):
1. Acknowledge internally but don't mention to rep
2. Continue with the next question
3. The system will retry

If you miss information:
- Ask the rep to repeat: "I'm sorry, could you say that again?"
- Never guess or make up values"""
```

---

## Flow Definition Code Organization

These principles reduce code size, improve maintainability, and make flows easier to understand.

### 1. Configuration as Class Constants

Move static configuration (workflow mappings, phone numbers, etc.) to class-level constants. This makes configuration visible and easy to modify.

```python
# Before: buried in handler method
async def _route_to_workflow_handler(self, args, flow_manager):
    flow_classes = {
        "scheduling": ("clients.demo_clinic_alpha.patient_scheduling.flow_definition", "PatientSchedulingFlow"),
        "lab_results": ("clients.demo_clinic_alpha.lab_results.flow_definition", "LabResultsFlow"),
    }
    ...

# After: class-level constant
class MainlineFlow:
    WORKFLOW_FLOWS = {
        "scheduling": ("clients.demo_clinic_alpha.patient_scheduling.flow_definition", "PatientSchedulingFlow"),
        "lab_results": ("clients.demo_clinic_alpha.lab_results.flow_definition", "LabResultsFlow"),
    }

    async def _route_to_workflow_handler(self, args, flow_manager):
        if workflow not in self.WORKFLOW_FLOWS:
            ...
        module_path, class_name = self.WORKFLOW_FLOWS[workflow]
```

### 2. Inline Single-Use Nodes

If a node creator is only called from one place and is simple (<10 lines), inline it. This reduces indirection and makes the code flow clearer.

```python
# Before: separate method for simple node
def _create_end_node(self) -> NodeConfig:
    return NodeConfig(
        name="end",
        task_messages=[{"role": "system", "content": "Say a brief goodbye."}],
        functions=[],
        post_actions=[{"type": "end_conversation"}],
    )

async def _end_call_handler(self, args, flow_manager):
    # ... business logic ...
    return None, self._create_end_node()

# After: inline the node
async def _end_call_handler(self, args, flow_manager):
    # ... business logic ...
    return None, NodeConfig(
        name="end",
        task_messages=[{"role": "system", "content": "Say a brief goodbye."}],
        functions=[],
        post_actions=[{"type": "end_conversation"}],
    )
```

**When to inline:**
- Node is used in exactly one place
- Node has no complex logic (just returns a NodeConfig)
- Node is less than 10 lines

**When NOT to inline:**
- Node is used in multiple places (extract to method)
- Node has conditional logic or parameters
- Node is complex enough to benefit from a descriptive name

### 3. Extract Reusable Schemas

When the same function schema appears in multiple nodes (e.g., `end_call` in greeting and transfer_failed), extract it to a helper method.

```python
# Before: duplicated in two nodes
def create_greeting_node(self):
    return NodeConfig(
        functions=[
            FlowsFunctionSchema(
                name="end_call",
                description="End the call when caller says goodbye.",
                properties={},
                required=[],
                handler=self._end_call_handler,
            ),
            # ... other functions
        ]
    )

def create_transfer_failed_node(self):
    return NodeConfig(
        functions=[
            FlowsFunctionSchema(
                name="end_call",
                description="End the call when caller says goodbye.",  # Duplicated!
                properties={},
                required=[],
                handler=self._end_call_handler,
            ),
        ]
    )

# After: extracted helper
def _end_call_schema(self) -> FlowsFunctionSchema:
    return FlowsFunctionSchema(
        name="end_call",
        description="End the call when caller says goodbye.",
        properties={},
        required=[],
        handler=self._end_call_handler,
    )

def create_greeting_node(self):
    return NodeConfig(functions=[..., self._end_call_schema()])

def create_transfer_failed_node(self):
    return NodeConfig(functions=[..., self._end_call_schema()])
```

### 4. Keep Dict References in Constructor

Don't extract every field from a dict into separate instance variables. Keep the dict reference and access fields where needed.

```python
# Before: 7 lines of repetitive extraction
self.office_hours = practice_info.get("office_hours", "Monday-Friday 8-5")
self.location = practice_info.get("location", "")
self.parking = practice_info.get("parking", "")
self.website = practice_info.get("website", "")
self.new_patient_info = practice_info.get("new_patient_info", "")
self.accepted_insurance = practice_info.get("accepted_insurance", "")
self.wait_times = practice_info.get("wait_times", "")

# After: keep dict reference
self.practice_info = patient_data.get("practice_info", {})

# Access in methods with defaults where needed
def _get_global_instructions(self):
    office_hours = self.practice_info.get("office_hours") or "Monday-Friday 8-5"
```

### 5. Concise Function Descriptions

Function descriptions should be brief. The LLM already has detailed examples in `task_messages`—don't duplicate them in function descriptions.

```python
# Before: 15 lines with redundant examples
FlowsFunctionSchema(
    name="route_to_workflow",
    description="""Route caller to an AI-powered workflow.

WHEN TO USE: Caller asks about scheduling, lab results, or prescriptions.
RESULT: Hands off to specialized AI workflow (no phone transfer).

IMPORTANT:
- Include ALL gathered context in the reason field
- Do NOT say "someone will be with you" - the transition is seamless

EXAMPLES:
- workflow="scheduling", reason="follow-up for back pain, prefers Dr. Chen"
- workflow="lab_results", reason="skin biopsy from last week, caller anxious"
- workflow="prescription_status", reason="lisinopril refill, CVS prior auth issue" """,
    ...
)

# After: 1 line (examples are in task_messages)
FlowsFunctionSchema(
    name="route_to_workflow",
    description="Route to AI workflow. Include ALL context in reason. Transition is seamless.",
    ...
)
```

**Rule of thumb:** If it's in `task_messages`, don't repeat it in function description.

### 6. Consolidate Related Handlers

If two handlers do similar things or one just calls the other, merge them.

```python
# Before: unnecessary indirection
async def _route_to_workflow_handler(self, args, flow_manager):
    workflow = args.get("workflow")
    reason = args.get("reason")
    # ... state updates ...
    return await self._handoff_to_workflow(flow_manager, workflow, reason)

async def _handoff_to_workflow(self, flow_manager, workflow, reason):
    # ... actual handoff logic ...

# After: single handler
async def _route_to_workflow_handler(self, args, flow_manager):
    workflow = args.get("workflow")
    reason = args.get("reason")
    # ... state updates ...
    # ... handoff logic directly here ...
```

### 7. Simplify When Possible

Remove unused parameters and unnecessary complexity.

```python
# Before: department-based routing with 3 options
FlowsFunctionSchema(
    name="request_staff",
    properties={
        "department": {"type": "string", "enum": ["billing", "front_desk", "medical"]},
        "urgent": {"type": "boolean"},
        "patient_confirmed": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    required=["department"],
)

async def _request_staff_handler(self, args, flow_manager):
    department = args.get("department", "front_desk")
    phone_numbers = {
        "billing": config.get("billing_number"),
        "front_desk": config.get("staff_number"),
        "medical": config.get("medical_number"),
    }
    transfer_number = phone_numbers.get(department)
    ...

# After: single staff number (if that's all you need)
FlowsFunctionSchema(
    name="request_staff",
    description="Transfer to human staff.",
    properties={
        "reason": {"type": "string", "description": "Brief reason for transfer"},
    },
    required=["reason"],
)

async def _request_staff_handler(self, args, flow_manager):
    transfer_number = self.cold_transfer_config.get("staff_number")
    ...
```

### 8. Use Comprehensions for Initialization

Replace repetitive initialization with dict comprehensions.

```python
# Before: 6 lines
def _init_state(self):
    self.flow_manager.state["caller_name"] = ""
    self.flow_manager.state["call_type"] = ""
    self.flow_manager.state["call_reason"] = ""
    self.flow_manager.state["routed_to"] = ""
    self.flow_manager.state["resolution"] = ""

# After: 2 lines
def _init_state(self):
    self.flow_manager.state.update({k: "" for k in [
        "caller_name", "call_type", "call_reason", "routed_to", "resolution"
    ]})
```

### 9. Method Organization

Group methods by purpose using section headers:

```python
class MyFlow:
    # ==================== Class Constants ====================
    WORKFLOW_FLOWS = {...}

    # ==================== Initialization ====================
    def __init__(self, ...): ...
    def _init_state(self): ...

    # ==================== Helpers: Normalization ====================
    def _normalize_name(self, name: str) -> str: ...
    def _normalize_dob(self, dob: str) -> str | None: ...
    def _normalize_phone(self, phone: str) -> str: ...
    def _phone_last4(self, phone: str) -> str: ...
    async def _try_db_update(self, patient_id, method, *args, error_msg): ...
    async def _update_phone_number(self, new_number, flow_manager) -> str: ...

    # ==================== Helpers: Prompts ====================
    def _get_global_instructions(self) -> str: ...

    # ==================== Helpers: Function Schemas ====================
    def _end_call_schema(self) -> FlowsFunctionSchema: ...
    def _request_staff_schema(self) -> FlowsFunctionSchema: ...
    def _route_to_workflow_schema(self) -> FlowsFunctionSchema: ...

    # ==================== Node Creators: Entry Points ====================
    def create_greeting_node(self) -> NodeConfig: ...
    def create_handoff_entry_node(self, context: str = "") -> NodeConfig: ...

    # ==================== Node Creators: Main Flow ====================
    def create_verification_node(self) -> NodeConfig: ...
    def create_results_node(self) -> NodeConfig: ...
    def create_completion_node(self) -> NodeConfig: ...

    # ==================== Node Creators: Utility/Bridge ====================
    def _create_post_workflow_node(self, target_flow, workflow_type, msg) -> NodeConfig: ...

    # ==================== Node Creators: Error/Edge Cases ====================
    def create_verification_failed_node(self) -> NodeConfig: ...
    def create_transfer_failed_node(self) -> NodeConfig: ...

    # ==================== Handlers: Verification ====================
    async def _proceed_to_verification_handler(self, args, flow_manager): ...
    async def _verify_identity_handler(self, args, flow_manager): ...

    # ==================== Handlers: Workflow Routing ====================
    async def _route_to_workflow_handler(self, args, flow_manager): ...

    # ==================== Handlers: Callbacks ====================
    async def _confirm_callback_handler(self, args, flow_manager): ...
    async def _update_callback_number_handler(self, args, flow_manager): ...

    # ==================== Handlers: Transfers ====================
    async def _initiate_sip_transfer(self, flow_manager): ...
    async def _request_staff_handler(self, args, flow_manager): ...
    async def _retry_transfer_handler(self, args, flow_manager): ...

    # ==================== Handlers: End Call ====================
    async def _end_call_handler(self, args, flow_manager): ...
```

### 10. Database Update Helper

Extract repeated try/except database update patterns into a reusable helper:

```python
# Before: repeated 5+ times across handlers
patient_id = flow_manager.state.get("patient_id")
if patient_id:
    try:
        db = get_async_patient_db()
        await db.update_field(patient_id, "identity_verified", True, self.organization_id)
    except Exception as e:
        logger.error(f"Error updating identity_verified: {e}")

# After: single helper, one-line calls
async def _try_db_update(self, patient_id: str, method: str, *args, error_msg: str = "DB update error"):
    if not patient_id:
        return
    try:
        db = get_async_patient_db()
        await getattr(db, method)(patient_id, *args, self.organization_id)
    except Exception as e:
        logger.error(f"{error_msg}: {e}")

# Usage:
await self._try_db_update(patient_id, "update_field", "identity_verified", True, error_msg="Error updating identity_verified")
await self._try_db_update(patient_id, "update_patient", {"callback_confirmed": True}, error_msg="Error updating callback")
await self._try_db_update(patient_id, "update_call_status", "Transferred", error_msg="Error updating call status")
```

### 11. Phone Number Helpers

Extract phone normalization and display patterns:

```python
def _normalize_phone(self, phone: str) -> str:
    """Strip to digits only."""
    return ''.join(c for c in phone if c.isdigit())

def _phone_last4(self, phone: str) -> str:
    """Get last 4 digits for display (e.g., 'ending in 1234')."""
    return phone[-4:] if len(phone) >= 4 else ""
```

When multiple handlers update phone numbers with similar logic, extract a shared helper:

```python
# Before: duplicated in _confirm_callback_handler and _update_callback_number_handler
new_number_digits = self._normalize_phone(new_number)
flow_manager.state["phone_number"] = new_number_digits
logger.info(f"Flow: Callback number updated to {self._phone_last4(new_number_digits)}")
patient_id = flow_manager.state.get("patient_id")
await self._try_db_update(patient_id, "update_patient", {"caller_phone_number": new_number_digits}, ...)

# After: shared helper
async def _update_phone_number(self, new_number: str, flow_manager: FlowManager) -> str:
    new_number_digits = self._normalize_phone(new_number)
    flow_manager.state["phone_number"] = new_number_digits
    logger.info(f"Flow: Callback number updated to {self._phone_last4(new_number_digits)}")
    patient_id = flow_manager.state.get("patient_id")
    await self._try_db_update(patient_id, "update_patient", {"caller_phone_number": new_number_digits}, error_msg="Error updating callback number")
    return new_number_digits

# Usage in handlers:
async def _confirm_callback_handler(self, args, flow_manager):
    new_number_digits = await self._update_phone_number(new_number, flow_manager) if new_number else None
    # ... rest of handler

async def _update_callback_number_handler(self, args, flow_manager):
    new_number_digits = await self._update_phone_number(new_number, flow_manager)
    return f"I've updated your callback number to the one ending in {self._phone_last4(new_number_digits)}.", None
```

### 12. Closures for Bridge Nodes (Avoid Instance Variables)

When creating bridge nodes that hand off to another flow, use closures instead of instance variables:

```python
# Before: instance variables (anti-pattern)
def _create_post_workflow_node(self, target_flow, workflow_type: str, transition_message: str = "") -> NodeConfig:
    self._pending_flow = target_flow           # Stored on self - can be overwritten!
    self._pending_workflow_type = workflow_type
    return NodeConfig(
        name=f"post_{workflow_type}",
        task_messages=[{"role": "system", "content": f"Call proceed_to_{workflow_type} immediately."}],
        functions=[FlowsFunctionSchema(
            name=f"proceed_to_{workflow_type}",
            handler=self._proceed_to_workflow_handler,  # Reads from self later
        )],
    )

async def _proceed_to_workflow_handler(self, args, flow_manager):
    if self._pending_workflow_type == "prescription":
        return None, self._pending_flow.create_status_node()
    return None, self._pending_flow.create_scheduling_node()

# After: closure captures values (safer, no extra method needed)
def _create_post_workflow_node(self, target_flow, workflow_type: str, transition_message: str = "") -> NodeConfig:
    async def proceed_handler(args, flow_manager):
        if workflow_type == "prescription":
            return None, target_flow.create_status_node()
        return None, target_flow.create_scheduling_node()

    return NodeConfig(
        name=f"post_{workflow_type}",
        task_messages=[{"role": "system", "content": f"Call proceed_to_{workflow_type} immediately."}],
        functions=[FlowsFunctionSchema(
            name=f"proceed_to_{workflow_type}",
            description=f"Proceed to {workflow_type}.",
            properties={},
            required=[],
            handler=proceed_handler,  # Closure captures target_flow and workflow_type
        )],
        respond_immediately=True,
        pre_actions=[{"type": "tts_say", "text": transition_message}] if transition_message else None,
    )
```

**Why closures are better:**
- Each call creates its own isolated handler with captured values
- No risk of values being overwritten if method is called twice
- No need for a separate handler method
- Values are captured at node creation time, not lookup time

### 13. Conditional Info Building with Comprehensions

When building optional info sections for prompts, use comprehensions:

```python
# Before: 8 lines
practice_facts = []
if office_hours:
    practice_facts.append(f"- Office hours: {office_hours}")
if location:
    practice_facts.append(f"- Location: {location}")
if parking:
    practice_facts.append(f"- Parking: {parking}")
practice_info_text = "\n".join(practice_facts) if practice_facts else "- Contact the front desk"

# After: 2 lines
facts = [(k, v) for k, v in [("Office hours", office_hours), ("Location", location), ("Parking", parking)] if v]
practice_info_text = "\n".join(f"- {k}: {v}" for k, v in facts) if facts else "- Contact the front desk"
```

For conditional prompt sections:

```python
# Before: 8 lines
results_info = ""
if results_summary:
    results_info = f"""# Lab Results Already Shared
- Test: {test_type}
- Date: {test_date}
- Results: {results_summary}

"""

# After: 1 line (use \n for line breaks in f-string)
results_info = f"# Lab Results Already Shared\n- Test: {test_type}\n- Date: {test_date}\n- Results: {results_summary}\n\n" if results_summary else ""
```

**Caveat:** If a variable is used elsewhere in the prompt (like `{office_hours}` in an example), keep the variable assignment even when using comprehensions.

### Summary Checklist

Before submitting a flow definition, verify:

**Structure & Organization:**
- [ ] Static configuration is in class constants (e.g., `WORKFLOW_FLOWS`)
- [ ] Methods are grouped with section headers (`# ==================== Section ====================`)
- [ ] Single-use simple nodes are inlined in handlers
- [ ] Repeated schemas extracted to helper methods (`_end_call_schema`, `_request_staff_schema`)

**Code Reduction:**
- [ ] Constructor doesn't over-extract from dicts
- [ ] Function descriptions are concise (not duplicating task_messages)
- [ ] No unnecessary handler indirection
- [ ] Unused parameters and complexity removed
- [ ] Initialization uses comprehensions where appropriate
- [ ] Conditional info building uses comprehensions

**Helpers & Patterns:**
- [ ] Database updates use `_try_db_update` helper
- [ ] Phone operations use `_normalize_phone`, `_phone_last4`, `_update_phone_number`
- [ ] Bridge nodes use closures instead of instance variables
- [ ] Shared logic between handlers is extracted to helpers
