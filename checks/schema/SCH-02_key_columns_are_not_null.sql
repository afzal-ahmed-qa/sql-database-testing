-- id: SCH-02
-- title: Columns that every row needs are NOT NULL
-- severity: Major
-- Returns each listed column that allows NULL.
WITH required(table_name, column_name) AS (
    VALUES ('rental', 'rental_date'), ('rental', 'inventory_id'), ('rental', 'customer_id'),
           ('payment', 'customer_id'), ('payment', 'amount'), ('payment', 'payment_date'),
           ('inventory', 'film_id'), ('inventory', 'store_id'),
           ('customer', 'first_name'), ('customer', 'last_name'), ('film', 'title')
)
SELECT r.table_name, r.column_name, c.is_nullable
FROM required r
JOIN information_schema.columns c
  ON c.table_schema = 'public' AND c.table_name = r.table_name AND c.column_name = r.column_name
WHERE c.is_nullable = 'YES';
