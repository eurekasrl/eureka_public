from sqlalchemy.orm import Session
from fastapi import HTTPException

def try_commit(db: Session, obj_db):
    try:
        db.add(obj_db)
        db.commit()
        db.refresh(obj_db)
        return obj_db
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Operation failed: {e}")