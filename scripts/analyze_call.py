#!/usr/bin/env python3
"""
Analyze Langfuse traces for call debugging.

Usage:
    # Analyze most recent trace
    python scripts/analyze_call.py

    # Analyze specific session
    python scripts/analyze_call.py --session-id <session_id>

    # Show last N traces
    python scripts/analyze_call.py --list 5
"""

import argparse
import base64
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

# Langfuse REST API client
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

def get_auth_header():
    """Generate Basic Auth header for Langfuse API."""
    credentials = f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def api_get(endpoint: str, params: dict = None):
    """Make GET request to Langfuse API."""
    url = f"{LANGFUSE_HOST}/api/public{endpoint}"
    response = httpx.get(url, headers=get_auth_header(), params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def list_recent_traces(limit: int = 10):
    """List recent traces with key info."""
    print(f"\n=== Last {limit} Conversation Traces ===\n")

    # Fetch more and filter for conversation traces
    result = api_get("/traces", {"limit": limit * 10, "orderBy": "timestamp.desc"})
    all_traces = result.get("data", [])

    # Filter for conversation traces (parent traces, not individual spans)
    traces = [t for t in all_traces if t.get("name") == "conversation" or "conversation" in (t.get("name") or "").lower()]

    # If no conversation traces, fall back to showing all
    if not traces:
        print("No 'conversation' traces found. Showing all traces:\n")
        traces = all_traces

    traces = traces[:limit]

    for i, trace in enumerate(traces, 1):
        session_id = trace.get("sessionId") or "N/A"
        name = trace.get("name") or "unnamed"
        timestamp = trace.get("timestamp", "N/A")
        if timestamp != "N/A":
            timestamp = timestamp[:19].replace("T", " ")

        # Get metadata
        metadata = trace.get("metadata") or {}
        workflow = metadata.get("workflow", "N/A")
        phone = metadata.get("phone_number", "N/A")

        print(f"{i}. [{timestamp}] {name}")
        print(f"   Session: {session_id}")
        print(f"   Workflow: {workflow} | Phone: {phone}")
        print(f"   Trace ID: {trace.get('id')}")
        print()


def analyze_trace(trace_id: str = None, session_id: str = None):
    """Analyze a specific trace and output structured summary."""

    # Fetch the trace
    if session_id:
        result = api_get("/traces", {"sessionId": session_id, "limit": 10})
        traces = result.get("data", [])
        # Find the conversation trace
        conv_traces = [t for t in traces if t.get("name") == "conversation"]
        if conv_traces:
            trace = conv_traces[0]
        elif traces:
            trace = traces[0]
        else:
            print(f"No trace found for session: {session_id}")
            return
    elif trace_id:
        trace = api_get(f"/traces/{trace_id}")
    else:
        # Get most recent conversation trace
        result = api_get("/traces", {"limit": 50, "orderBy": "timestamp.desc"})
        all_traces = result.get("data", [])
        conv_traces = [t for t in all_traces if t.get("name") == "conversation"]
        if conv_traces:
            trace = conv_traces[0]
        elif all_traces:
            trace = all_traces[0]
        else:
            print("No traces found")
            return

    print("\n" + "=" * 60)
    print("CALL ANALYSIS")
    print("=" * 60)

    # Basic info
    metadata = trace.get("metadata") or {}
    print(f"\nSession ID: {trace.get('sessionId')}")
    print(f"Trace ID: {trace.get('id')}")
    print(f"Timestamp: {trace.get('timestamp')}")
    print(f"Workflow: {metadata.get('workflow', 'N/A')}")
    print(f"Phone: {metadata.get('phone_number', 'N/A')}")
    print(f"Organization: {metadata.get('organization_id', 'N/A')}")
    print(f"Langfuse URL: {LANGFUSE_HOST}/trace/{trace.get('id')}")

    # Fetch observations (spans) for this trace
    # The trace object itself contains observations if we fetch it directly
    trace_id = trace.get("id")
    try:
        full_trace = api_get(f"/traces/{trace_id}")
        observations = full_trace.get("observations", [])
    except Exception as e:
        print(f"Could not fetch trace details: {e}")
        observations = []

    if not observations:
        print("\nNo observations found for this trace")
        return

    # Categorize observations
    turns = []
    llm_calls = []
    tts_calls = []
    stt_calls = []
    errors = []
    latency_data = []

    for obs in observations:
        name = (obs.get("name") or "").lower()
        model = (obs.get("model") or "").lower()

        if "turn" in name:
            turns.append(obs)
        elif "tts" in name or "cartesia" in name or "sonic" in model:
            tts_calls.append(obs)
        elif "stt" in name or "deepgram" in name:
            stt_calls.append(obs)
        elif "llm" in name or "openai" in name or "groq" in name or "gpt" in model or obs.get("type") == "GENERATION":
            llm_calls.append(obs)
        elif "latency" in name:
            latency_data.append(obs)

        # Check for errors
        level = obs.get("level") or ""
        status = obs.get("statusMessage") or ""
        if level == "ERROR" or "error" in status.lower():
            errors.append(obs)

    # Print conversation flow
    print("\n" + "-" * 40)
    print("CONVERSATION FLOW")
    print("-" * 40)

    # Extract conversation from LLM calls (input messages + output)
    conversation = []

    for llm in sorted(llm_calls, key=lambda x: x.get("startTime") or ""):
        input_data = llm.get("input")
        output_data = llm.get("output")
        start_time = llm.get("startTime") or ""

        # Get the last user message from input
        if isinstance(input_data, list):
            for msg in reversed(input_data):
                if isinstance(msg, dict) and msg.get("role") == "user":
                    content = msg.get("content", "")
                    if content and len(str(content)) < 500:  # Skip long/system messages
                        conversation.append((start_time, "USER", str(content)))
                        break

        # Get bot response from output
        if output_data:
            if isinstance(output_data, str) and output_data.strip():
                conversation.append((start_time + "z", "BOT", output_data))  # +z to sort after user
            elif isinstance(output_data, dict):
                content = output_data.get("content", output_data.get("text", ""))
                if content:
                    conversation.append((start_time + "z", "BOT", str(content)))

    # Sort by timestamp and display
    conversation.sort(key=lambda x: x[0])

    if conversation:
        seen = set()  # Deduplicate similar messages
        for ts, role, text in conversation:
            text_key = (role, text[:50])
            if text_key in seen:
                continue
            seen.add(text_key)
            prefix = "USER" if role == "USER" else "BOT"
            print(f"[{prefix}]: {text[:300]}")
            print()
    else:
        print("No conversation data extracted")

    # Print LLM calls summary
    print("\n" + "-" * 40)
    print(f"LLM CALLS ({len(llm_calls)} total)")
    print("-" * 40)

    for llm in sorted(llm_calls, key=lambda x: x.get("startTime") or "")[:15]:
        model = llm.get("model") or "unknown"
        duration = ""
        start = llm.get("startTime")
        end = llm.get("endTime")
        if start and end:
            try:
                from datetime import datetime
                s = datetime.fromisoformat(start.replace("Z", "+00:00"))
                e = datetime.fromisoformat(end.replace("Z", "+00:00"))
                dur_ms = (e - s).total_seconds() * 1000
                duration = f"{dur_ms:.0f}ms"
            except (ValueError, TypeError):
                pass

        usage = llm.get("usage") or {}
        tokens = f"in:{usage.get('input', usage.get('promptTokens', '?'))} out:{usage.get('output', usage.get('completionTokens', '?'))}"

        # Check for function calls
        output = llm.get("output") or {}
        func_call = ""
        if isinstance(output, dict) and output.get("tool_calls"):
            func_names = [tc.get("function", {}).get("name", "?") for tc in output.get("tool_calls", [])]
            func_call = f" -> {', '.join(func_names)}"

        print(f"  [{model}] {duration} | {tokens}{func_call}")

    # Print errors
    if errors:
        print("\n" + "-" * 40)
        print(f"ERRORS ({len(errors)})")
        print("-" * 40)
        for err in errors:
            print(f"  - {err.get('name')}: {err.get('statusMessage') or 'No message'}")

    # Print latency summary
    print("\n" + "-" * 40)
    print("LATENCY")
    print("-" * 40)

    for lat in latency_data:
        lat_meta = lat.get("metadata") or {}
        print(f"  V2V: {lat_meta.get('v2v_ms', '?')}ms | LLM TTFB: {lat_meta.get('llm_ttfb_ms', '?')}ms | TTS TTFB: {lat_meta.get('tts_ttfb_ms', '?')}ms")

    if not latency_data:
        print("  No latency spans found")

    # Summary stats
    print("\n" + "-" * 40)
    print("SUMMARY")
    print("-" * 40)
    print(f"  Total observations: {len(observations)}")
    print(f"  Turns: {len(turns)}")
    print(f"  LLM calls: {len(llm_calls)}")
    print(f"  TTS calls: {len(tts_calls)}")
    print(f"  STT calls: {len(stt_calls)}")
    print(f"  Errors: {len(errors)}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Analyze Langfuse call traces")
    parser.add_argument("--session-id", "-s", help="Session ID to analyze")
    parser.add_argument("--trace-id", "-t", help="Trace ID to analyze")
    parser.add_argument("--list", "-l", type=int, nargs="?", const=10, help="List recent traces")

    args = parser.parse_args()

    if args.list:
        list_recent_traces(args.list)
    else:
        analyze_trace(trace_id=args.trace_id, session_id=args.session_id)


if __name__ == "__main__":
    main()
