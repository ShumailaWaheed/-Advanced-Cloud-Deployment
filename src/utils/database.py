"""Database connection pooling utilities for the todo chatbot application."""

import asyncio
import asyncpg
import psycopg2.pool
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager, contextmanager
import logging
import json as json_mod
import uuid as uuid_mod
from datetime import datetime, timezone
from src.config.db_config import DatabaseConfig


async def _init_connection(conn):
    """Set up type codecs on each new connection so services can pass
    plain strings for UUID, timestamp, and jsonb columns."""
    await conn.set_type_codec(
        'uuid', encoder=lambda v: str(v), decoder=lambda v: v,
        schema='pg_catalog', format='text',
    )
    await conn.set_type_codec(
        'jsonb', encoder=lambda v: json_mod.dumps(v) if v is not None else v,
        decoder=lambda v: json_mod.loads(v) if v is not None else v,
        schema='pg_catalog', format='text',
    )
    await conn.set_type_codec(
        'json', encoder=lambda v: json_mod.dumps(v) if v is not None else v,
        decoder=lambda v: json_mod.loads(v) if v is not None else v,
        schema='pg_catalog', format='text',
    )


class DatabasePool:
    """Database connection pool manager."""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._sync_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self.logger = logging.getLogger(__name__)

    async def initialize_pool(self):
        """Initialize the async connection pool."""
        if self._pool is not None:
            return

        try:
            dsn = DatabaseConfig.get_database_url()
            # Strip channel_binding from DSN (asyncpg doesn't support it)
            import re
            dsn = re.sub(r'[?&]channel_binding=[^&]*', '', dsn)
            dsn = dsn.replace('?&', '?').rstrip('?')

            self._pool = await asyncpg.create_pool(
                dsn=dsn,
                min_size=DatabaseConfig.DB_POOL_MIN_SIZE,
                max_size=DatabaseConfig.DB_POOL_MAX_SIZE,
                command_timeout=DatabaseConfig.DB_CONNECT_TIMEOUT,
                timeout=60,
                init=_init_connection,
                server_settings={
                    "application_name": "todo-chatbot",
                    "idle_in_transaction_session_timeout": str(DatabaseConfig.DB_STATEMENT_TIMEOUT * 1000)
                }
            )
            self.logger.info("Async database pool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database pool: {e}")
            raise

    def initialize_sync_pool(self):
        """Initialize the sync connection pool."""
        if self._sync_pool is not None:
            return

        try:
            self._sync_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=DatabaseConfig.DB_POOL_MIN_SIZE,
                maxconn=DatabaseConfig.DB_POOL_MAX_SIZE,
                dsn=DatabaseConfig.get_database_url(),
                connect_timeout=DatabaseConfig.DB_CONNECT_TIMEOUT
            )
            self.logger.info("Sync database pool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize sync database pool: {e}")
            raise

    async def get_connection(self):
        """Get a connection from the async pool."""
        if self._pool is None:
            await self.initialize_pool()
        return await self._pool.acquire()

    def get_sync_connection(self):
        """Get a connection from the sync pool."""
        if self._sync_pool is None:
            self.initialize_sync_pool()
        return self._sync_pool.getconn()

    async def release_connection(self, conn):
        """Release an async connection back to the pool."""
        if self._pool is not None:
            await self._pool.release(conn)

    def release_sync_connection(self, conn):
        """Release a sync connection back to the pool."""
        if self._sync_pool is not None:
            self._sync_pool.putconn(conn)

    @asynccontextmanager
    async def get_db_connection(self):
        """Async context manager for database connections."""
        conn = await self.get_connection()
        try:
            yield conn
        finally:
            await self.release_connection(conn)

    @contextmanager
    def get_sync_db_connection(self):
        """Sync context manager for database connections."""
        conn = self.get_sync_connection()
        try:
            yield conn
        finally:
            self.release_sync_connection(conn)

    async def close_pool(self):
        """Close the async connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def close_sync_pool(self):
        """Close the sync connection pool."""
        if self._sync_pool is not None:
            self._sync_pool.closeall()
            self._sync_pool = None

    async def execute_query(self, query: str, *args) -> Any:
        """Execute a query using a pooled connection."""
        async with self.get_db_connection() as conn:
            return await conn.fetch(query, *args)

    async def execute_single_query(self, query: str, *args) -> Any:
        """Execute a query and return a single result."""
        async with self.get_db_connection() as conn:
            return await conn.fetchrow(query, *args)

    async def execute_command(self, command: str, *args) -> int:
        """Execute a command (INSERT, UPDATE, DELETE) and return affected row count."""
        async with self.get_db_connection() as conn:
            result = await conn.execute(command, *args)
            # Extract row count from result
            if 'UPDATE' in result or 'DELETE' in result or 'INSERT' in result:
                return int(result.split()[-1]) if result.split()[-1].isdigit() else 0
            return 0

    async def health_check(self) -> bool:
        """Perform a health check on the database connection."""
        try:
            async with self.get_db_connection() as conn:
                # Execute a simple query to check connectivity
                result = await conn.fetchrow("SELECT 1 as test")
                return result is not None and result['test'] == 1
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False


# Global database pool instance
db_pool = DatabasePool()


# Initialize the pool when module is imported
async def init_db_pool():
    """Initialize the database pool."""
    await db_pool.initialize_pool()


# Health check function
async def check_db_health() -> Dict[str, Any]:
    """Check database health and return status."""
    is_healthy = await db_pool.health_check()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "checks": {
            "connection": is_healthy
        },
        "timestamp": asyncio.get_event_loop().time()
    }