from datetime import UTC, datetime


def now_iso_date() -> str:
    return datetime.now(UTC).date().isoformat()
