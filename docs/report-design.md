# Power BI Report Design – H2R Workforce Analytics

**Theme:** Navy header `#1B2A49`, accents Blue `#0F6CBD`, Teal `#0E9F8E`, Purple `#6B4FBB`, Orange `#E8833A`, Red `#D13438`
**Global slicers (sync across pages):** Fiscal Year, Business Unit, Department, Region, Grade

| Page | KPI cards | Visuals |
|---|---|---|
| 1. Executive Overview | Headcount, Hires, Exits, Attrition % (R12M), Female %, Avg Tenure | Headcount line + hires/exits columns; Headcount by department; Region donut; Grade pyramid; Gender by BU |
| 2. Talent Acquisition & Onboarding | Applicants, Hired, Offer Acceptance %, Applicant→Hire %, Induction %, Onboarding Score | Funnel; Hires & conversion by source (combo); Hires per quarter; Onboarding score histogram |
| 3. Learning & Performance | Training Completion %, Assessment Score, Avg Rating, High Performer %, Promotion Rate % | Completion by course; Rating distribution by cycle (100% stacked); Learning hours by category; Promotion rate by rating |
| 4. Attrition, Retention & Exit | Exits, Attrition %, Voluntary %, Regrettable Exits, Early Attrition %, KT Completed % | Rolling 12M attrition line; Exit reasons; Attrition by department; Payroll cost trend |
| 5. Data Health | DQ Checks Failed, Last Refresh | Table of `ops_dq_results` (conditional formatting on status); Rows loaded per table over time |

**Interactions:** drill-through from department → employee-level detail page (secured with RLS); tooltips showing PY comparison.
