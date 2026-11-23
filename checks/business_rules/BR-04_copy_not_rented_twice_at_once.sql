-- id: BR-04
-- title: One physical copy is not rented out again while it is still out
-- severity: Critical
-- known_defect: DQ-06
-- Window function: compare each rental of a copy with the previous rental of the same copy.
WITH ordered AS (
    SELECT rental_id, inventory_id, rental_date,
           lag(rental_id)   OVER w AS previous_rental_id,
           lag(return_date) OVER w AS previous_return_date
    FROM rental
    WINDOW w AS (PARTITION BY inventory_id ORDER BY rental_date)
)
SELECT inventory_id, previous_rental_id, rental_id, rental_date, previous_return_date
FROM ordered
WHERE previous_rental_id IS NOT NULL
  AND (previous_return_date IS NULL OR previous_return_date > rental_date)
ORDER BY inventory_id, rental_date;
