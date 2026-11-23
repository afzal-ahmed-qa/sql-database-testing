-- id: BR-01
-- title: A film is not returned before it was rented
-- severity: Major
SELECT rental_id, rental_date, return_date
FROM rental
WHERE return_date < rental_date;
