-- id: SCH-01
-- title: Every table has a primary key
-- severity: Major
-- Returns each base table in "public" without a primary key.
SELECT t.table_name
FROM information_schema.tables t
LEFT JOIN information_schema.table_constraints c
       ON c.table_schema = t.table_schema
      AND c.table_name = t.table_name
      AND c.constraint_type = 'PRIMARY KEY'
WHERE t.table_schema = 'public'
  AND t.table_type = 'BASE TABLE'
  AND c.constraint_name IS NULL
ORDER BY t.table_name;
