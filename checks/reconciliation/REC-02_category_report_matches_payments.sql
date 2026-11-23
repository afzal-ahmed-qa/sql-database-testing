-- id: REC-02
-- title: The sales_by_film_category report adds up to the total payments
-- severity: Major
-- known_defect: DQ-07
-- Returns one row if the two totals differ.
SELECT payments.total AS payments_total, report.total AS report_total,
       round(report.total / payments.total, 2) AS ratio
FROM (SELECT sum(amount) AS total FROM payment) payments,
     (SELECT sum(total_sales) AS total FROM sales_by_film_category) report
WHERE payments.total IS DISTINCT FROM report.total;
