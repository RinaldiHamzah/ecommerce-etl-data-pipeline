from __future__ import annotations

import logging
from typing import Any

from psycopg2.pool import SimpleConnectionPool

from config import get_database_config

logger = logging.getLogger(__name__)
_pool: SimpleConnectionPool | None = None


def get_pool() -> SimpleConnectionPool:
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(minconn=1, maxconn=8, **get_database_config())
        logger.info("Dashboard database connection pool initialized")
    return _pool


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception:
        logger.exception("Dashboard query failed")
        raise
    finally:
        pool.putconn(conn)


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    rows = fetch_all(query, params)
    return rows[0] if rows else {}
