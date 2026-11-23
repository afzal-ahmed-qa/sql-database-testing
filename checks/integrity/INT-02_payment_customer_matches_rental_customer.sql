-- id: INT-02
-- title: A payment is made by the customer who rented the film
-- severity: Major
-- known_defect: DQ-01
-- Returns payments whose customer differs from the rental's customer.
SELECT p.payment_id, p.rental_id, p.customer_id AS paid_by, r.customer_id AS rented_by, p.amount
FROM payment p
JOIN rental r ON r.rental_id = p.rental_id
WHERE p.customer_id <> r.customer_id
ORDER BY p.payment_id;
