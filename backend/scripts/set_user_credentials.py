"""Create or update login users in user_master (no signup API).

``user_master.email`` is the **notification address** used by assign/resolve
webhooks (n8n payload field ``email``). It is also the login identifier.
Runtime Copilot uses ``external_reference`` for Salveris acting principal and
``password_hash`` for login. It does not read bootstrap constants from this file.

Examples:
  python -m backend.scripts.set_user_credentials --seed-alice-bob
  python -m backend.scripts.set_user_credentials --email ops@example.com \\
      --name Alice --role ops --password ... --external-reference <uuid>

``--seed-alice-bob`` inserts Alice, Bob, Rita, and Karan Malhotra only when
they are missing. Existing rows keep their email. Empty ``password_hash`` and
``external_reference`` are filled. Karan Malhotra is updated in place when the
name already exists in ``user_master``.
Existing rows keep their email, password hash, and Salveris principal.
Optional env vars apply only when a field is empty on insert or when
``--reset-passwords`` is set.
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

# First-insert bootstrap only. Never used by the running API.
_BOOTSTRAP_USERS: tuple[dict[str, str], ...] = (
    {
        "name": "Alice",
        "role": "Ops Engineer",
        "email": "alice@sentineliq.demo",
        "password_env": "SEED_ALICE_PASSWORD",
        "password": "Alice123!",
        "principal_env": "SALVERIS_DEFAULT_ACTING_PRINCIPAL_ID",
        "principal": "10000000-0000-0000-0000-000000000031",
    },
    {
        "name": "Bob",
        "role": "Ops Engineer",
        "email": "bob@sentineliq.demo",
        "password_env": "SEED_BOB_PASSWORD",
        "password": "Bob123!",
        "principal_env": "SALVERIS_BOB_ACTING_PRINCIPAL_ID",
        "principal": "10000000-0000-0000-0000-000000000032",
    },
    {
        "name": "Rita",
        "role": "HR",
        "email": "rita@hr.local",
        "password_env": "SEED_RITA_PASSWORD",
        "password": "Rita123!",
        "principal_env": "SALVERIS_RITA_ACTING_PRINCIPAL_ID",
        "principal": "10000000-0000-0000-0000-000000000034",
    },
    {
        "name": "Karan Malhotra",
        "role": "Operations Manager",
        "email": "karan.malhotra@sentineliq.demo",
        "password_env": "SEED_KARAN_PASSWORD",
        "password": "Karan123!",
        "principal_env": "SALVERIS_KARAN_ACTING_PRINCIPAL_ID",
        "principal": "10000000-0000-0000-0000-00000000003f",
    },
)


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


def find_user(db, *, name: str | None = None, email: str | None = None) -> UserMaster | None:
    if email:
        user = (
            db.query(UserMaster)
            .filter(UserMaster.email.ilike(email.strip().lower()))
            .first()
        )
        if user is not None:
            return user
    if name:
        return (
            db.query(UserMaster)
            .filter(UserMaster.name.ilike(name.strip()))
            .first()
        )
    return None


def upsert_user(
    db,
    *,
    email: str,
    name: str,
    role: str,
    password: str,
    external_reference: str,
    overwrite_password: bool = True,
    overwrite_email: bool = True,
    overwrite_principal: bool = True,
) -> UserMaster:
    email_norm = email.strip().lower()
    user = find_user(db, name=name, email=email_norm)
    created = user is None
    if user is None:
        user = UserMaster(email=email_norm, name=name.strip(), active=True)
        db.add(user)
        overwrite_password = True
        overwrite_email = True
        overwrite_principal = True

    user.name = name.strip()
    if role.strip():
        user.role = role.strip()
    user.active = True
    if overwrite_email or not (user.email or "").strip():
        user.email = email_norm
    if overwrite_principal or not (user.external_reference or "").strip():
        user.external_reference = external_reference.strip()
    if overwrite_password or not (user.password_hash or "").strip():
        user.password_hash = hash_password(password)
    db.commit()
    db.refresh(user)
    _logger.info(
        "User credentials upserted (user_id=%s, created=%s, email='%s', "
        "external_reference='%s')",
        user.user_id,
        created,
        user.email,
        user.external_reference,
    )
    return user


def seed_demo_users(*, reset_passwords: bool) -> None:
    db = SessionLocal()
    try:
        for spec in _BOOTSTRAP_USERS:
            existing = find_user(db, name=spec["name"], email=spec["email"])
            email = spec["email"]
            principal = _env(spec["principal_env"], spec["principal"])
            password = _env(spec["password_env"], spec["password"])
            if existing is not None:
                if (existing.email or "").strip():
                    email = existing.email.strip()
                if (existing.external_reference or "").strip():
                    principal = existing.external_reference.strip()
                elif not _env(spec["principal_env"]):
                    principal = spec["principal"]
            upsert_user(
                db,
                email=email,
                name=spec["name"],
                role=spec["role"],
                password=password,
                external_reference=principal,
                overwrite_password=reset_passwords,
                overwrite_email=False,
                overwrite_principal=False,
            )
    finally:
        db.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Set user_master login credentials")
    parser.add_argument(
        "--seed-alice-bob",
        action="store_true",
        help="Insert Alice, Bob, Rita, and Karan Malhotra when missing; "
        "keep existing DB email (notification address). Fill empty "
        "password hash and Salveris principal",
    )
    parser.add_argument(
        "--reset-passwords",
        action="store_true",
        help="With --seed-alice-bob, replace password hashes from env or bootstrap",
    )
    parser.add_argument("--email")
    parser.add_argument("--name")
    parser.add_argument("--role", default="Ops Engineer")
    parser.add_argument("--password")
    parser.add_argument("--external-reference")
    args = parser.parse_args(argv)

    apply_schema()

    if args.seed_alice_bob:
        seed_demo_users(reset_passwords=args.reset_passwords)
        print(
            "Seeded Alice, Bob, Rita, and Karan Malhotra from user_master "
            "(passwords not printed)."
        )
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
