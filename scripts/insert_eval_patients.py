#!/usr/bin/env python3
"""
Insert eval patients from scenarios.yaml files.

Reads patient data from evals/demo_clinic_alpha/*/scenarios.yaml
and inserts into the database. This ensures eval scenarios and
voice testing use the exact same patient data.

Run during dev.sh or manually: python scripts/insert_eval_patients.py
"""
import asyncio
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml
from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent.parent / ".env")

DEMO_CLINIC_ALPHA_ORG_ID = ObjectId("6920f7c6a588212df55fc295")
DEMO_CLINIC_BETA_ORG_ID = ObjectId("6920f7c6a588212df55fc296")
DEV_ORG_IDS = [DEMO_CLINIC_ALPHA_ORG_ID, DEMO_CLINIC_BETA_ORG_ID]
EVALS_DIR = Path(__file__).parent.parent / "evals" / "demo_clinic_alpha"


def normalize_date(date_str: str) -> str:
    """Convert various date formats to YYYY-MM-DD."""
    if not date_str:
        return ""

    # Already ISO format: 1972-06-18
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return date_str

    # MM/DD/YYYY format: 04/23/2001
    if re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        month, day, year = date_str.split("/")
        return f"{year}-{month}-{day}"

    return date_str


def normalize_phone(phone_str: str) -> str:
    """Strip non-digits from phone number."""
    return re.sub(r"\D", "", phone_str)


def extract_name_parts(full_name: str) -> tuple[str, str]:
    """Split 'First Last' into (first, last)."""
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])
    return full_name, ""


# Test phone number for manual eligibility verification testing
# User simulates insurance company on this number
ELIGIBILITY_TEST_PHONE = "+15555550143"


