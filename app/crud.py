from sqlalchemy.orm import Session
from sqlalchemy import func, case
from sklearn.linear_model import LinearRegression
import numpy as np
from app.models import Employee, Trucker, Document

# --- EMPLOYEE GROWTH ---
def get_employee_growth(db: Session):
    results = db.query(
        func.strftime('%Y-%m', Employee.registration_date).label('month'),
        func.count(Employee.id).label('count')
    ).filter(Employee.is_archived == False).group_by('month').all()

    monthly = {r.month: r.count for r in results}
    avg_growth = sum(monthly.values()) / len(monthly) if monthly else 0

    # Projection with Linear Regression
    X = np.array(range(len(monthly))).reshape(-1, 1)
    y = np.array([v for v in monthly.values()])
    model = LinearRegression()
    model.fit(X, y)
    next_month = model.predict([[len(monthly)]])
    projection = round(next_month[0])

    return {
        "monthly_registrations": monthly,
        "average_growth": avg_growth,
        "projection": projection
    }

# --- TRUCKER DISTRIBUTION ---
def get_trucker_distribution(db: Session):
    by_province = db.query(Trucker.province_of_issue, func.count(Trucker.id)).group_by(Trucker.province_of_issue).all()
    by_company = db.query(func.coalesce(Trucker.company_name, 'Independent'), func.count(Trucker.id)) \
                   .group_by(func.coalesce(Trucker.company_name, 'Independent')).all()

    total = db.query(Trucker).count()
    percentages = {k: round((v / total) * 100, 2) for k, v in by_company}
    most_common = max(by_company, key=lambda x: x[1])[0]

    trend = "Balanced"
    if percentages.get("Independent", 0) > 40:
        trend = "Increasing independence"
    elif any(v > 60 for v in percentages.values()):
        trend = "Company dominance"

    return {
        "by_province": dict(by_province),
        "by_company": dict(by_company),
        "percentages": percentages,
        "most_common": most_common,
        "trend": trend
    }

# --- BUSINESS IMPACT ---
def get_business_impact(db: Session):
    total_employees = db.query(Employee).count()
    archived_employees = db.query(Employee).filter(Employee.is_archived == True).count()
    employee_churn_rate = round((archived_employees / total_employees) * 100, 2) if total_employees else 0

    total_truckers = db.query(Trucker).count()
    archived_truckers = db.query(Trucker).filter(Trucker.is_archived == True).count()
    trucker_churn_rate = round((archived_truckers / total_truckers) * 100, 2) if total_truckers else 0

    total_docs = db.query(Document).count()
    verified_docs = db.query(Document).filter(Document.verified == True).count()
    compliance_rate = round((verified_docs / total_docs) * 100, 2) if total_docs else 0

    return {
        "employee_churn_rate": employee_churn_rate,
        "trucker_churn_rate": trucker_churn_rate,
        "document_compliance_rate": compliance_rate
    }

# --- COMPLIANCE DATA ---
def get_compliance_data(db: Session):
    total_employees = db.query(Employee).count()
    active_employees = db.query(Employee).filter(Employee.is_archived == False).count()

    total_truckers = db.query(Trucker).count()
    active_truckers = db.query(Trucker).filter(Trucker.is_archived == False).count()

    total_docs = db.query(Document).count()
    verified_docs = db.query(Document).filter(Document.verified == True).count()
    unverified = total_docs - verified_docs

    return {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_truckers": total_truckers,
        "active_truckers": active_truckers,
        "total_documents": total_docs,
        "verified_documents": verified_docs,
        "unverified_documents": unverified
    }
