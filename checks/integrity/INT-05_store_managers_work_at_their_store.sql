-- id: INT-05
-- title: A store's manager is a staff member of that store
-- severity: Major
-- known_defect: DQ-03
SELECT st.store_id, st.manager_staff_id, sf.store_id AS manager_works_at
FROM store st
JOIN staff sf ON sf.staff_id = st.manager_staff_id
WHERE sf.store_id <> st.store_id
ORDER BY st.store_id;
