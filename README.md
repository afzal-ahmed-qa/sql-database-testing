# SQL database testing with PostgreSQL

[![SQL Checks](https://github.com/afzal-ahmed-qa/sql-database-testing/actions/workflows/sql-checks.yml/badge.svg)](https://github.com/afzal-ahmed-qa/sql-database-testing/actions/workflows/sql-checks.yml)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-8.4-0A9EDC?logo=pytest&logoColor=white)

Data-quality and database tests for [Pagila](https://github.com/devrimgunduz/pagila), a sample
database of a DVD rental shop: 1,000 films, 999 customers, 51,805 rentals and 51,061 payments.
GitHub Actions starts PostgreSQL 18, loads Pagila, runs every check, and publishes the report:
https://afzal-ahmed-qa.github.io/sql-database-testing/

In my UI and API projects I check what an application shows. This one checks what it stores:
whether the data is complete, consistent and follows the business rules, and whether the
database itself refuses bad data. It found **8 real defects**, listed in [docs/defects.md](docs/defects.md).

## What's checked

| Area | Checks | Examples |
|---|---|---|
| Schema | SCH-01..03 | every table has a primary key; required columns are NOT NULL; rentals and payments have their foreign keys |
| Integrity | INT-01..05 | no orphan rentals; a payment is made by the customer who rented; unique e-mails; two "active" flags agree; store managers work at their store |
| Business rules | BR-01..06 | no return before rental; no payment before rental; positive amounts; a copy is not rented twice at once; valid prices and e-mails |
| Reconciliation | REC-01..02 | the two sales reports add up to the real payments |
| Write rules | W-01..05 | the database refuses unknown customers, duplicate rentals, deleting customers with rentals and negative amounts; updates set `last_update` |

21 tests: 13 pass, 8 document a defect.

## How it works

Each check in `checks/` is a plain SQL file that **returns the rows that break a rule**, so no rows
means the rule holds. The header names it:

```sql
-- id: BR-04
-- title: One physical copy is not rented out again while it is still out
-- severity: Critical
-- known_defect: DQ-06
WITH ordered AS (
    SELECT rental_id, inventory_id, rental_date,
           lag(rental_id)   OVER w AS previous_rental_id,
           lag(return_date) OVER w AS previous_return_date
    FROM rental
    WINDOW w AS (PARTITION BY inventory_id ORDER BY rental_date)
)
SELECT ... WHERE previous_return_date IS NULL OR previous_return_date > rental_date;
```

`tests/test_sql_checks.py` runs every file as its own pytest test and reports how many rows broke
the rule, with the first five as examples. A check with `known_defect` is marked as an expected
failure, and `xfail_strict` makes it fail the day the defect is gone, so the defect list stays true.

The write tests in `tests/test_write_rules.py` insert, update and delete inside a transaction that
is always rolled back, with a savepoint around each expected error, so the database is never changed.

SQL used: joins and anti-joins (`LEFT JOIN … WHERE … IS NULL`), `GROUP BY … HAVING`, CTEs, window
functions (`lag() OVER (PARTITION BY … ORDER BY …)`), `IS DISTINCT FROM` for NULL-safe comparison,
`FULL JOIN` for reconciliation, regular expressions, and `information_schema` for schema checks.

## Two problems I ran into

**A connection string that connected to the wrong database.** With an empty password the string
read `password= dbname=pagila`, and libpq took `dbname=pagila` as the password. The schema went into
another database, and the next load failed on objects that "already existed". `scripts/db.py` now
quotes every value and leaves empty ones out.

**Matching report rows by name.** `sales_by_store` labels stores as "city,country", and Pagila has
several stores in some cities, so looking a store up by its label matched the wrong ones. REC-01
builds the same label from the stores that actually have sales and compares by label.

## Running it

You need PostgreSQL 17 or newer (the dump uses `transaction_timeout`; 18 with pgvector loads it unchanged) and Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PGHOST=localhost PGPORT=5432 PGUSER=postgres PGPASSWORD=postgres
python scripts/load_pagila.py                    # add --without-vector if pgvector is not installed
pytest -v                                        # all checks
pytest -v -k "BR-"                               # one area
pytest --html=report/index.html --self-contained-html
```

With Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:pg18`.

---

Afzal Ahmed, [github.com/afzal-ahmed-qa](https://github.com/afzal-ahmed-qa)
