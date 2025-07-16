from fastapi import FastAPI
from app.routes import auth, analytics, documents
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(documents.router)

@app.get("/")
def read_root():
    return {"message": "IoT Analytics Backend Running!"}
