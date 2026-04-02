"""
Centralized non-secret configuration constants for Postopus.

Place small, non-sensitive defaults and lists here. Secrets and tokens
must remain in the `.env` file and be accessed via `env_loader`.
"""

# Theme/category names used across the codebase. Keep in sync with DB schema.
THEMES = (
    "detsad",
    "kultura",
    "admin",
    "novost",
    "union",
    "sport",
    "reklama",
    "kultpodved",
)

# Default name_base used by driver_tables and session initialization
DEFAULT_NAME_BASE = "config"

# Default cron schedule lines used by start scripts as a fallback.
# These are non-secret and serve as sensible defaults; override per-deployment
# by storing schedules in MongoDB or providing alternate config.
CRON_SCHEDULE = (
    "05 7,8,10,12,14-23 mi_novost",
    "15 9,13 mi_repost_reklama",
    "15 7,12,18,20,22 mi_addons",
    "15 21 mi_repost_krugozor",
    "15 19 mi_repost_aprel",
    "20 6-23 mi_repost_me",
    # dran - disabled by default
    # '25 7,9,12,18,20,22 dran_novost',
    # '25 6,8,11,15,19,21,23 dran_addons',
    # '40 5-22 dran_reklama',
    "50 6-22 mi_reklama",
)
