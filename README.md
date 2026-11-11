# OptimalBot Portal

Voice AI agent for healthcare phone calls: it places outbound calls to insurance payers for eligibility verification and answers inbound patient calls for scheduling, prescription status, and lab results, navigating phone trees and handing off to staff, plus a web portal to run and review calls.

Portfolio project. Code is shared to show the architecture and eval design; running it requires your own API keys.

## Architecture

### How a call starts

```mermaid
%%{init: {'flowchart': {'wrappingWidth': 420}}}%%
flowchart TB
    Portal["React portal"]
    Payer["Insurance payer line"]
    Patient["Patient"]

    API["FastAPI backend<br/>/start-call · /dialin-webhook<br/>patients · sessions · auth"]
    Daily["Daily telephony<br/>rooms · SIP dial-out<br/>dial-in webhook · SIP transfer"]
    Cloud["Pipecat Cloud<br/>(production)"]
    Clients["clients/&lt;org&gt;/&lt;workflow&gt;/<br/>flow_definition.py<br/>services.yaml · schema.py"]

    Bot["Bot — bot.py / CallSession<br/>builds and runs the<br/>Pipecat pipeline"]

    DB[("MongoDB<br/>organizations · patients<br/>sessions · audit logs")]
    Langfuse["Langfuse /<br/>OpenTelemetry"]

    Portal -- "start a call" --> API
    Payer <--> Daily
    Patient <--> Daily
    Daily -- "dial-in webhook" --> API
    API <--> DB

    API -- "start bot (local)" --> Bot
    API -. "production" .-> Cloud -.-> Bot
    Clients -. "FlowLoader +<br/>PipelineFactory" .-> Bot

    Bot <--> Daily
    Bot -- "transcript, usage,<br/>patient fields, call status" --> DB
    Bot -. "traces" .-> Langfuse

    classDef bot fill:#dcefe1,stroke:#2f6b47,stroke-width:2px,color:#10301f
    classDef infra fill:#e6eaf8,stroke:#41519e,stroke-width:1.5px,color:#151d45
    class Bot bot
    class Portal,Payer,Patient,API,Daily,Cloud,Clients,DB,Langfuse infra
```

A call starts when the portal posts to `/start-call` (dial-out) or Daily posts to `/dialin-webhook/{organization}/{workflow}` (dial-in). The backend checks the workflow is enabled for the organization, creates a session record, and starts the bot — a local process in development, Pipecat Cloud in production — passing the workflow name and the patient record. `FlowLoader` and `PipelineFactory` build the call from that workflow's own `flow_definition.py` and `services.yaml`. When the call ends, the bot writes the transcript, token and telephony usage, extracted patient fields, and final call status back to MongoDB.

### Inside the bot: the Pipecat pipeline

```mermaid
%%{init: {'flowchart': {'wrappingWidth': 520}}}%%
flowchart TB
    In["Daily transport in — caller audio"]
    STT["STT · Deepgram Flux — per-workflow EOT thresholds, payer keyterms"]
    Safety["Safety monitor · Groq Llama Guard (optional per workflow)"]
    Triage["Triage · Groq classifier — CONVERSATION / IVR / VOICEMAIL (dial-out only)"]

    LLM["Conversation LLM · OpenAI<br/>driven by Pipecat Flows nodes<br/>calls flow-control functions only"]
    IVRNav["IVR navigation — parses &lt;dtmf&gt; / &lt;ivr&gt; tags out of LLM output"]
    TTS["Output validator → TTS · Cartesia"]

    Obs["Observer LLM · OpenAI<br/>rolling 10-turn window, extracts<br/>23 eligibility fields (eligibility only)"]
    Null["NullFilter — observer can never speak"]

    Out["Daily transport out — bot audio"]

    In --> STT --> Safety --> Triage
    Triage --> LLM --> IVRNav --> TTS --> Out
    Triage -. "voicemail or stuck IVR ends the call" .-> Out
    TTS -. "bot speech via Producer → Consumer" .-> Obs
    Triage -. "caller speech" .-> Obs
    Obs --> Null

    classDef conv fill:#dcefe1,stroke:#2f6b47,stroke-width:2px,color:#10301f
    classDef observer fill:#fbeccd,stroke:#8a5d12,stroke-width:2px,color:#3d2906
    classDef infra fill:#e6eaf8,stroke:#41519e,stroke-width:1.5px,color:#151d45
    class LLM,IVRNav,TTS conv
    class Obs,Null observer
    class In,Out,STT,Safety,Triage infra
```

