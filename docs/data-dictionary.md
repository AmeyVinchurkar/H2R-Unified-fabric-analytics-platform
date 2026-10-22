# Data Dictionary

## Source files (Bronze)
| File | System | Grain | Key columns |
|---|---|---|---|
| hris_employees | HRIS | Employee | employee_id, hire_date, termination_date, department_id, grade_id, manager_id |
| hris_departments / locations / grades | HRIS | Reference | department_id / location_id / grade_id |
| hris_onboarding | HRIS | Employee | induction_completed, buddy_assigned, onboarding_survey_score |
| hris_exits | HRIS | Exit event | exit_type, exit_reason, regrettable_flag, kt_completed |
| ats_requisitions | ATS | Requisition | requisition_id, opened_date, requisition_status |
| ats_candidates | ATS | Candidate application | candidate_id, source_channel, current_stage, offer_status |
| lms_courses | LMS | Course | course_id, course_category, duration_hours |
| lms_training_records | LMS | Employee × course | completion_status, assessment_score |
| tna_leave_records | Time & Attendance | Leave request | leave_type, leave_days, approval_status |
| perf_reviews | Performance | Employee × cycle | performance_rating (1–5), goal_achievement_pct, promoted_flag |
| payroll_monthly | Payroll | Employee × month | base_pay, benefits, bonus, overtime_pay, deductions |

## Gold model
| Table | Grain | Notes |
|---|---|---|
| dim_employee | Employee | Gender standardised, age/tenure bands, is_active |
| dim_date | Day | Fiscal year Apr–Mar (`FY26` = Apr-25 to Mar-26) |
| fact_headcount_monthly | Employee × month-end | is_new_hire, is_exit, is_month_end_active – drives attrition |
| fact_recruitment | Candidate | is_offered, is_hired, time_to_hire_days, time_to_fill_days |
| fact_training | Employee × course | learning_hours only counted when completed |
| fact_payroll | Employee × month | gross_pay, net_pay derived in Silver |
| fact_exit | Exit | tenure_at_exit_years |

## Key KPI definitions
| KPI | Formula |
|---|---|
| Attrition % | Exits ÷ Average monthly headcount for the period |
| Early Attrition % | Exits with tenure < 1 year ÷ Total exits |
| Offer Acceptance % | Hired ÷ Offered |
| Time to Hire | Hire date − Applied date |
| Time to Fill | Hire date − Requisition opened date |
| Training Completion % | Completed enrolments ÷ Total enrolments |
| High Performer % | Ratings ≥ 4 ÷ All ratings |
