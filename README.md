Understood.

You want a **complete redo of the FastAPI IoT backend** with:

✅ **Much faster runtime**  
✅ **Minimal overhead**  
✅ **No ORM (SQLAlchemy) for speed**  
✅ **Still simple to run**  
✅ **SQLite by default, PostgreSQL-ready**

Here's a **lightning-fast version** using `asyncpg` and `databases` for async database access. This setup is significantly faster than SQLAlchemy-based versions because it uses raw async SQL queries.

---

## 🚀 Fast & Lightweight Version

### ✅ Features:
- JWT auth
- Async database support (SQLite or PostgreSQL)
- Analytics: employee growth, trucker distribution, compliance, churn
- Linear regression projection
- Document verification logic
- Interactive docs at `/docs`

---

## 🔧 Setup Steps

### 1. 📄 `requirements.txt`
```txt
fastapi>=0.95.0,<0.96.0
uvicorn>=0.21.1,<0.22.0
httpx>=0.24.0,<0.25.0
python-jose>=3.3.0,<3.4.0
passlib>=1.7.4,<1.8.0
python-dotenv>=1.0.0,<1.1.0
scikit-learn>=1.2.2,<1.3.0
databases>=0.5.0,<0.6.0
asyncpg>=0.27.0,<0.28.0
```

---

### 2. 📄 `.env`
```bash
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=5f821c6a7a4d3b9e0c5f2a1d3e7b4c8f2e1a0d5c7b6f8a9e0d2c1b7a8f3e9d0c
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

### 3. 📄 `app/main.py`
```python
from fastapi import FastAPI
from app.routes import auth, analytics, documents

app = FastAPI()

app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(documents.router)

@app.get("/")
def read_root():
    return {"message": "Fast IoT Analytics Backend Running!"}
```

---

### 4. 📄 `app/database.py`
```python
from databases import Database
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database = Database(DATABASE_URL)
```

---

### 5. 📄 `app/models.py` – *Skipped*, handled via raw SQL in CRUD*

---

### 6. 📄 `app/schemas.py` *(Same as before)*
```python
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmployeeGrowthResponse(BaseModel):
    monthly_registrations: Dict[str, int]
    average_growth: float
    projection: float

class TruckerDistributionResponse(BaseModel):
    by_province: Dict[str, int]
    by_company: Dict[str, int]
    percentages: Dict[str, float]
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
```

---

### 7. 📄 `app/crud.py`
```python
import json
import numpy as np
from sklearn.linear_model import LinearRegression
from app.database import database

# --- Helper to run raw SQL ---
async def fetch_all(query: str):
    result = await database.fetch_all(query=query)
    return [dict(row) for row in result]

# --- EMPLOYEE GROWTH ---
async def get_employee_growth():
    query = """
        SELECT strftime('%Y-%m', registration_date) AS month, COUNT(*) AS count
        FROM employees WHERE NOT is_archived
        GROUP BY month ORDER BY month;
    """
    results = await fetch_all(query)
    monthly = {r["month"]: r["count"] for r in results}
    avg_growth = sum(monthly.values()) / len(monthly) if monthly else 0

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
async def get_trucker_distribution():
    by_province = await fetch_all("SELECT province_of_issue, COUNT(*) FROM truckers GROUP BY province_of_issue;")
    by_company = await fetch_all("""
        SELECT COALESCE(company_name, 'Independent') AS company, COUNT(*)
        FROM truckers GROUP BY company;
    """)

    total = (await fetch_all("SELECT COUNT(*) FROM truckers"))[0]["COUNT(*)"]
    percentages = {item["company"]: round((item["COUNT(*)"] / total) * 100, 2) for item in by_company}
    most_common = max(by_company, key=lambda x: x["COUNT(*)"])["company"]

    trend = "Balanced"
    if percentages.get("Independent", 0) > 40:
        trend = "Increasing independence"
    elif any(v > 60 for v in percentages.values()):
        trend = "Company dominance"

    return {
        "by_province": dict([(item["province_of_issue"], item["COUNT(*)"]) for item in by_province]),
        "by_company": dict([(item["company"], item["COUNT(*)"]) for item in by_company]),
        "percentages": percentages,
        "most_common": most_common,
        "trend": trend
    }

