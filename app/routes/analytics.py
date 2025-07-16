from fastapi import APIRouter, Depends
from app.database import SessionLocal
from app.crud import get_employee_growth, get_trucker_distribution, get_business_impact, get_compliance_data
from app.schemas import EmployeeGrowthResponse, TruckerDistributionResponse, BusinessImpactResponse, ComplianceDataResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/employees/growth", response_model=EmployeeGrowthResponse)
def read_employee_growth(db: Session = Depends(get_db)):
    return get_employee_growth(db)

@router.get("/truckers/distribution", response_model=TruckerDistributionResponse)
def read_trucker_distribution(db: Session = Depends(get_db)):
    return get_trucker_distribution(db)

@router.get("/business/impact", response_model=BusinessImpactResponse)
def read_business_impact(db: Session = Depends(get_db)):
    return get_business_impact(db)

@router.get("/compliance", response_model=ComplianceDataResponse)
def read_compliance(db: Session = Depends(get_db)):
    return get_compliance_data(db)
