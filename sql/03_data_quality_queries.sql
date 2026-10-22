/* Data quality monitoring queries (SQL endpoint) */

-- Latest DQ run summary
SELECT check_name, table_name, severity, failed_rows, total_rows, status, run_ts
FROM   dbo.ops_dq_results
WHERE  run_ts = (SELECT MAX(run_ts) FROM dbo.ops_dq_results)
ORDER BY CASE status WHEN 'FAIL' THEN 0 ELSE 1 END, severity;

-- Ingestion volume trend (spot missing / partial loads)
SELECT table_name, CAST(loaded_at AS DATE) AS load_date, row_count,
       row_count - LAG(row_count) OVER (PARTITION BY table_name ORDER BY loaded_at) AS change_vs_previous
FROM   dbo.ops_ingestion_audit
ORDER BY table_name, loaded_at DESC;

-- Records quarantined
SELECT _reason, COUNT(*) AS records FROM dbo.quarantine_employee GROUP BY _reason;

-- Orphan facts (should return 0 rows)
SELECT 'fact_payroll' AS fact_table, COUNT(*) AS orphans
FROM dbo.fact_payroll p WHERE NOT EXISTS (SELECT 1 FROM dbo.dim_employee e WHERE e.employee_id = p.employee_id)
UNION ALL
SELECT 'fact_training', COUNT(*)
FROM dbo.fact_training t WHERE NOT EXISTS (SELECT 1 FROM dbo.dim_employee e WHERE e.employee_id = t.employee_id);
