"""Renders dashboard design previews (PNG) from the synthetic sample data using the same KPI logic
as the Power BI semantic model. Replace with real Power BI screenshots once the report is built."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
D = "../sample-data/"; O = "../powerbi/screenshots/"
BLUE, TEAL, PURP, ORG, RED, GREY = "#0F6CBD", "#0E9F8E", "#6B4FBB", "#E8833A", "#D13438", "#605E5C"
emp = pd.read_csv(D+"hris_employees.csv", parse_dates=["hire_date","termination_date","date_of_birth"]).drop_duplicates("employee_id")
emp["department_id"] = emp.department_id.str.upper()
dept = pd.read_csv(D+"hris_departments.csv"); loc = pd.read_csv(D+"hris_locations.csv"); grd = pd.read_csv(D+"hris_grades.csv")
emp = emp.merge(dept, on="department_id").merge(loc, on="location_id").merge(grd, on="grade_id")
emp["gender"] = emp.gender.str.strip().str.lower().map({"m":"Male","male":"Male","f":"Female","female":"Female","non-binary":"Non-binary"})
cand = pd.read_csv(D+"ats_candidates.csv", parse_dates=["applied_date"])
ex = pd.read_csv(D+"hris_exits.csv", parse_dates=["last_working_date"]).merge(emp[["employee_id","department_name","hire_date"]], on="employee_id")
tr = pd.read_csv(D+"lms_training_records.csv"); onb = pd.read_csv(D+"hris_onboarding.csv")
perf = pd.read_csv(D+"perf_reviews.csv"); pay = pd.read_csv(D+"payroll_monthly.csv", parse_dates=["pay_month"])
months = pd.date_range("2021-04-30","2026-03-31",freq="ME")
mv = []
for m in months:
    ms = m.replace(day=1)
    alive = emp[(emp.hire_date<=m)&(emp.termination_date.isna()|(emp.termination_date>=ms))]
    mv.append((m, len(alive), ((emp.hire_date>=ms)&(emp.hire_date<=m)).sum(), ((emp.termination_date>=ms)&(emp.termination_date<=m)).sum()))
mv = pd.DataFrame(mv, columns=["m","hc","hires","exits"])
act = emp[emp.termination_date.isna()]
last12 = mv.tail(12); attr = last12.exits.sum()/last12.hc.mean()

def frame(title, sub):
    fig = plt.figure(figsize=(16,9), facecolor="#F5F7FA")
    fig.patches.append(plt.Rectangle((0,.92),1,.08,transform=fig.transFigure,color="#1B2A49",zorder=0))
    fig.text(.02,.955,title,color="white",fontsize=20,weight="bold",va="center")
    fig.text(.98,.955,sub,color="#C8D3E6",fontsize=10,va="center",ha="right")
    fig.text(.02,.012,"Design preview rendered from synthetic data · Hire-to-Retire Analytics on Microsoft Fabric",fontsize=8,color=GREY)
    return fig
def cards(fig, items, y=.80):
    w = .96/len(items)
    for i,(lab,val,col) in enumerate(items):
        ax = fig.add_axes([.02+i*w,y,w-.01,.10]); ax.set_xticks([]); ax.set_yticks([])
        ax.set_facecolor("white"); [s.set_color("#E1E5EB") for s in ax.spines.values()]
        ax.axvline(0,color=col,lw=8)
        ax.text(.08,.65,val,fontsize=22,weight="bold",color="#1B2A49",transform=ax.transAxes,va="center")
        ax.text(.08,.22,lab,fontsize=10,color=GREY,transform=ax.transAxes,va="center")
def panel(fig, rect, title):
    ax = fig.add_axes(rect); ax.set_facecolor("white"); ax.set_title(title,loc="left",fontsize=12,weight="bold",color="#1B2A49")
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=8); return ax

# ---- Page 1 Executive overview
fig = frame("Hire-to-Retire | Executive Workforce Overview","FY22 – FY26  ·  All regions")
cards(fig,[("Active Headcount",f"{len(act):,}",BLUE),("Hires (L12M)",f"{last12.hires.sum():,}",TEAL),
           ("Exits (L12M)",f"{last12.exits.sum():,}",RED),("Attrition % (L12M)",f"{attr:.1%}",ORG),
           ("Female %",f"{(act.gender=='Female').mean():.1%}",PURP),("Avg Tenure (Yrs)",f"{((pd.Timestamp('2026-03-31')-act.hire_date).dt.days/365).mean():.1f}",GREY)])
ax = panel(fig,[.04,.43,.50,.31],"Headcount trend (line) with monthly hires & exits (bars)")
ax.plot(mv.m,mv.hc,color=BLUE,lw=2.5); ax2=ax.twinx(); ax2.bar(mv.m,mv.hires,width=12,color=TEAL,alpha=.6,label="Hires")
ax2.bar(mv.m+pd.Timedelta(days=12),mv.exits,width=12,color=RED,alpha=.6,label="Exits"); ax2.legend(fontsize=8,loc="upper left"); ax2.tick_params(labelsize=8); ax2.set_ylim(0,max(mv.hires.max(),mv.exits.max())*3)
ax = panel(fig,[.68,.43,.29,.31],"Headcount by department"); s=act.department_name.value_counts().sort_values()
ax.barh(s.index,s.values,color=BLUE); [ax.text(v+3,i,v,va="center",fontsize=8) for i,v in enumerate(s.values)]
ax = panel(fig,[.04,.06,.28,.30],"Headcount by region"); s=act.region.value_counts()
ax.pie(s.values,labels=s.index,colors=[BLUE,TEAL,PURP],autopct="%1.0f%%",wedgeprops=dict(width=.4),textprops={"fontsize":9})
ax = panel(fig,[.37,.08,.27,.27],"Grade pyramid"); s=act.groupby(["grade_level","grade_name"]).size().reset_index().sort_values("grade_level",ascending=False)
ax.barh(s.grade_name,s[0],color=PURP)
ax = panel(fig,[.70,.08,.27,.27],"Gender mix by business unit"); g=pd.crosstab(act.business_unit,act.gender,normalize="index")
g.plot.barh(stacked=True,ax=ax,color=[PURP,BLUE,TEAL],legend=False); ax.legend(fontsize=7,loc="lower right"); ax.set_ylabel("")
fig.savefig(O+"01_executive_overview.png",dpi=110); plt.close()

# ---- Page 2 Talent acquisition & onboarding
fig = frame("Hire-to-Retire | Talent Acquisition & Onboarding","Recruitment funnel · Source effectiveness · First-year experience")
stg = {"Applied":1,"Screened":2,"Interviewed":3,"Offered":4,"Hired":5}; cand["o"]=cand.current_stage.map(stg)
fun = [(k,(cand.o>=v).sum()) for k,v in stg.items()]; off=(cand.o>=4).sum(); hired=(cand.o==5).sum()
early = (ex.last_working_date-ex.hire_date).dt.days.lt(365).sum()/len(ex)
cards(fig,[("Applicants",f"{len(cand):,}",BLUE),("Candidates Hired",f"{hired:,}",TEAL),("Offer Acceptance %",f"{hired/off:.1%}",PURP),
           ("Applicant → Hire %",f"{hired/len(cand):.1%}",ORG),("Induction Completion %",f"{(onb.induction_completed=='Y').mean():.1%}",TEAL),
           ("Onboarding Score",f"{onb.onboarding_survey_score.mean():.2f} / 5",GREY)])
ax = panel(fig,[.04,.43,.40,.31],"Recruitment funnel"); n=[f[1] for f in fun]
ax.barh([f[0] for f in fun][::-1],n[::-1],color=[TEAL,PURP,BLUE,BLUE,BLUE]); [ax.text(v+50,i,f"{v:,}",va="center",fontsize=9) for i,v in enumerate(n[::-1])]
ax = panel(fig,[.52,.43,.45,.31],"Hires & conversion by source channel"); s=cand.groupby("source_channel").agg(app=("o","size"),h=("o",lambda x:(x==5).sum()))
s["conv"]=s.h/s.app; s=s.sort_values("h"); ax.bar(s.index,s.h,color=BLUE); ax2=ax.twinx(); ax2.plot(s.index,s.conv*100,color=ORG,marker="o"); ax2.set_ylabel("Conversion %",fontsize=8); ax.tick_params(axis="x",rotation=15)
ax = panel(fig,[.04,.08,.43,.27],"Hires per quarter"); q=emp.groupby(emp.hire_date.dt.to_period("Q")).size(); ax.bar(q.index.astype(str),q.values,color=TEAL); ax.tick_params(axis="x",rotation=60,labelsize=7)
ax = panel(fig,[.55,.08,.42,.27],"Onboarding survey score distribution"); ax.hist(onb.onboarding_survey_score,bins=20,color=PURP)
fig.savefig(O+"02_talent_acquisition_onboarding.png",dpi=110); plt.close()

# ---- Page 3 Develop & perform
fig = frame("Hire-to-Retire | Learning & Performance","Capability building · Performance distribution · Promotions")
cards(fig,[("Training Completion %",f"{(tr.completion_status=='Completed').mean():.1%}",TEAL),("Avg Assessment Score",f"{tr.assessment_score.mean():.0f}",BLUE),
           ("Avg Performance Rating",f"{perf.performance_rating.mean():.2f}",PURP),("High Performer %",f"{(perf.performance_rating>=4).mean():.1%}",ORG),
           ("Promotion Rate %",f"{(perf.promoted_flag=='Y').mean():.1%}",GREY)])
crs = pd.read_csv(D+"lms_courses.csv"); t=tr.merge(crs,on="course_id")
ax = panel(fig,[.04,.43,.45,.31],"Completion % by course"); s=t.groupby("course_name").completion_status.apply(lambda x:(x=="Completed").mean()*100).sort_values()
ax.barh(s.index,s.values,color=TEAL); ax.set_xlim(0,100)
ax = panel(fig,[.56,.43,.41,.31],"Rating distribution by review cycle"); p=pd.crosstab(perf.review_cycle,perf.performance_rating,normalize="index")*100
p.plot.bar(stacked=True,ax=ax,color=[RED,ORG,"#A0AEC0",BLUE,TEAL],legend=True,rot=0); ax.legend(title="Rating",fontsize=7,title_fontsize=7,ncol=5,loc="upper center")
ax = panel(fig,[.04,.08,.45,.27],"Learning hours by category"); s=t[t.completion_status=="Completed"].groupby("course_category").duration_hours.sum().sort_values()
ax.barh(s.index,s.values,color=PURP)
ax = panel(fig,[.56,.08,.41,.27],"Promotion rate by rating"); s=perf.groupby("performance_rating").promoted_flag.apply(lambda x:(x=="Y").mean()*100)
ax.bar(s.index.astype(str),s.values,color=BLUE); ax.set_xlabel("Performance rating",fontsize=8)
fig.savefig(O+"03_learning_performance.png",dpi=110); plt.close()

# ---- Page 4 Retain & retire
fig = frame("Hire-to-Retire | Attrition, Retention & Exit","Why people leave · When they leave · Cost of workforce")
cards(fig,[("Total Exits",f"{len(ex):,}",RED),("Attrition % (L12M)",f"{attr:.1%}",ORG),("Voluntary %",f"{(ex.exit_type=='Voluntary').mean():.1%}",PURP),
           ("Regrettable Exits",f"{(ex.regrettable_flag=='Y').sum():,}",RED),("Early Attrition %",f"{early:.1%}",ORG),("KT Completed %",f"{(ex.kt_completed=='Y').mean():.1%}",TEAL)])
ax = panel(fig,[.04,.43,.45,.31],"Rolling 12-month attrition %"); r=mv.exits.rolling(12).sum()/mv.hc.rolling(12).mean()*100
ax.plot(mv.m,r,color=RED,lw=2.5); ax.fill_between(mv.m,r,color=RED,alpha=.08)
ax = panel(fig,[.56,.43,.41,.31],"Exit reasons"); s=ex.exit_reason.value_counts().sort_values(); ax.barh(s.index,s.values,color=ORG)
ax = panel(fig,[.04,.11,.45,.24],"Attrition % by department (all time)"); h=emp.department_name.value_counts(); s=(ex.department_name.value_counts()/h*100).sort_values(ascending=False)
ax.bar(s.index,s.values,color=PURP); ax.tick_params(axis="x",rotation=20,labelsize=7); [l.set_ha("right") for l in ax.get_xticklabels()]
ax = panel(fig,[.56,.08,.41,.27],"Monthly payroll cost (₹ Cr)"); s=pay.assign(g=pay.base_pay+pay.benefits+pay.bonus+pay.overtime_pay).groupby("pay_month").g.sum()/1e7
ax.plot(s.index,s.values,color=BLUE,lw=2)
fig.savefig(O+"04_attrition_retention_exit.png",dpi=110); plt.close()
print("attrition L12M", round(attr,3), "active", len(act))
