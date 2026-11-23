-- id: BR-05
-- title: Films are offered only at the shop's three price points
-- severity: Minor
SELECT film_id, title, rental_rate
FROM film
WHERE rental_rate NOT IN (0.99, 2.99, 4.99);
