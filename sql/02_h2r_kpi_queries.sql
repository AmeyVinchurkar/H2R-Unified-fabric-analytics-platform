/* H2R KPI queries – ad-hoc analysis & report validation (T-SQL, Fabric SQL endpoint) */

-- Annualised attrition rate by fiscal year  = exits / average headcount
WITH m AS (
    SELECT d.fiscal_year, h.month_end,
           COUNT(*)                                    AS headcount,
           SUM(CASE WHEN h.is_exit = 1 THEN 1 ELSE 0 END) AS exits
    FROM   dbo.fact_headcount_monthly h
    JOIN   dbo.dim_date d ON d.date_key = h.date_key
    GROUP BY d.fiscal_year, h.month_end
)
SELECT fiscal_year,
       AVG(CAST(headcount AS FLOAT))                          AS avg_headcount,
       SUM(exits)                                             AS exits,
       ROUND(SUM(exits) * 100.0 / AVG(CAST(headcount AS FLOAT)), 1) AS attrition_pct
FROM   m
GROUP BY fiscal_year
ORDER BY fiscal_year;

-- Early attrition: % of hires leaving inside first year (onboarding effectiveness)
SELECT YEAR(e.hire_date) AS hire_year,
       COUNT(*) AS hires,
       SUM(CASE WHEN DATEDIFF(day, e.hire_date, e.termination_date) < 365 THEN 1 ELSE 0 END) AS left_within_1yr,
       ROUND(SUM(CASE WHEN DATEDIFF(day, e.hire_date, e.termination_date) < 365 THEN 1.0 ELSE 0 END)
             * 100 / COUNT(*), 1) AS early_attrition_pct
FROM   dbo.dim_employee e
GROUP BY YEAR(e.hire_date)
ORDER BY hire_year;

-- Performance vs attrition: do high performers leave?
SELECT p.performance_rating,
       COUNT(DISTINCT p.employee_id) AS employees_rated,
       COUNT(DISTINCT x.employee_id) AS later_exited,
       ROUND(COUNT(DISTINCT x.employee_id) * 100.0 / COUNT(DISTINCT p.employee_id), 1) AS exit_pct
FROM   dbo.fact_performance p
LEFT JOIN dbo.fact_exit x ON x.employee_id = p.employee_id
GROUP BY p.performance_rating
ORDER BY p.performance_rating;

-- Learning hours per active employee by department
SELECT d.department_name,
       SUM(t.learning_hours) * 1.0 / COUNT(DISTINCT e.employee_id) AS learning_hours_per_employee,
       ROUND(AVG(CASE WHEN t.is_completed = 1 THEN 100.0 ELSE 0 END), 1) AS completion_pct
FROM   dbo.dim_employee e
JOIN   dbo.dim_department d ON d.department_id = e.department_id
LEFT JOIN dbo.fact_training t ON t.employee_id = e.employee_id
WHERE  e.is_active = 1
GROUP BY d.department_name
ORDER BY learning_hours_per_employee DESC;

-- Cost of workforce: gross pay trend by business unit
SELECT d.fiscal_year, dp.business_unit,
       SUM(p.gross_pay) AS total_gross_pay,
       SUM(p.gross_pay) / COUNT(DISTINCT p.employee_id) AS avg_cost_per_employee
FROM   dbo.fact_payroll p
JOIN   dbo.dim_date d       ON d.date_key = p.date_key
JOIN   dbo.dim_employee e   ON e.employee_id = p.employee_id
JOIN   dbo.dim_department dp ON dp.department_id = e.department_id
GROUP BY d.fiscal_year, dp.business_unit
ORDER BY d.fiscal_year, dp.business_unit;

-- Top 10 managers by regrettable exits in their teams
SELECT TOP 10 m.full_name AS manager, COUNT(*) AS regrettable_exits
FROM   dbo.fact_exit x
JOIN   dbo.dim_employee e ON e.employee_id = x.employee_id
JOIN   dbo.dim_employee m ON m.employee_id = e.manager_id
WHERE  x.regrettable_flag = 'Y'
GROUP BY m.full_name
ORDER BY regrettable_exits DESC;
