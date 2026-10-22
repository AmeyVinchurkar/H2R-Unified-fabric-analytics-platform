# Pipeline Design – `pl_h2r_daily_load`

```
[Copy: HRIS] ─┐
[Copy: ATS ] ─┤
[Copy: LMS ] ─┼─► [NB 01 Bronze] ─► [NB 02 Silver] ─► [NB 03 Gold] ─► [NB 04 DQ] ─► [Refresh semantic model]
[Copy: TNA ] ─┤          │                 │                │              │
[Copy: PERF] ─┤          └──── on fail ────┴──── on fail ───┴── on fail ───┴──► [Teams / Outlook alert]
[Copy: PAY ] ─┘
```

| Setting | Value |
|---|---|
| Schedule | Daily 06:00 IST |
| Parameters | `batch_id = @pipeline().RunId`, `load_mode = overwrite` (full) / `append` (incremental) |
| Retry | 2 retries, 5-minute interval on notebook activities |
| Fail-fast | Notebook 04 raises an exception on any CRITICAL DQ failure → pipeline fails → alert |
| Landing zone | `Files/raw/h2r/<source>.csv` |
| Observability | `ops_ingestion_audit` (row counts per load), `ops_dq_results` (check outcomes) |

### Incremental strategy (production extension)
- Payroll, leave and training are append-only → load only new `pay_month` / `leave_start_date` using a watermark table
- Employee master changes → Delta `MERGE` on `employee_id` (SCD Type 1); extend to SCD Type 2 for grade/department history
