#!/usr/bin/env python3
import argparse
import asyncio
import importlib.util
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

def load_schema(client: str, workflow: str) -> dict:
    schema_path = Path(__file__).parent.parent / "clients" / client / workflow / "schema.py"
    if not schema_path.exists():
        raise FileNotFoundError(f"No schema.py found at {schema_path}")
    spec = importlib.util.spec_from_file_location("schema", schema_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.WORKFLOW_SCHEMA

async def apply_schema(db, client: str, workflow: str):
    schema = load_schema(client, workflow)
    result = await db.organizations.update_one(
        {"slug": client},
        {
            "$set": {
                f"workflows.{workflow}": schema,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    return result.matched_count > 0

async def show_current(db, client: str, workflow: str):
    org = await db.organizations.find_one({"slug": client})
    if not org:
        print(f"Organization '{client}' not found")
        return
    wf = org.get("workflows", {}).get(workflow)
    if not wf:
        print(f"Workflow '{workflow}' not found for '{client}'")
        return
    fields = wf.get("patient_schema", {}).get("fields", [])
    print(f"\n{client}/{workflow}: {len(fields)} fields in DB")
    for f in fields:
        computed = " (computed)" if f.get("computed") else ""
        print(f"  {f['display_order']:2d}. {f['key']}: {f['label']}{computed}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", help="Workflow name (e.g. eligibility_verification)")
    parser.add_argument("-c", "--client", required=True, help="Client slug (e.g. demo_clinic_alpha)")
    parser.add_argument("--show", action="store_true", help="Show current DB schema instead of applying")
    args = parser.parse_args()

    client = AsyncIOMotorClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    db = client[os.getenv("MONGO_DB_NAME", "alfons")]

    if args.show:
        await show_current(db, args.client, args.workflow)
    else:
        schema = load_schema(args.client, args.workflow)
        field_count = len(schema.get("patient_schema", {}).get("fields", []))
        print(f"Applying {args.client}/{args.workflow} schema ({field_count} fields)...")

        if await apply_schema(db, args.client, args.workflow):
            print(f"✓ Updated {args.client}/{args.workflow}")
        else:
            print(f"✗ Organization '{args.client}' not found")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
