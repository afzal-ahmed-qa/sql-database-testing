"""Shared database fixtures."""

import sys
from pathlib import Path

import psycopg
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from db import connection_string  # noqa: E402


@pytest.fixture(scope="session")
def db():
    """One read-only connection for all checks."""
    with psycopg.connect(connection_string()) as conn:
        conn.read_only = True
        yield conn


@pytest.fixture
def tx():
    """A connection for write tests: everything is rolled back afterwards,
    so the database is the same before and after every test."""
    with psycopg.connect(connection_string()) as conn:
        try:
            yield conn
        finally:
            conn.rollback()
