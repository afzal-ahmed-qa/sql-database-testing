-- id: INT-03
-- title: No two customers share an e-mail address (case-insensitive)
-- severity: Major
SELECT lower(email) AS email, count(*) AS customers
FROM customer
GROUP BY lower(email)
HAVING count(*) > 1;
