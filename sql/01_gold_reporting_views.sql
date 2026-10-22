/* =====================================================================
   H2R – Reporting views on the Fabric Lakehouse SQL analytics endpoint
   Run in: lh_h2r  →  SQL analytics endpoint  →  New SQL query
   ===================================================================== */

-- 1. Current workforce profile
CREATE OR ALTER VIEW dbo.vw_active_workforce AS
SELECT  e.employee_id, e.full_name, e.gender, e.age_band, e.tenure_band,
        d.department_name, d.business_unit, l.city, l.region,
        g.grade_name, g.grade_level, e.employment_type, e.work_mode, e.hire_date
FROM    dbo.dim_employee   e
JOIN    dbo.dim_department d ON d.department_id = e.department_id
JOIN    dbo.dim_location   l ON l.location_id   = e.location_id
JOIN    dbo.dim_grade      g ON g.grade_id      = e.grade_id
WHERE   e.is_active = 1;
GO

-- 2. Monthly headcount, hires, exits and attrition %
CREATE OR ALTER VIEW dbo.vw_monthly_workforce_movement AS
SELECT  h.month_end,
        SUM(CASE WHEN h.is_month_end_active = 1 THEN 1 ELSE 0 END)  AS closing_headcount,
        SUM(CASE WHEN h.is_new_hire = 1 THEN 1 ELSE 0 END)          AS hires,
        SUM(CASE WHEN h.is_exit = 1 THEN 1 ELSE 0 END)              AS exits,
        CAST(SUM(CASE WHEN h.is_exit = 1 THEN 1 ELSE 0 END) AS DECIMAL(10,2))
          / NULLIF(COUNT(*), 0) * 100                              AS monthly_attrition_pct
FROM    dbo.fact_headcount_monthly h
GROUP BY h.month_end;
GO

-- 3. Recruitment funnel by source channel
CREATE OR ALTER VIEW dbo.vw_recruitment_funnel AS
SELECT  source_channel,
        COUNT(*)                                             AS applicants,
        SUM(CASE WHEN stage_order >= 2 THEN 1 ELSE 0 END)    AS screened,
        SUM(CASE WHEN stage_order >= 3 THEN 1 ELSE 0 END)    AS interviewed,
        SUM(CASE WHEN stage_order >= 4 THEN 1 ELSE 0 END)    AS offered,
        SUM(CASE WHEN is_hired = 1 THEN 1 ELSE 0 END)        AS hired,
        AVG(CAST(time_to_hire_days AS FLOAT))                AS avg_time_to_hire_days
FROM    dbo.fact_recruitment
GROUP BY source_channel;
GO

-- 4. Attrition drivers
CREATE OR ALTER VIEW dbo.vw_exit_analysis AS
SELECT  d.department_name, x.exit_type, x.exit_reason,
        COUNT(*)                                                    AS exits,
        SUM(CASE WHEN x.regrettable_flag = 'Y' THEN 1 ELSE 0 END)   AS regrettable_exits,
        AVG(CAST(x.tenure_at_exit_years AS FLOAT))                  AS avg_tenure_at_exit,
        AVG(CAST(x.exit_interview_score AS FLOAT))                  AS avg_exit_score
FROM    dbo.fact_exit x
JOIN    dbo.dim_department d ON d.department_id = x.department_id
GROUP BY d.department_name, x.exit_type, x.exit_reason;
GO
