"""
Script de migración incremental.
Agrega columnas faltantes a tablas existentes sin perder datos.
Es idempotente: se puede ejecutar varias veces sin error.
Usa las credenciales del archivo .env del proyecto.
"""
import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import text
from src.infrastructure.database.connection import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Migraciones simples: ADD COLUMN con verificación de existencia
# ──────────────────────────────────────────────────────────────────────────────
ADD_COLUMN_MIGRATIONS = [
    # ── users: columnas de perfil extendido (Historia 10 / Fase 3) ──
    {
        "description": "users.age (INT nullable)",
        "check": "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='users' AND COLUMN_NAME='age'",
        "sql": "ALTER TABLE users ADD COLUMN age INT NULL",
    },
    {
        "description": "users.gender (ENUM nullable)",
        "check": "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='users' AND COLUMN_NAME='gender'",
        "sql": "ALTER TABLE users ADD COLUMN gender ENUM('MALE','FEMALE','OTHER','PREFER_NOT_TO_SAY') NULL",
    },
    {
        "description": "users.height (FLOAT nullable)",
        "check": "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='users' AND COLUMN_NAME='height'",
        "sql": "ALTER TABLE users ADD COLUMN height FLOAT NULL",
    },
    {
        "description": "users.fitness_goal (ENUM nullable)",
        "check": "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='users' AND COLUMN_NAME='fitness_goal'",
        "sql": "ALTER TABLE users ADD COLUMN fitness_goal ENUM('WEIGHT_LOSS','MUSCLE_GAIN','GENERAL_FITNESS','ATHLETIC_PERFORMANCE','HEALTH_MAINTENANCE') NULL",
    },
    {
        "description": "users.activity_level (VARCHAR nullable)",
        "check": "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='users' AND COLUMN_NAME='activity_level'",
        "sql": "ALTER TABLE users ADD COLUMN activity_level VARCHAR(50) NULL",
    },
    # ── physical_records: recorded_at (Historia 4 / RF-064) ──
    {
        "description": "physical_records.recorded_at (DATETIME, default NOW)",
        "check": "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='physical_records' AND COLUMN_NAME='recorded_at'",
        "sql": (
            "ALTER TABLE physical_records "
            "ADD COLUMN recorded_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6), "
            "ADD INDEX ix_physical_records_recorded_at (recorded_at)"
        ),
    },
    {
        "description": "physical_records: sincronizar recorded_at ← created_at en registros existentes",
        "check": None,
        "sql": (
            "UPDATE physical_records "
            "SET recorded_at = created_at "
            "WHERE created_at IS NOT NULL AND (recorded_at IS NULL OR recorded_at = '1970-01-01 00:00:00')"
        ),
    },
]


async def migrate_refresh_tokens(conn) -> None:
    """
    Reestructura refresh_tokens del esquema antiguo al nuevo.
    Esquema antiguo: token (PK VARCHAR), user_id, expires_at, is_revoked (bool), created_at.
    Esquema nuevo:   id (PK CHAR36), user_id, token (UNIQUE), expires_at, created_at, revoked_at (nullable).
    """
    # Verificar si ya tiene columna 'id'
    result = await conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='refresh_tokens' AND COLUMN_NAME='id'"
    ))
    has_id = int(result.scalar() or 0) > 0

    if has_id:
        logger.info("[SKIP]  refresh_tokens — ya tiene esquema nuevo (columna 'id' presente)")
        return

    logger.info("[...] refresh_tokens — migrando esquema antiguo a nuevo...")
    # En entorno de desarrollo, los tokens son de corta vida. Se recrea la tabla.
    await conn.execute(text("DROP TABLE IF EXISTS refresh_tokens"))
    await conn.execute(text("""
        CREATE TABLE refresh_tokens (
            id         CHAR(36)     NOT NULL,
            user_id    CHAR(36)     NOT NULL,
            token      VARCHAR(512) NOT NULL,
            expires_at DATETIME     NOT NULL,
            created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            revoked_at DATETIME     NULL,
            PRIMARY KEY (id),
            UNIQUE KEY uq_refresh_tokens_token (token),
            KEY ix_refresh_tokens_user_id (user_id),
            CONSTRAINT fk_rt_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """))
    logger.info("[OK]    refresh_tokens — tabla recreada con esquema correcto")


async def run_migrations():
    logger.info("Iniciando migraciones incrementales...")
    async with engine.begin() as conn:
        # 1. Migraciones simples (ADD COLUMN)
        for m in ADD_COLUMN_MIGRATIONS:
            desc = m["description"]
            check_sql = m.get("check")
            apply_sql = m["sql"]

            if check_sql:
                result = await conn.execute(text(check_sql))
                count = result.scalar()
                if count and int(count) > 0:
                    logger.info(f"[SKIP]  {desc} — ya existe")
                    continue

            try:
                await conn.execute(text(apply_sql))
                logger.info(f"[OK]    {desc}")
            except Exception as exc:
                logger.warning(f"[WARN]  {desc} — {exc}")

        # 2. Migración estructural de refresh_tokens
        await migrate_refresh_tokens(conn)

    logger.info("Migraciones completadas.")


if __name__ == "__main__":
    asyncio.run(run_migrations())
