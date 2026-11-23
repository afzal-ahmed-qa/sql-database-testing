"""Write tests: the database itself must refuse bad data.

Each test runs in a transaction that the `tx` fixture rolls back, so nothing
is stored. A savepoint lets a test go on after an expected error.
"""

import psycopg
import pytest
from psycopg import errors


def expect_error(tx, sql, params, error):
    with pytest.raises(error):
        with tx.transaction():  # savepoint: the outer transaction stays usable
            tx.execute(sql, params)


def test_w01_rental_of_unknown_customer_is_refused(tx):
    expect_error(
        tx,
        "INSERT INTO rental (rental_date, inventory_id, customer_id, staff_id) VALUES (now(), 1, %s, 1)",
        (99_999_999,),
        errors.ForeignKeyViolation,
    )


def test_w02_same_rental_twice_is_refused(tx):
    row = tx.execute("SELECT rental_date, inventory_id, customer_id, staff_id FROM rental LIMIT 1").fetchone()
    expect_error(
        tx,
        "INSERT INTO rental (rental_date, inventory_id, customer_id, staff_id) VALUES (%s, %s, %s, %s)",
        row,
        errors.UniqueViolation,
    )


def test_w03_customer_with_rentals_cannot_be_deleted(tx):
    customer_id = tx.execute("SELECT customer_id FROM rental LIMIT 1").fetchone()[0]
    expect_error(tx, "DELETE FROM customer WHERE customer_id = %s", (customer_id,), errors.ForeignKeyViolation)


def test_w04_update_sets_last_update(tx):
    before = tx.execute("SELECT last_update FROM customer WHERE customer_id = 1").fetchone()[0]
    # now() is fixed for the whole transaction, so compare with the trigger's own clock
    tx.execute("UPDATE customer SET first_name = first_name WHERE customer_id = 1")
    after = tx.execute("SELECT last_update FROM customer WHERE customer_id = 1").fetchone()[0]
    assert after > before


@pytest.mark.xfail(reason="DQ-08: no CHECK constraint stops negative payment amounts")
def test_w05_negative_payment_is_refused(tx):
    expect_error(
        tx,
        "INSERT INTO payment (customer_id, staff_id, rental_id, amount, payment_date) "
        "VALUES (1, 1, 1, %s, '2024-05-01')",
        (-5,),
        psycopg.errors.CheckViolation,
    )