Every workflow shares the same frame pipeline, assembled per workflow from `services.yaml`: Deepgram Flux speech-to-text, an OpenAI LLM driven by Pipecat Flows nodes, and Cartesia text-to-speech over a Daily room. Dial-out calls add a Groq triage classifier and IVR navigation in front of the conversation; dial-in calls go straight to the flow. The eligibility workflow adds a second, silent LLM in a parallel branch that extracts structured fields while the call is still running — it receives the caller's speech directly and the bot's speech through a producer/consumer pair, and a `NullFilter` at the end of the branch makes it impossible for it to emit audio.

## Workflows

Defined for the demo organization in `clients/demo_clinic_alpha`. Every call writes its transcript and call status to a session record in MongoDB.

- **eligibility_verification (dial-out).** Calls an insurance payer, classifies the answer as person, phone menu, or voicemail, navigates menus, and leaves a callback message on voicemail. With a representative it collects plan, network, date, coverage, deductible, and reference number details, which a silent observer LLM extracts into the patient record.
- **patient_scheduling (dial-in).** Handles new and returning patients (date-of-birth check), offers two generated appointment slots, and confirms the booking. Logs appointment fields on the patient record.
- **prescription_status (dial-in).** Verifies the caller, then reads the stored status of a GLP-1 prescription and can record a refill or renewal request. Safety monitoring is on. Logs refill and renewal flags.
- **lab_results (dial-in).** Verifies the caller, reads a stored summary only when results are ready, and otherwise confirms a callback. Safety monitoring is on. Logs whether results were communicated and the callback number.
- **mainline (dial-in).** Answers practice questions from configured facts, routes callers to the other workflows within the same call, and transfers other requests to staff. Logs caller name, reason, and where the call was routed.

`clients/demo_clinic_beta` has one more patient_scheduling workflow, to show a second organization with its own prompts.

## Evaluation

Scenario evals live in `evals/<org>/<workflow>/` (a `run.py` and a `scenarios.yaml` each) and test conversation logic in text, with no audio or telephony. A run seeds a synthetic patient into a test MongoDB database, loads the workflow's real flow class, and lets a simulated caller (`gpt-4o-mini`) follow the scenario's persona against it. Function handlers run for real against the test database. Graders then score the result: rule checks (node reached, database state, safety detection, forbidden phrases, extracted data) and Claude LLM judges (conversation quality, HIPAA behavior, routing). Triage evals under `evals/demo_clinic_alpha/eligibility_verification/triage/` test greeting classification and IVR navigation separately. `evals/ivr_deprecated` is retired.

Workflow evals need `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and a MongoDB instance (`MONGO_URI`); Langfuse keys are optional. Each `run.py` supports `--list` (no API calls), `--scenario <id>`, `--all`, `-v`, and `--sync-dataset`.

## Multi-tenant design

An organization is a folder under `clients/` plus a document in the MongoDB `organizations` collection. A workflow is a subfolder with a `flow_definition.py` (a class named after the folder, which `FlowLoader` finds by convention), a `services.yaml` with `${VAR}` placeholders for keys, and a `schema.py` describing its fields for the portal. `python scripts/new_client.py --org-slug <slug> --workflow-name <name> --flow-type dialin|dialout` scaffolds the folder.

## Setup and deployment

Requires Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), Node.js 20, and MongoDB. Running calls needs your own API keys; `.env.example` lists every variable.

```bash
cp .env.example .env
./setup-local.sh                  # creates .venv with uv
cd frontend && npm install

source .venv/bin/activate
ENV=local python app.py           # backend, port 8000
ENV=local python bot.py           # bot, port 7860
cd frontend && npm run dev        # portal, port 3000
```

Deployment is in `deploy.sh`: the backend to Fly.io, the bot (Docker image) to Pipecat Cloud, and the frontend with `cd frontend && vercel --prod`.

```bash
./deploy.sh test                  # backend and bot to the test environment
./deploy.sh prod backend          # one component to production
```

## Data

All patient data in this repository is synthetic.
