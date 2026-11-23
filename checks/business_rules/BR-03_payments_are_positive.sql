-- id: BR-03
-- title: Every payment has a positive amount
-- severity: Major
-- known_defect: DQ-05
SELECT payment_id, customer_id, rental_id, amount
FROM payment
WHERE amount <= 0
ORDER BY payment_id;
