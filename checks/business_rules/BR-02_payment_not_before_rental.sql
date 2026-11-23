-- id: BR-02
-- title: A rental is not paid before it starts
-- severity: Major
-- known_defect: DQ-04
SELECT p.payment_id, p.rental_id, p.payment_date, r.rental_date,
       round(extract(epoch FROM r.rental_date - p.payment_date) / 86400, 1) AS days_early
FROM payment p
JOIN rental r ON r.rental_id = p.rental_id
WHERE p.payment_date < r.rental_date
ORDER BY days_early DESC;
