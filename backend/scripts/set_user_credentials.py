"""Create or update login users in user_master (no signup API).

Examples:
  python -m backend.scripts.set_user_credentials --seed-alice-bob
  python -m backend.scripts.set_user_credentials --email alice@sentineliq.demo \\
      --name Alice --role ops --password ... --external-reference <uuid>

Default local-dev passwords for --seed-alice-bob (override with env):
  Alice: alice@sentineliq.demo  (SEED_ALICE_PASSWORD, default Alice123!)
  Bob:   bob@sentineliq.demo    (SEED_BOB_PASSWORD, default Bob123!)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")
_venv_env = _ROOT / ".venv" / ".env"
if _venv_env.exists():
    load_dotenv(_venv_env)

from backend.database import SessionLocal, engine
from backend.db_models import UserMaster
from backend.logging_config import get_logger, setup_logging
from backend.services.auth_service import hash_password

setup_logging()
_logger = get_logger(__name__)

ALICE_EMAIL = "alice@sentineliq.demo"
BOB_EMAIL = "bob@sentineliq.demo"
DEFAULT_ALICE_PASSWORD = "Alice123!"
DEFAULT_BOB_PASSWORD = "Bob123!"
DEFAULT_ALICE_PRINCIPAL = "10000000-0000-0000-0000-000000000031"
DEFAULT_BOB_PRINCIPAL = "10000000-0000-0000-0000-000000000032"


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def apply_schema() -> None:
    sql_path = _ROOT / "backend" / "sql" / "alter_user_master_auth.sql"
    kept: list[str] = []
    for line in sql_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        kept.append(stripped)
    statements = [stmt.strip() for stmt in " ".join(kept).split(";") if stmt.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
    _logger.info("user_master auth columns applied")


def upsert_user(
    db,
    *,
    email: str,
    name: str,
    role: str,
    password: str,
    external_reference: str,
) -> UserMaster:
    email_norm = email.strip().lower()
    user = (
        db.query(UserMaster)
        .filter(UserMaster.email.ilike(email_norm))
        .first()
    )
    created = user is None
    if user is None:
        user = UserMaster(email=email_norm, name=name.strip(), active=True)
        db.add(user)

    user.name = name.strip()
    user.role = role.strip() or user.role
    user.active = True
    user.password_hash = hash_password(password)
    user.external_reference = external_reference.strip()
    db.commit()
    db.refresh(user)
    _logger.info(
        "User credentials upserted (user_id=%s, created=%s, "
        "external_reference='%s')",
        user.user_id,
        created,
        user.external_reference,
    )
    return user


def seed_alice_bob(alice_password: str, bob_password: str) -> None:
    alice_ref = _env("SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID", DEFAULT_ALICE_PRINCIPAL)
    bob_ref = _env("SALVERIS_BOB_ACTING_PRINCIPAL_ID", DEFAULT_BOB_PRINCIPAL)
    if not alice_ref or not bob_ref:
        raise SystemExit(
            "Alice/Bob Salveris principal IDs are missing. Set "
            "SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID and SALVERIS_BOB_ACTING_PRINCIPAL_ID."
        )
    db = SessionLocal()
    try:
        upsert_user(
            db,
            email=ALICE_EMAIL,
            name="Alice",
            role="Ops Engineer",
            password=alice_password,
            external_reference=alice_ref,
        )
        upsert_user(
            db,
            email=BOB_EMAIL,
            name="Bob",
            role="Ops Engineer",
            password=bob_password,
            external_reference=bob_ref,
        )
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Set user_master login credentials")
    parser.add_argument(
        "--seed-alice-bob",
        action="store_true",
        help="Upsert Alice and Bob mapped to Salveris acting principals",
    )
    parser.add_argument("--email")
    parser.add_argument("--name")
    parser.add_argument("--role", default="Ops Engineer")
    parser.add_argument("--password")
    parser.add_argument("--external-reference")
    args = parser.parse_args(argv)

    apply_schema()

    if args.seed_alice_bob:
        alice_password = _env("SEED_ALICE_PASSWORD", DEFAULT_ALICE_PASSWORD)
        bob_password = _env("SEED_BOB_PASSWORD", DEFAULT_BOB_PASSWORD)
        seed_alice_bob(alice_password, bob_password)
        print("Seeded Alice and Bob (passwords not printed).")
        return 0

    missing = [
        name
        for name, value in (
            ("email", args.email),
            ("name", args.name),
            ("password", args.password),
            ("external-reference", args.external_reference),
        )
        if not value
    ]
    if missing:
        parser.error("missing required arguments: " + ", ".join(missing))

    db = SessionLocal()
    try:
        upsert_user(
            db,
            email=args.email,
            name=args.name,
            role=args.role,
            password=args.password,
            external_reference=args.external_reference,
        )
    finally:
        db.close()
    print("User credentials updated (password not printed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
