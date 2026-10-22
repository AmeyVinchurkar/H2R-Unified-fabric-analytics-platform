# Implementation Guide – Build the H2R Platform in Microsoft Fabric (Step by Step)

> Written for first-time Fabric users. Estimated time: 3–4 hours.

## Prerequisites
- A Microsoft Fabric trial or capacity (start a free trial at app.fabric.microsoft.com → profile icon → *Free trial*)
- Power BI Desktop (optional – the report can be built in the browser)
- The `sample-data/` CSV files from this repository downloaded to your PC

---

## Step 1 – Create the workspace
1. Open **app.fabric.microsoft.com** → **Workspaces** → **+ New workspace**
2. Name: `WS_H2R_Analytics` → Advanced → choose your **Trial / Fabric capacity** → **Apply**

## Step 2 – Create the Lakehouse
1. In the workspace → **+ New item** → **Lakehouse**
2. Name: `lh_h2r` → **Create**

## Step 3 – Upload the source files
1. In `lh_h2r` → **Files** → `…` → **New subfolder** → `raw` → inside it create `h2r`
2. Open `Files/raw/h2r` → **Upload** → **Upload files** → select all 13 CSVs from `sample-data/` → **Upload**

> In a real project, Step 3 is done by the pipeline's **Copy data** activity from HRIS/ATS/LMS sources (see `pipeline-design.md`).

## Step 4 – Import the notebooks
1. Workspace → **Import** → **Notebook** → **From this computer**
2. Select the 4 `.ipynb` files in `notebooks/`
3. Open each notebook → left panel **Lakehouses** → **Add** → **Existing lakehouse** → `lh_h2r`
   (do this for all 4 notebooks)

## Step 5 – Run the Medallion layers
Run each notebook with **Run all**, in order:

| # | Notebook | Expected result |
|---|---|---|
| 1 | `01_bronze_ingestion` | 13 `bronze_*` tables + `ops_ingestion_audit` |
| 2 | `02_silver_transformation` | `silver_*` tables + `quarantine_employee` |
| 3 | `03_gold_dimensional_model` | 6 `dim_*` + 8 `fact_*` tables |
| 4 | `04_data_quality_checks` | `ops_dq_results` – all critical checks PASS |

Refresh **Tables** in the Lakehouse explorer to see them.

## Step 6 – Build the pipeline (orchestration)
1. Workspace → **+ New item** → **Data pipeline** → `pl_h2r_daily_load`
2. Add 4 **Notebook** activities, connect with **On success** arrows: Bronze → Silver → Gold → DQ
3. On the Bronze activity → **Settings → Base parameters**: `batch_id` = `@pipeline().RunId`, `load_mode` = `overwrite`
4. Add an **Office 365 Outlook** (or Teams) activity connected with **On fail** from each notebook → message: *H2R load failed – check run @{pipeline().RunId}*
5. **Run** once to test → **Schedule** → Daily, 06:00

## Step 7 – SQL views
1. Lakehouse → top-right switch **Lakehouse → SQL analytics endpoint**
2. **New SQL query** → paste `sql/01_gold_reporting_views.sql` → **Run**
3. Try queries from `sql/02_h2r_kpi_queries.sql` to validate numbers

## Step 8 – Semantic model
1. SQL analytics endpoint → **Reporting** tab → **New semantic model** → name `sm_h2r`
2. Select all `dim_*`, `fact_*`, `ops_dq_results`, `ops_ingestion_audit` → **Confirm**
3. Open the model → **Open data model** → create relationships (drag column to column):

| From (many) | To (one) |
|---|---|
| every `fact_*`[employee_id] | `dim_employee`[employee_id] |
| every `fact_*`[date_key] | `dim_date`[date_key] |
| `dim_employee`[department_id] | `dim_department`[department_id] |
| `dim_employee`[location_id] | `dim_location`[location_id] |
| `dim_employee`[grade_id] | `dim_grade`[grade_id] |
| `fact_training`[course_id] | `dim_course`[course_id] |

> `fact_recruitment` relates to `dim_date` only (candidates who were not hired have no employee).
4. Mark `dim_date` as date table: select table → **Mark as date table** → `date`
5. **New measure** → paste measures from `powerbi/h2r_dax_measures.dax` one by one
6. Optional RLS: **Manage roles** → role `Department Head` → filter `dim_department[department_name] = "Engineering"`

## Step 9 – Power BI report
Build the 5 pages described in `report-design.md`. Use the screenshots in `powerbi/screenshots/` as the layout reference.
After building, take your own screenshots and replace the preview images.

## Step 10 – Publish to GitHub
Push the project, then export your Fabric items to keep them version controlled:
Workspace settings → **Git integration** → connect to this GitHub repo → **Commit**.

## Troubleshooting
| Error | Fix |
|---|---|
| `Path does not exist: Files/raw/h2r/...` | Lakehouse not attached to notebook, or folder name differs |
| `Table or view not found: bronze_...` | Run notebook 01 first |
| DQ notebook raises exception | Open `ops_dq_results`, filter `status = 'FAIL'` to see which check |
| Measure shows blank | Check relationship direction and that `dim_date` is marked as date table |
