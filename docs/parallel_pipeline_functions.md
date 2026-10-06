# Parallel Pipeline for Function Calls

## Problem

When the insurance rep provides multiple data points in one response:

> "thirty dollar copay, no coinsurance, no deductible applies, no prior auth, telehealth covered"

The bot loops, asking the same follow-up question 6 times.

## Root Cause

1. LLM calls 6 `record_*` functions simultaneously
2. Each function returns `(None, None)` meaning "stay on current node"
3. **pipecat-flows forces `run_llm=True`** for each "node function"
4. This triggers 6 separate LLM completions instead of 1

Pipecat's default behavior is smart - it waits for ALL functions to complete before running LLM once. But pipecat-flows overrides this by explicitly setting `run_llm=True` for functions that don't transition to a new node.

## Solution

Two LLMs running in parallel:

| LLM | Role | Functions |
|-----|------|-----------|
| **Extraction LLM** | Silent, captures data | All `record_*` functions |
| **Conversation LLM** | Speaks to rep | Only transition functions (`proceed_to_*`, `end_call`) |

## Architecture

```
              Transcription (from STT)
                       │
              ┌────────┴────────┐
              │  ParallelPipeline │
              │ (ExtractionDetector) │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼                           ▼
┌─────────────────┐       ┌─────────────────┐
│ EXTRACTION      │       │ MAIN BRANCH     │
│ (silent)        │       │ (pass-through)  │
│                 │       │                 │
│ • extraction_llm│       │                 │
│ • record_*      │       │                 │
│ • updates state │       │                 │
│ • NO TTS output │       │                 │
└─────────────────┘       └─────────────────┘
         │                           │
         └─────────────┬─────────────┘
                       ▼
              ┌────────────────┐
              │ CONVERSATION   │
              │ • main_llm     │
              │ • reads state  │
              │ • asks questions│
              │ • TTS output   │
              └────────────────┘
```

## Why This Works

- **Extraction LLM** registers functions directly with Pipecat (not through pipecat-flows), so it uses Pipecat's default batching: run LLM once after ALL functions complete
- **Conversation LLM** only has transition functions, so no batching issues
- State is shared via `flow_manager.state` - extraction writes, conversation reads
- No race condition: function handlers are fast (in-memory + async DB), LLM latency (~500ms) dominates

## Implementation

Following the existing `TriageDetector` pattern:

1. **ExtractionDetector** - extends `ParallelPipeline` with own context aggregator
2. **ExtractionSilencer** - absorbs text frames (no TTS output from extraction)
3. **ExtractionUpstreamGate** - blocks `FunctionCallResultFrame` from polluting main context
4. Register extraction functions directly with extraction LLM (bypasses pipecat-flows)
5. Remove `record_*` from conversation node configs

## Key Files

| File | Purpose |
|------|---------|
| `pipeline/extraction_detector.py` | New ParallelPipeline for extraction |
| `pipeline/extraction_processors.py` | Silencer and UpstreamGate |
| `pipeline/pipeline_factory.py` | Wire up extraction branch |
| `flow_definition.py` | Split functions between extraction and conversation |

## References

- `pipeline/triage_detector.py` - existing parallel LLM pattern to follow
- `pipeline/triage_processors.py` - gate patterns
- Pipecat docs: [ParallelPipeline](https://docs.pipecat.ai/server/pipeline/parallel-pipeline)
