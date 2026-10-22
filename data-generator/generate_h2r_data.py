"""
Hire-to-Retire (H2R) synthetic data generator.

Creates realistic, fully synthetic HR source files that simulate data coming from
HRIS, Recruitment (ATS), Learning (LMS), Time & Attendance, Performance and Payroll
systems. No real employee or company data is used.

Usage:
    python generate_h2r_data.py --employees 1500 --out ../sample-data
"""
import argparse
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

FIRST = ["Aarav", "Vivaan", "Aditya", "Diya", "Ananya", "Ishaan", "Kavya", "Rohan", "Sneha", "Neha",
         "Arjun", "Priya", "Rahul", "Meera", "Karan", "Pooja", "Siddharth", "Riya", "Varun", "Tanvi",
         "James", "Olivia", "Liam", "Emma", "Noah", "Sophia", "Lucas", "Mia", "Ethan", "Ava"]
LAST = ["Sharma", "Patil", "Kulkarni", "Iyer", "Reddy", "Nair", "Mehta", "Joshi", "Deshmukh", "Rao",
        "Gupta", "Singh", "Kapoor", "Menon", "Shah", "Smith", "Brown", "Wilson", "Taylor", "Clark"]

DEPARTMENTS = [
    ("D01", "Engineering", "Technology"), ("D02", "Data & Analytics", "Technology"),
    ("D03", "Quality Assurance", "Technology"), ("D04", "Sales", "Business"),
    ("D05", "Marketing", "Business"), ("D06", "Finance", "Corporate"),
    ("D07", "Human Resources", "Corporate"), ("D08", "Customer Success", "Business"),
    ("D09", "Delivery Excellence", "Operations"), ("D10", "IT Operations", "Operations"),
]
DEPT_WEIGHTS = [0.24, 0.12, 0.10, 0.10, 0.06, 0.06, 0.05, 0.10, 0.08, 0.09]

LOCATIONS = [
    ("L01", "Pune", "India", "APAC"), ("L02", "Bengaluru", "India", "APAC"),
    ("L03", "Hyderabad", "India", "APAC"), ("L04", "Chennai", "India", "APAC"),
    ("L05", "London", "United Kingdom", "EMEA"), ("L06", "New York", "United States", "Americas"),
]
LOC_WEIGHTS = [0.30, 0.22, 0.16, 0.12, 0.10, 0.10]

GRADES = [("G1", "Associate", 1), ("G2", "Senior Associate", 2), ("G3", "Consultant", 3),
          ("G4", "Senior Consultant", 4), ("G5", "Manager", 5), ("G6", "Senior Manager", 6),
          ("G7", "Director", 7)]
GRADE_WEIGHTS = [0.22, 0.24, 0.20, 0.16, 0.10, 0.06, 0.02]
GRADE_SALARY = {"G1": 450000, "G2": 700000, "G3": 1000000, "G4": 1450000,
                "G5": 2100000, "G6": 3000000, "G7": 4500000}  # annual base, INR equivalent

SOURCES = ["Employee Referral", "Job Portal", "LinkedIn", "Campus", "Consultant", "Careers Site"]
SOURCE_W = [0.22, 0.25, 0.20, 0.12, 0.11, 0.10]
EXIT_REASONS = ["Better Opportunity", "Higher Studies", "Relocation", "Compensation",
                "Career Growth", "Personal Reasons", "Performance", "Retirement"]
EXIT_W = [0.28, 0.06, 0.10, 0.18, 0.20, 0.10, 0.05, 0.03]
COURSES = [("C01", "Microsoft Fabric Fundamentals", "Technical", 16),
           ("C02", "Power BI Advanced", "Technical", 12), ("C03", "Data Engineering with PySpark", "Technical", 20),
           ("C04", "Leadership Essentials", "Leadership", 8), ("C05", "Information Security Awareness", "Compliance", 2),
           ("C06", "POSH Awareness", "Compliance", 2), ("C07", "Client Communication", "Soft Skills", 6),
           ("C08", "Agile Delivery", "Process", 10), ("C09", "Generative AI for Business", "Technical", 8),
           ("C10", "Code of Conduct", "Compliance", 1)]
LEAVE_TYPES = [("Earned Leave", 0.45), ("Sick Leave", 0.25), ("Casual Leave", 0.22), ("Unpaid Leave", 0.08)]

