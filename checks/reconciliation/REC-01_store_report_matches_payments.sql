-- id: REC-01
-- title: The sales_by_store report adds up to the payments, per store
-- severity: Critical
-- Returns each store where the report and the raw payments differ.
-- Stores are matched by the report's "city,country" label. Pagila has several
-- stores in some cities, so the label is built from the stores that have sales,
-- not looked up from the label (that would match the wrong stores).
WITH raw AS (
    SELECT c.city || ',' || cy.country AS store, sum(p.amount) AS total
    FROM payment p
    JOIN rental r    ON r.rental_id = p.rental_id
    JOIN inventory i ON i.inventory_id = r.inventory_id
    JOIN store s     ON s.store_id = i.store_id
    JOIN address a   ON a.address_id = s.address_id
    JOIN city c      ON c.city_id = a.city_id
    JOIN country cy  ON cy.country_id = c.country_id
    GROUP BY 1
)
SELECT coalesce(raw.store, v.store) AS store, raw.total AS payments, v.total_sales AS report
FROM raw
FULL JOIN sales_by_store v ON v.store = raw.store
WHERE raw.total IS DISTINCT FROM v.total_sales;
