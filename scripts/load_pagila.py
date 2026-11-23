"""Download the Pagila sample database and load it into PostgreSQL.

The files come from a fixed commit of https://github.com/devrimgunduz/pagila,
so every run tests the same data.

    python scripts/load_pagila.py                    # uses PG* env vars or localhost:5432
    python scripts/load_pagila.py --without-vector   # for servers without pgvector

Pagila's newest schema has one table, film_embedding, that needs the pgvector
extension. None of the checks use it, so --without-vector leaves it out.
"""

from __future__ import annotations

import argparse
import re
import time
import urllib.request
from pathlib import Path

import psycopg

from db import connection_string

PAGILA_COMMIT = "6ea53f812254c91a602f61c0ef62beca3fa676b1"
FILES = ["pagila-schema.sql", "pagila-insert-data.sql"]
CACHE = Path(__file__).resolve().parent.parent / ".pagila"


def download() -> dict[str, str]:
    CACHE.mkdir(exist_ok=True)
    texts = {}
    for name in FILES:
        target = CACHE / f"{PAGILA_COMMIT[:12]}-{name}"
        if not target.exists():
            url = f"https://raw.githubusercontent.com/devrimgunduz/pagila/{PAGILA_COMMIT}/{name}"
            print(f"Downloading {url}")
            urllib.request.urlretrieve(url, target)
        texts[name] = target.read_text(encoding="utf-8")
    return texts


def without_vector(schema: str) -> str:
    """Drops the statements that need pgvector. pg_dump ends each statement with ';' and a blank line."""
    statements = re.split(r";\n\n", schema)
    keep = [s for s in statements if "film_embedding" not in s and not re.search(r"EXTENSION\s+(IF NOT EXISTS\s+)?vector", s)]
    return ";\n\n".join(keep)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--without-vector", action="store_true", help="skip the film_embedding table (no pgvector)")
    parser.add_argument("--recreate", action="store_true", help="drop and recreate the database first")
    args = parser.parse_args()

    texts = download()
    schema = texts["pagila-schema.sql"]
    data = texts["pagila-insert-data.sql"]
    if args.without_vector:
        schema = without_vector(schema)
        data = "\n".join(line for line in data.splitlines() if not line.startswith("INSERT INTO public.film_embedding"))

    dbname = "pagila"
    with psycopg.connect(connection_string("postgres"), autocommit=True) as admin:
        exists = admin.execute("select 1 from pg_database where datname = %s", (dbname,)).fetchone()
        if exists and args.recreate:
            admin.execute(f"drop database {dbname} with (force)")
            exists = None
        if not exists:
            admin.execute(f"create database {dbname}")

    started = time.time()
    with psycopg.connect(connection_string(dbname), autocommit=True) as conn:
        conn.execute(schema)
        conn.execute(data)
    # The dump empties search_path for its own session, so count in a fresh one.
    with psycopg.connect(connection_string(dbname)) as conn:
        counts = {t: conn.execute(f"select count(*) from {t}").fetchone()[0] for t in ("film", "customer", "rental", "payment")}
    print(f"Loaded Pagila in {time.time() - started:.1f}s: {counts}")


if __name__ == "__main__":
    main()
