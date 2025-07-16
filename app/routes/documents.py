from fastapi import APIRouter, Depends, HTTPException
from app.database import SessionLocal
from app.models import Document
from app.schemas import DocumentUpdate

router = APIRouter(prefix="/documents", tags=["Documents"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put("/{doc_id}", status_code=204)
def update_document(doc_id: int, data: DocumentUpdate, db: Session = Depends(get_db)):
    doc = db.query(Document).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.verified = data.verified
    if data.verified and not doc.verification_date:
        doc.verification_date = datetime.utcnow()
        doc.verified_by = data.verified_by
    elif not data.verified:
        doc.verification_date = None
        doc.verified_by = None

    db.commit()
    return None
