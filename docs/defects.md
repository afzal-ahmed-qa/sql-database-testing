# Data-quality defects in Pagila

Found by the checks in this repository against Pagila at commit
`6ea53f8` ([devrimgunduz/pagila](https://github.com/devrimgunduz/pagila)), loaded into PostgreSQL 18.
Pagila is sample data, so these are recorded for practice rather than raised with a vendor.
Each defect has a check that is marked as a known defect: it turns red once the data is fixed.

| ID | Defect | Rows | Severity | Check |
|---|---|---|---|---|
| DQ-01 | Rental 4591 was paid by five different customers, none of whom rented it | 5 payments | Major | INT-02 |
| DQ-02 | `customer.active` (0/1) and `customer.activebool` disagree | 43 customers | Major | INT-04 |
| DQ-03 | The managers of stores 1 and 2 are staff of stores 25 and 33 | 2 stores | Major | INT-05 |
| DQ-04 | Payments dated before their rental starts (average 94 days, up to 211) | 14,665 payments | Major | BR-02 |
| DQ-05 | Payments with an amount of 0.00 | 24 payments | Major | BR-03 |
| DQ-06 | A physical copy is rented out again while it is still out | 1,238 rentals | Critical | BR-04 |
| DQ-07 | `sales_by_film_category` counts a film's revenue once per category: 405,100.72 against 170,962.39 in payments (2.37×) | whole report | Major | REC-02 |
| DQ-08 | No CHECK constraint stops negative payment amounts | schema | Major | W-05 |

---

### DQ-01, One rental paid by five other customers

```sql
SELECT p.payment_id, p.rental_id, p.customer_id AS paid_by, r.customer_id AS rented_by
FROM payment p JOIN rental r USING (rental_id)
WHERE p.customer_id <> r.customer_id;
```
**Expected:** no rows; a rental is paid by the customer who rented it.
**Actual:** rental 4591 (customer 182) has payments 17206, 19518, 25162, 29163 and 31834 from
customers 577, 16, 259, 401 and 546. Revenue per customer and any "customer balance" is wrong for six customers.

### DQ-02, Two "active" flags that disagree

`customer` has both `active` (integer) and `activebool` (boolean). 32 customers are `0 / true`
and 11 are `1 / false`. Which one a report uses decides whether those 43 customers count as active.

### DQ-03, Store managers who work for another store

`store.manager_staff_id` for stores 1 and 2 points to staff 1 and 2, but `staff.store_id` puts
them in stores 25 and 33. Since only stores 1 and 2 hold inventory, every one of the 51,805
rentals is processed by a member of staff assigned to a different store.

### DQ-04, Paid before rented

14,665 of 51,061 payments (29%) are dated before the rental they pay for: on average 94 days
earlier, at most 211. Prepayment is not part of the business model, so the dates of one of the
two tables are unreliable, and any revenue-by-month report shifts revenue into earlier months.

### DQ-05, Zero payments

24 payments have `amount = 0.00`. Either they should not exist, or they need a reason
(a voucher, a refund) that the schema does not record.

### DQ-06, The same copy rented twice at once

Using `lag()` over each copy's rentals in date order: 1,238 rentals start before the previous
rental of the same copy was returned, 187 of them while the previous rental is still open.
Example: copy 5 was rented on 2022-12-22 16:41 while the previous rental ran until 2022-12-23 18:03.
Physically impossible; stock and availability reports built on this data are wrong.

### DQ-07, A sales report that counts revenue up to three times

```sql
SELECT (SELECT sum(amount) FROM payment), (SELECT sum(total_sales) FROM sales_by_film_category);
-- 170962.39 | 405100.72
```
The view joins payments to `film_category`. 561 films have two categories and 403 have three, so
their revenue is added to every category. The sum of the report is 2.37 times the real revenue.
`sales_by_store` adds up correctly (REC-01), so the payments themselves are not the problem.

### DQ-08, Negative payments are accepted

```sql
INSERT INTO payment (customer_id, staff_id, rental_id, amount, payment_date)
VALUES (1, 1, 1, -5, '2024-05-01');   -- succeeds
```
Run inside a rolled-back transaction by W-05. A `CHECK (amount >= 0)` would stop it.
