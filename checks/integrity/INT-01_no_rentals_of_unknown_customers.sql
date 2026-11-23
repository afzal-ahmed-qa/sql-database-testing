-- id: INT-01
-- title: Every rental belongs to an existing customer
-- severity: Critical
-- Anti-join: rentals whose customer row does not exist.
SELECT r.rental_id, r.customer_id
FROM rental r
LEFT JOIN customer c ON c.customer_id = r.customer_id
WHERE c.customer_id IS NULL;
