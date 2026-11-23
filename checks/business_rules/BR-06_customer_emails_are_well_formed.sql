-- id: BR-06
-- title: Customer e-mail addresses are well formed
-- severity: Minor
SELECT customer_id, email
FROM customer
WHERE email IS NULL OR email !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$';