START = date(2021, 4, 1)
END = date(2026, 3, 31)


def rand_date(start, end, size):
    span = (end - start).days
    return [start + timedelta(days=int(d)) for d in rng.integers(0, span, size)]


def generate(n_emp, out):
    os.makedirs(out, exist_ok=True)

    # ---------- Reference data ----------
    pd.DataFrame(DEPARTMENTS, columns=["department_id", "department_name", "business_unit"]) \
        .to_csv(f"{out}/hris_departments.csv", index=False)
    pd.DataFrame(LOCATIONS, columns=["location_id", "city", "country", "region"]) \
        .to_csv(f"{out}/hris_locations.csv", index=False)
    pd.DataFrame(GRADES, columns=["grade_id", "grade_name", "grade_level"]) \
        .to_csv(f"{out}/hris_grades.csv", index=False)
    pd.DataFrame(COURSES, columns=["course_id", "course_name", "course_category", "duration_hours"]) \
        .to_csv(f"{out}/lms_courses.csv", index=False)

    # ---------- Recruitment (ATS): requisitions + candidates ----------
    n_cand = int(n_emp * 4.5)
    req_ids = [f"REQ{str(i).zfill(5)}" for i in range(1, int(n_emp * 1.1) + 1)]
    req_open = rand_date(START - timedelta(days=60), END - timedelta(days=30), len(req_ids))
    reqs = pd.DataFrame({
        "requisition_id": req_ids,
        "department_id": rng.choice([d[0] for d in DEPARTMENTS], len(req_ids), p=DEPT_WEIGHTS),
        "location_id": rng.choice([l[0] for l in LOCATIONS], len(req_ids), p=LOC_WEIGHTS),
        "grade_id": rng.choice([g[0] for g in GRADES], len(req_ids), p=GRADE_WEIGHTS),
        "opened_date": req_open,
        "requisition_status": rng.choice(["Filled", "Open", "Cancelled"], len(req_ids), p=[0.82, 0.10, 0.08]),
    })
    reqs.to_csv(f"{out}/ats_requisitions.csv", index=False)

    cand = pd.DataFrame({
        "candidate_id": [f"CAN{str(i).zfill(6)}" for i in range(1, n_cand + 1)],
        "requisition_id": rng.choice(req_ids, n_cand),
        "source_channel": rng.choice(SOURCES, n_cand, p=SOURCE_W),
        "gender": rng.choice(["Male", "Female", "Non-binary"], n_cand, p=[0.56, 0.42, 0.02]),
    })
    cand = cand.merge(reqs[["requisition_id", "opened_date"]], on="requisition_id")
    cand["applied_date"] = [o + timedelta(days=int(d)) for o, d in zip(cand.opened_date, rng.integers(1, 30, n_cand))]
    stage = rng.choice(["Applied", "Screened", "Interviewed", "Offered", "Hired"], n_cand,
                       p=[0.38, 0.24, 0.18, 0.06, 0.14])
    cand["current_stage"] = stage
    cand["offer_status"] = np.where(np.isin(stage, ["Offered", "Hired"]),
                                    np.where(stage == "Hired", "Accepted",
                                             rng.choice(["Declined", "Pending"], n_cand, p=[0.7, 0.3])), None)
    cand = cand.drop(columns="opened_date")

    # ---------- HRIS: employees ----------
    hire_dates = sorted(rand_date(START, END - timedelta(days=15), n_emp))
    dept = rng.choice([d[0] for d in DEPARTMENTS], n_emp, p=DEPT_WEIGHTS)
    grade = rng.choice([g[0] for g in GRADES], n_emp, p=GRADE_WEIGHTS)
    emp = pd.DataFrame({
        "employee_id": [f"E{str(i).zfill(6)}" for i in range(1, n_emp + 1)],
        "first_name": rng.choice(FIRST, n_emp),
        "last_name": rng.choice(LAST, n_emp),
        "gender": rng.choice(["Male", "Female", "Non-binary"], n_emp, p=[0.58, 0.40, 0.02]),
        "date_of_birth": [date(1970, 1, 1) + timedelta(days=int(d)) for d in rng.integers(0, 365 * 32, n_emp)],
        "hire_date": hire_dates,
        "department_id": dept,
        "location_id": rng.choice([l[0] for l in LOCATIONS], n_emp, p=LOC_WEIGHTS),
        "grade_id": grade,
        "employment_type": rng.choice(["Full-Time", "Contract", "Intern"], n_emp, p=[0.86, 0.10, 0.04]),
        "work_mode": rng.choice(["Hybrid", "On-site", "Remote"], n_emp, p=[0.6, 0.25, 0.15]),
    })
    # Link hired candidates to employees (recruitment -> hire traceability)
    hired_idx = cand.index[cand.current_stage == "Hired"].tolist()
    link_n = min(len(hired_idx), n_emp)
    emp["candidate_id"] = None
    emp.loc[: link_n - 1, "candidate_id"] = cand.loc[hired_idx[:link_n], "candidate_id"].values
    emp["manager_id"] = None
    managers = emp.loc[emp.grade_id.isin(["G5", "G6", "G7"]), "employee_id"].tolist()
    emp.loc[~emp.grade_id.isin(["G6", "G7"]), "manager_id"] = rng.choice(managers, (~emp.grade_id.isin(["G6", "G7"])).sum())

    # Exits (attrition ~15% annualised, rising with low performance / tenure 1-3 yrs)
    # Each employee gets a "would-leave-after" tenure drawn from an exponential curve
    # (~14% annual attrition); exits that would fall after the data cut-off stay Active.
    exit_dates = []
    for hd in emp.hire_date:
        stay_days = int(90 + rng.exponential(365 * 6.5))
        ed = hd + timedelta(days=stay_days)
        exit_dates.append(ed if ed < END else None)
    emp["termination_date"] = exit_dates
    emp["employment_status"] = np.where(emp.termination_date.isna(), "Active", "Exited")
    emp["email"] = (emp.first_name.str.lower() + "." + emp.last_name.str.lower() + "."
                    + emp.employee_id.str[-4:] + "@h2r-demo.example")

    # Inject realistic data quality issues for the Silver layer to handle
    dq = emp.sample(frac=0.02, random_state=SEED).index
    emp.loc[dq[: len(dq) // 2], "gender"] = rng.choice(["M", "F", "female", " Male "], len(dq) // 2)
    emp.loc[dq[len(dq) // 2:], "department_id"] = emp.loc[dq[len(dq) // 2:], "department_id"].str.lower()
    emp = pd.concat([emp, emp.sample(12, random_state=1)])  # duplicate records
    emp.to_csv(f"{out}/hris_employees.csv", index=False)
    cand.to_csv(f"{out}/ats_candidates.csv", index=False)

    emp = emp.drop_duplicates("employee_id")

    # ---------- Onboarding ----------
    onb = pd.DataFrame({
        "employee_id": emp.employee_id,
        "onboarding_start": emp.hire_date,
        "laptop_issued_days": rng.integers(0, 6, len(emp)),
        "induction_completed": rng.choice(["Y", "N"], len(emp), p=[0.93, 0.07]),
        "buddy_assigned": rng.choice(["Y", "N"], len(emp), p=[0.85, 0.15]),
        "onboarding_survey_score": np.round(rng.normal(4.1, 0.6, len(emp)).clip(1, 5), 1),
    })
    onb.to_csv(f"{out}/hris_onboarding.csv", index=False)

    # ---------- Learning (LMS) ----------
    rows = []
    for e, hd, td in zip(emp.employee_id, emp.hire_date, emp.termination_date):
        end_d = td if isinstance(td, date) else END
        for c in rng.choice([c[0] for c in COURSES], rng.integers(1, 7), replace=False):
            enr = rand_date(hd, max(end_d, hd + timedelta(days=2)), 1)[0]
            done = rng.random() < 0.78
            rows.append((e, c, enr, enr + timedelta(days=int(rng.integers(3, 45))) if done else None,
                         "Completed" if done else rng.choice(["In Progress", "Not Started"]),
                         int(rng.integers(60, 101)) if done else None))
    pd.DataFrame(rows, columns=["employee_id", "course_id", "enrolled_date", "completed_date",
                                "completion_status", "assessment_score"]) \
        .to_csv(f"{out}/lms_training_records.csv", index=False)

    # ---------- Leave & attendance ----------
    rows = []
    for e, hd, td in zip(emp.employee_id, emp.hire_date, emp.termination_date):
        end_d = td if isinstance(td, date) else END
        for _ in range(rng.poisson(max(1, (end_d - hd).days / 365 * 6))):
            s = rand_date(hd, max(end_d, hd + timedelta(days=2)), 1)[0]
            lt = rng.choice([l[0] for l in LEAVE_TYPES], p=[l[1] for l in LEAVE_TYPES])
            rows.append((e, lt, s, int(rng.integers(1, 6)),
                         rng.choice(["Approved", "Rejected", "Pending"], p=[0.92, 0.05, 0.03])))
    lv = pd.DataFrame(rows, columns=["employee_id", "leave_type", "leave_start_date", "leave_days", "approval_status"])
    lv.insert(0, "leave_id", [f"LV{str(i).zfill(7)}" for i in range(1, len(lv) + 1)])
    lv.to_csv(f"{out}/tna_leave_records.csv", index=False)

    # ---------- Performance (annual cycle, FY ends 31-Mar) ----------
    rows = []
    for fy in range(2022, 2027):
        cycle_end = date(fy, 3, 31)
        eligible = emp[(emp.hire_date <= cycle_end - timedelta(days=90)) &
                       ((emp.termination_date.isna()) | (emp.termination_date.apply(lambda x: isinstance(x, date) and x >= cycle_end)))]
        ratings = rng.choice([1, 2, 3, 4, 5], len(eligible), p=[0.04, 0.12, 0.50, 0.25, 0.09])
        for e, r in zip(eligible.employee_id, ratings):
            rows.append((e, f"FY{str(fy)[2:]}", int(r), round(float(np.clip(rng.normal(r * 18 + 10, 8), 0, 100)), 1),
                         rng.choice(["Y", "N"], p=[0.15 if r >= 4 else 0.03, 0.85 if r >= 4 else 0.97])))
    pd.DataFrame(rows, columns=["employee_id", "review_cycle", "performance_rating", "goal_achievement_pct",
                                "promoted_flag"]).to_csv(f"{out}/perf_reviews.csv", index=False)

    # ---------- Payroll (monthly) ----------
    rows = []
    months = pd.date_range(START, END, freq="MS").date
    base = {e: GRADE_SALARY[g] * rng.uniform(0.85, 1.2) for e, g in zip(emp.employee_id, emp.grade_id)}
    for m in months:
        active = emp[(emp.hire_date <= m) & ((emp.termination_date.isna()) |
                                             (emp.termination_date.apply(lambda x: isinstance(x, date) and x >= m)))]
        yrs = (m.year - START.year)
        for e in active.employee_id:
            monthly = base[e] * (1.08 ** yrs) / 12
            bonus = monthly * rng.uniform(0.5, 1.5) if m.month == 6 and rng.random() < 0.6 else 0
            rows.append((e, m, round(monthly, 2), round(monthly * 0.12, 2), round(bonus, 2),
                         round(monthly * rng.uniform(0, 0.08), 2), round(monthly * 0.18, 2)))
    pd.DataFrame(rows, columns=["employee_id", "pay_month", "base_pay", "benefits", "bonus", "overtime_pay",
                                "deductions"]).to_csv(f"{out}/payroll_monthly.csv", index=False)

    # ---------- Exits (separation) ----------
    ex = emp[emp.employment_status == "Exited"]
    pd.DataFrame({
        "employee_id": ex.employee_id,
        "resignation_date": [t - timedelta(days=int(d)) for t, d in zip(ex.termination_date, rng.integers(30, 90, len(ex)))],
        "last_working_date": ex.termination_date,
        "exit_type": rng.choice(["Voluntary", "Involuntary"], len(ex), p=[0.86, 0.14]),
        "exit_reason": rng.choice(EXIT_REASONS, len(ex), p=EXIT_W),
        "regrettable_flag": rng.choice(["Y", "N"], len(ex), p=[0.35, 0.65]),
        "kt_completed": rng.choice(["Y", "N"], len(ex), p=[0.88, 0.12]),
        "exit_interview_score": np.round(rng.normal(3.4, 0.8, len(ex)).clip(1, 5), 1),
    }).to_csv(f"{out}/hris_exits.csv", index=False)

    for f in sorted(os.listdir(out)):
        if f.endswith(".csv"):
            print(f"{f:<28} {len(pd.read_csv(f'{out}/{f}')):>8,} rows")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--employees", type=int, default=1500)
    p.add_argument("--out", default="../sample-data")
    a = p.parse_args()
    generate(a.employees, a.out)
