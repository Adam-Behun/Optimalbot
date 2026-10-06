# CLAUDE.md

Notes for working in this repository. See README.md for the overview.

## Commands

```bash
./setup-local.sh                  # creates .venv with uv; also regenerates the uv.*.lock files (uv lock --upgrade)
cd frontend && npm install        # frontend dependencies

ENV=local python app.py           # backend, port 8000
ENV=local python bot.py           # local bot server, port 7860
cd frontend && npm run dev        # portal, port 3000

./run.sh                          # validate.py, reset eval patients, start backend, bot, frontend and ../marketing
python validate.py --quick        # check environment variables and config files

ruff check .                      # lint (CI)
pyright                           # type check (CI)
cd frontend && npm run type-check && npm run build   # frontend checks (CI)
```

`run.sh` also starts a marketing site from `../marketing`, which is not part of this repository, and exits if its `node_modules` is missing. Start the three services by hand if you do not have it.

Deployment is in `deploy.sh`: backend to Fly.io, bot (Docker image) to Pipecat Cloud. The frontend deploys with `cd frontend && vercel --prod`.

## Environment

- `ENV=local`: the backend starts calls by posting to the local bot at `LOCAL_BOT_URL` (default `http://localhost:7860`) and creates the Daily room itself.
- `ENV=production` (or `test`): the backend starts calls through the Pipecat Cloud API and requires `PIPECAT_API_KEY`.
- `.env.example` lists every variable the code reads. The backend requires `JWT_SECRET_KEY` (at least 32 characters), `MONGO_URI`, and `ALLOWED_ORIGINS`.
- Every `services.yaml` uses `${VAR}` placeholders for OPENAI, DEEPGRAM, CARTESIA, DAILY, and `DAILY_PHONE_NUMBER_ID`. The eligibility, lab results, and prescription status configs also use GROQ. `PipelineFactory` raises if a placeholder variable is unset.

## Stack

- Backend: FastAPI, MongoDB (Motor)
- Frontend: React, TypeScript, Vite, Tailwind, Shadcn/Radix
- Voice: Pipecat and Pipecat Flows, Daily (rooms, telephony, SIP transfer)
- Services: OpenAI (conversation LLM and observer LLM), Groq (triage classifier, Llama Guard safety checks), Deepgram Flux (STT), Cartesia (TTS)
- Observability: OpenTelemetry and Langfuse, both optional

## Key files

| Purpose | Location |
|---------|----------|
| Flow definitions | `clients/<org>/<workflow>/flow_definition.py` |
| Service configs | `clients/<org>/<workflow>/services.yaml` |
| Workflow field schemas for the portal | `clients/<org>/<workflow>/schema.py` |
| Shared flow base classes | `clients/demo_clinic_alpha/dialin_base_flow.py`, `dialout_base_flow.py` |
| Flow class lookup | `core/flow_loader.py` |
| Pipeline assembly | `pipeline/pipeline_factory.py` |
| Call session setup and cleanup | `pipeline/session.py` |
| IVR and voicemail triage | `pipeline/triage_detector.py`, `ivr_navigation_processor.py`, `ivr_human_detector.py` |
| Safety monitor and output validator | `pipeline/safety_processors.py`, `handlers/safety.py` |
| Transport, transcript, triage handlers | `handlers/` |
| Start-call endpoint | `backend/api/dialout.py` |
| Dial-in webhook | `backend/api/dialin.py` |
| Starting the bot (local and Pipecat Cloud) | `backend/server_utils.py` |
| Patient and session models | `backend/models/patient.py`, `backend/sessions.py` |
| Call status values | `backend/constants.py` |
| Evals | `evals/<org>/<workflow>/run.py` and `scenarios.yaml` |

## Call types

**Dial-out.** The portal calls `POST /start-call`. The backend checks the workflow is enabled for the organization, creates a session, and starts the bot with `dialout_targets` in the body. When the bot joins the Daily room, `DialoutManager` calls `transport.start_dialout()`, with up to three attempts.

**Dial-in.** Daily posts to `/dialin-webhook/{client_name}/{workflow_name}`. The backend creates a session and starts the bot with `dialin_settings` (`call_id`, `call_domain`, `from`, `to`). When the first participant joins, the flow starts at `get_initial_node()`. The flow looks the patient up by phone number and verifies date of birth.

## Flow architecture

`FlowLoader` imports `clients.<org>.<workflow>.flow_definition` and uses the class named after the workflow folder (`patient_scheduling` becomes `PatientSchedulingFlow`).

A node is a Pipecat Flows `NodeConfig`:

- `name`
- `role_messages` and `task_messages`
- `functions`: LLM-callable `FlowsFunctionSchema` handlers that return `(result, next_node)`; returning `None` as the node stays on the current one
- `pre_actions` and `post_actions`: the actions used in this repo are `tts_say`, `end_conversation`, and `function`
- `respond_immediately`

The dial-out flow (`eligibility_verification`) gets triage in front of the conversation. A Groq classifier labels the first utterances as CONVERSATION, IVR, or VOICEMAIL:

1. Human: the flow starts at `create_greeting_node()`.
2. IVR: `IVRNavigationProcessor` presses keys or speaks to navigate menus, a Groq human detector watches for a person, and when navigation completes the flow starts at `create_greeting_node()`. If navigation gets stuck the call is marked Failed.
3. Voicemail: the configured message is spoken, the call is marked Voicemail, and the call ends.

Dial-in flows (`patient_scheduling`, `prescription_status`, `lab_results`, `mainline`) skip triage. They can hand off to another workflow in the same call with `route_to_workflow`, or transfer to staff through a Daily SIP transfer.

The eligibility flow also runs an observer LLM in a parallel pipeline branch that extracts fields from the conversation into the patient record, with a final extraction pass at the end of the call.

## Adding a client or workflow

```
clients/<org_slug>/<workflow_name>/
    flow_definition.py    # class <WorkflowName>Flow
    services.yaml         # call_type, stt/llm/tts/transport settings, cold_transfer.staff_number
    schema.py             # WORKFLOW_SCHEMA for the portal
```

`python scripts/new_client.py --org-slug <slug> --workflow-name <name> --flow-type dialin|dialout` scaffolds the folder. The organization also needs a MongoDB document with the workflow enabled. `scripts/workflow_schema.py` applies a `schema.py` to the organization document. Add `evals/<org>/<workflow>/` with a `run.py` and `scenarios.yaml`.

New flow nodes: add a `create_<name>_node()` method with its messages and functions, and return it from a handler in another node.

## Evals

Each `run.py` supports `--list`, `--scenario <id>`, `--all`, `-v`, and `--sync-dataset`. Workflow evals seed a synthetic patient into the `alfons_test` database, run the real flow with a simulated caller, and grade the result; they need OpenAI and Anthropic keys and MongoDB. Triage evals live under `evals/demo_clinic_alpha/eligibility_verification/triage/`. `evals/ivr_deprecated` is retired.

## Deepgram Flux settings

STT settings are per workflow in `services.yaml`: `eager_eot_threshold`, `eot_threshold`, `eot_timeout_ms`, and `keyterm`. The eligibility dial-out config uses 0.65 and 0.75 for the first two; the dial-in configs use 0.4 to 0.45 and 0.5 to 0.55. Change them in the workflow's own file.

## Other conventions

- Changes to `pipeline/` or `handlers/` affect every workflow.
- Frontend components come from `frontend/src/components/ui/`; workflow screens are in `frontend/src/components/workflows/`.
- All patient data in the repository is synthetic.
