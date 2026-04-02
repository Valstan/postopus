"""Migration helper: move centralized config constants into MongoDB.

Usage:
  python scripts/migrate_config_to_db.py         # dry-run (prints what would be written)
  python scripts/migrate_config_to_db.py --apply # perform upsert into MongoDB
"""

from __future__ import annotations

import argparse
import datetime
import json
from typing import Any, Dict

from env_loader import MONGO_BASE, logger

try:
    from bin.config import CRON_SCHEDULE, DEFAULT_NAME_BASE, THEMES
except Exception:
    THEMES = []
    CRON_SCHEDULE = []
    DEFAULT_NAME_BASE = "config"


def build_doc() -> Dict[str, Any]:
    return {
        "title": "postopus_config",
        "themes": list(THEMES),
        "cron_schedule": list(CRON_SCHEDULE),
        "name_base_default": DEFAULT_NAME_BASE,
        "updated_at": datetime.datetime.utcnow(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write to MongoDB")
    args = parser.parse_args(argv)

    doc = build_doc()

    print("=== Migration plan: postopus_config ===")
    print(
        json.dumps(
            {k: (v if k != "updated_at" else str(v)) for k, v in doc.items()},
            indent=2,
            ensure_ascii=False,
        )
    )

    if not args.apply:
        print("\nDry-run: use --apply to write to MongoDB")
        return 0

    if MONGO_BASE is None:
        logger.error("MONGO_BASE not configured (MONGO_CLIENT missing in .env). Aborting write.")
        return 2

    collection = MONGO_BASE["site_config"]
    # Convert updated_at to RFC string for storage
    doc_to_store = dict(doc)
    doc_to_store["updated_at"] = doc["updated_at"].isoformat()

    result = collection.update_one(
        {"title": "postopus_config"}, {"$set": doc_to_store}, upsert=True
    )
    if result.acknowledged:
        print("Migration applied: upserted postopus_config")
        return 0
    else:
        print("Migration failed (no acknowledgement from MongoDB)")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