# --- BUSINESS IMPACT ---
async def get_business_impact():
    total_employees = (await fetch_all("SELECT COUNT(*) FROM employees"))[0]["COUNT(*)"]
    archived_employees = (await fetch_all("SELECT COUNT(*) FROM employees WHERE is_archived = 1"))[0]["COUNT(*)"]
    employee_churn_rate = round((archived_employees / total_employees) * 100, 2) if total_employees else 0

    total_truckers = (await fetch_all("SELECT COUNT(*) FROM truckers"))[0]["COUNT(*)"]
    archived_truckers = (await fetch_all("SELECT COUNT(*) FROM truckers WHERE is_archived = 1"))[0]["COUNT(*)"]
    trucker_churn_rate = round((archived_truckers / total_truckers) * 100, 2) if total_truckers else 0

    total_docs = (await fetch_all("SELECT COUNT(*) FROM documents"))[0]["COUNT(*)"]
    verified_docs = (await fetch_all("SELECT COUNT(*) FROM documents WHERE verified = 1"))[0]["COUNT(*)"]
    compliance_rate = round((verified_docs / total_docs) * 100, 2) if total_docs else 0

    return {
        "employee_churn_rate": employee_churn_rate,
        "trucker_churn_rate": trucker_churn_rate,
        "document_compliance_rate": compliance_rate
    }

# --- COMPLIANCE DATA ---
async def get_compliance_data():
    total_employees = (await fetch_all("SELECT COUNT(*) FROM employees"))[0]["COUNT(*)"]
    active_employees = (await fetch_all("SELECT COUNT(*) FROM employees WHERE is_archived = 0"))[0]["COUNT(*)"]

    total_truckers = (await fetch_all("SELECT COUNT(*) FROM truckers"))[0]["COUNT(*)"]
    active_truckers = (await fetch_all("SELECT COUNT(*) FROM truckers WHERE is_archived = 0"))[0]["COUNT(*)"]

    total_docs = (await fetch_all("SELECT COUNT(*) FROM documents"))[0]["COUNT(*)"]
    verified_docs = (await fetch_all("SELECT COUNT(*) FROM documents WHERE verified = 1"))[0]["COUNT(*)"]
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
```

---

### 8. 📄 `app/routes/auth.py`
*(Same as before but without ORM session handling)*  
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.schemas import Token
from app.database import database

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET_KEY = "5f821c6a7a4d3b9e0c5f2a1d3e7b4c8f2e1a0d5c7b6f8a9e0d2c1b7a8f3e9d0c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(username: str):
    result = await database.fetch_one(f"SELECT * FROM users WHERE username = '{username}'")
    return dict(result) if result else None

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
```

---

### 9. 📄 `app/routes/analytics.py`
```python
from fastapi import APIRouter
from app.crud import get_employee_growth, get_trucker_distribution, get_business_impact, get_compliance_data

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/employees/growth")
async def read_employee_growth():
    return await get_employee_growth()

@router.get("/truckers/distribution")
async def read_trucker_distribution():
    return await get_trucker_distribution()

@router.get("/business/impact")
async def read_business_impact():
    return await get_business_impact()

@router.get("/compliance")
async def read_compliance():
    return await get_compliance_data()
```

---

### 10. 📄 `app/routes/documents.py`
```python
from fastapi import APIRouter
from app.schemas import DocumentUpdate
from app.database import database

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.put("/{doc_id}", status_code=204)
async def update_document(doc_id: int, data: DocumentUpdate):
    doc_query = f"SELECT * FROM documents WHERE id = {doc_id}"
    doc = await database.fetch_one(doc_query)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    now = datetime.now().isoformat()
    if data.verified and not doc["verification_date"]:
        await database.execute(
            f"UPDATE documents SET verified=1, verification_date='{now}', verified_by='{data.verified_by}' WHERE id={doc_id}"
        )
    elif not data.verified:
        await database.execute(
            f"UPDATE documents SET verified=0, verification_date=NULL, verified_by=NULL WHERE id={doc_id}"
        )
    return None
```

---

## 🚀 Run the App

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then go to: http://localhost:8000/docs

---

## ✅ Benefits of This Version
- No ORM overhead — direct SQL
- Async database calls
- Lighter and faster than SQLAlchemy
- Still full feature parity

---

Let me know if you'd like this zipped up or need a SQLite schema init script!
