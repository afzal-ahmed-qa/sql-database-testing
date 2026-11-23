-- id: SCH-03
-- title: Rentals and payments are tied to their parents by foreign keys
-- severity: Critical
-- Returns each expected foreign key that is missing.
WITH expected(child, child_column, parent) AS (
    VALUES ('rental', 'customer_id', 'customer'), ('rental', 'inventory_id', 'inventory'),
           ('rental', 'staff_id', 'staff'), ('payment', 'customer_id', 'customer'),
           ('payment', 'rental_id', 'rental'), ('inventory', 'film_id', 'film')
),
actual AS (
    SELECT kcu.table_name AS child, kcu.column_name AS child_column, ccu.table_name AS parent
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema
    JOIN information_schema.constraint_column_usage ccu
      ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public'
)
SELECT e.*
FROM expected e
WHERE NOT EXISTS (
    SELECT 1 FROM actual a
    WHERE a.parent = e.parent AND a.child_column = e.child_column
      AND (a.child = e.child OR a.child LIKE e.child || '_p%')  -- payment is partitioned
);
