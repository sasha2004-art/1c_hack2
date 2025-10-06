from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from ..db.base import get_db
from .. import crud, schemas, models

router = APIRouter()


@router.get("/public/lists/{list_id}", response_model=schemas.ListRead)
def read_public_list(list_id: int, db: Session = Depends(get_db)):
    """Return a list by id if it is public. No authentication required."""
    db_list = crud.get_list(db, list_id=list_id)
    if db_list is None:
        raise HTTPException(status_code=404, detail="List not found")
    # Only return lists explicitly marked as PUBLIC
    if getattr(db_list, "privacy_level", None) != models.PrivacyLevel.PUBLIC:
        # Hide existence of private lists
        raise HTTPException(status_code=404, detail="List not found")
    return db_list
