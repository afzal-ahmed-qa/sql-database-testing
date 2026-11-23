-- id: INT-04
-- title: The two "active" columns of a customer agree
-- severity: Major
-- known_defect: DQ-02
-- customer has both active (integer 0/1) and activebool (boolean); they must say the same.
SELECT customer_id, active, activebool
FROM customer
WHERE (active = 1) IS DISTINCT FROM activebool
ORDER BY customer_id;
