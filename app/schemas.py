from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmployeeGrowthResponse(BaseModel):
    monthly_registrations: dict
    average_growth: float
    projection: float

class TruckerDistributionResponse(BaseModel):
    by_province: dict
    by_company: dict
    percentages: dict
    most_common: str
    trend: str

class BusinessImpactResponse(BaseModel):
    employee_churn_rate: float
    trucker_churn_rate: float
    document_compliance_rate: float

class ComplianceDataResponse(BaseModel):
    total_employees: int
    active_employees: int
    total_truckers: int
    active_truckers: int
    total_documents: int
    verified_documents: int
    unverified_documents: int

class DocumentUpdate(BaseModel):
    verified: bool
    verified_by: Optional[str] = None
