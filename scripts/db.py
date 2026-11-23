"""Connection settings from the standard PostgreSQL environment variables."""

import os


def _quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def connection_string(dbname: str | None = None) -> str:
    """Builds a libpq connection string.

    Values are quoted and empty settings are left out: in "password= dbname=x"
    libpq would read "dbname=x" as the password and connect to another database.
    """
    settings = {
        "host": os.getenv("PGHOST", "localhost"),
        "port": os.getenv("PGPORT", "5432"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", "postgres"),
        "dbname": dbname or os.getenv("PGDATABASE", "pagila"),
    }
    return " ".join(f"{key}={_quote(value)}" for key, value in settings.items() if value)