def load_scenarios_from_yaml(yaml_path: Path, workflow: str) -> list[dict]:
    """Load patient data from a scenarios.yaml file."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    patients = []
    seen_keys = set()  # Track unique patients

    for scenario in data.get("scenarios", []):
        patient_data = scenario.get("patient", {})
        if not patient_data:
            continue

        # Eligibility verification uses member_id for uniqueness
        if workflow == "eligibility_verification":
            member_id = patient_data.get("insurance_member_id", "")
            if not member_id or member_id in seen_keys:
                continue
            seen_keys.add(member_id)
        else:
            # Other workflows use phone_number
            phone = normalize_phone(patient_data.get("phone_number", ""))
            if not phone or phone in seen_keys:
                continue
            seen_keys.add(phone)

        first_name, last_name = extract_name_parts(patient_data.get("patient_name", ""))

        # Build patient document
        patient = {
            "patient_name": patient_data.get("patient_name", ""),
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": normalize_date(patient_data.get("date_of_birth", "")),
            "workflow": workflow,
            "identity_verified": False,
        }

        # Workflow-specific fields
        if workflow == "eligibility_verification":
            patient.update({
                "phone_number": "",  # Not applicable for eligibility
                "insurance_member_id": patient_data.get("insurance_member_id", ""),
                "insurance_company_name": patient_data.get("insurance_company_name", ""),
                "insurance_phone": ELIGIBILITY_TEST_PHONE,  # Override for testing
                "provider_agent_first_name": patient_data.get("provider_agent_first_name", ""),
                "provider_agent_last_initial": patient_data.get("provider_agent_last_initial", ""),
                "facility_name": patient_data.get("facility_name", ""),
                "tax_id": patient_data.get("tax_id", ""),
                "provider_name": patient_data.get("provider_name", ""),
                "provider_npi": patient_data.get("provider_npi", ""),
                "provider_call_back_phone": patient_data.get("provider_call_back_phone", ""),
                "cpt_code": patient_data.get("cpt_code", ""),
                "place_of_service": patient_data.get("place_of_service", ""),
                "date_of_service": patient_data.get("date_of_service", ""),
            })
        elif workflow == "prescription_status":
            patient.update({
                "phone_number": normalize_phone(patient_data.get("phone_number", "")),
                "pharmacy_name": patient_data.get("pharmacy_name", ""),
                "pharmacy_phone": patient_data.get("pharmacy_phone", ""),
                "pharmacy_address": patient_data.get("pharmacy_address", ""),
                "prescriptions": patient_data.get("prescriptions", []),
                "status_communicated": False,
                "refill_requested": False,
            })
        elif workflow == "lab_results":
            patient.update({
                "phone_number": normalize_phone(patient_data.get("phone_number", "")),
                "test_type": patient_data.get("test_type", ""),
                "test_date": patient_data.get("test_date", ""),
                "ordering_physician": patient_data.get("ordering_physician", ""),
                "results_status": patient_data.get("results_status", ""),
                "results_summary": patient_data.get("results_summary", ""),
                "provider_review_required": patient_data.get("provider_review_required", False),
                "callback_timeframe": patient_data.get("callback_timeframe", ""),
                "results_communicated": False,
            })
        else:
            patient["phone_number"] = normalize_phone(patient_data.get("phone_number", ""))

        patients.append(patient)

    return patients


def load_all_eval_patients() -> list[dict]:
    """Load patients from all workflow scenarios.yaml files."""
    all_patients = []

    for workflow_dir in sorted(EVALS_DIR.iterdir()):
        if not workflow_dir.is_dir():
            continue

        scenarios_file = workflow_dir / "scenarios.yaml"
        if not scenarios_file.exists():
            continue

        workflow = workflow_dir.name
        patients = load_scenarios_from_yaml(scenarios_file, workflow)
        all_patients.extend(patients)

    return all_patients


async def reset_eval_patients():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client["alfons"]

    # Archive cost data from sessions before deleting them
    # This preserves usage/cost benchmarks for the cost estimator
    sessions_with_costs = await db.sessions.find(
        {"organization_id": {"$in": DEV_ORG_IDS}, "total_cost_usd": {"$exists": True, "$gt": 0}},
        {"usage": 1, "costs": 1, "total_cost_usd": 1, "workflow": 1, "created_at": 1, "organization_id": 1},
    ).to_list(length=None)

    if sessions_with_costs:
        benchmarks = []
        for s in sessions_with_costs:
            benchmarks.append({
                "workflow": s.get("workflow"),
                "organization_id": s.get("organization_id"),
                "usage": s.get("usage"),
                "costs": s.get("costs"),
                "total_cost_usd": s.get("total_cost_usd"),
                "session_created_at": s.get("created_at"),
                "archived_at": datetime.now(timezone.utc),
            })
        await db.cost_benchmarks.insert_many(benchmarks)
        print(f"Archived {len(benchmarks)} session cost records to cost_benchmarks")

    # Clean up dev sessions and audit logs for all dev orgs
    # Audit logs may have ObjectId, string, null, or missing org_id (legacy inconsistency)
    sessions_deleted = await db.sessions.delete_many({"organization_id": {"$in": DEV_ORG_IDS}})
    audit_query = {"$or": [
        {"organization_id": {"$in": DEV_ORG_IDS}},
        {"organization_id": {"$in": [str(oid) for oid in DEV_ORG_IDS]}},
        {"organization_id": None},
        {"organization_id": {"$exists": False}},
    ]}
    audit_deleted = await db.audit_logs.delete_many(audit_query)
    print(f"Cleaned up {sessions_deleted.deleted_count} sessions, {audit_deleted.deleted_count} audit logs")

    # Load all patients from scenarios.yaml files
    all_patients = load_all_eval_patients()

    if not all_patients:
        print("No eval patients found in scenarios.yaml files")
        return

    # Get unique names to delete
    names_to_delete = set()
    for p in all_patients:
        names_to_delete.add((p["first_name"], p["last_name"]))

    # Delete existing records for these patients
    delete_filter = {
        "organization_id": DEMO_CLINIC_ALPHA_ORG_ID,
        "$or": [{"first_name": fn, "last_name": ln} for fn, ln in names_to_delete],
    }
    result = await db.patients.delete_many(delete_filter)
    print(f"Deleted {result.deleted_count} existing eval patient(s)")

    # Insert fresh records
    now = datetime.now(timezone.utc)
    docs = []
    for p in all_patients:
        doc = {
            **p,
            "organization_id": DEMO_CLINIC_ALPHA_ORG_ID,
            "call_status": "Not Started",
            "created_at": now,
            "updated_at": now,
        }
        docs.append(doc)

    await db.patients.insert_many(docs)

    # Group by workflow for display
    by_workflow = {}
    for p in all_patients:
        wf = p["workflow"]
        if wf not in by_workflow:
            by_workflow[wf] = []
        by_workflow[wf].append(p)

    print(f"Inserted {len(all_patients)} eval patients:")
    for workflow in sorted(by_workflow.keys()):
        print(f"  {workflow}:")
        for p in by_workflow[workflow]:
            # Workflow-specific display
            if workflow == "eligibility_verification":
                member_id = p.get("insurance_member_id", "")
                insurance = p.get("insurance_company_name", "")
                cpt = p.get("cpt_code", "")
                print(f"    {p['patient_name']:18} {member_id:15} {insurance:20} CPT {cpt}")
            else:
                phone = p["phone_number"]
                phone_fmt = f"{phone[:3]}-{phone[3:6]}-{phone[6:]}" if len(phone) >= 10 else phone

                if workflow == "prescription_status":
                    meds = len(p.get("prescriptions", []))
                    status = p["prescriptions"][0]["status"] if meds == 1 else f"{meds} meds"
                elif workflow == "lab_results":
                    status = p.get("results_status", "")
                else:
                    status = ""

                print(f"    {p['patient_name']:18} {phone_fmt}  DOB {p['date_of_birth']}  {status}")


if __name__ == "__main__":
    asyncio.run(reset_eval_patients())
