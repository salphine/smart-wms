from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from .. import models
from ..database import get_db
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/scans", tags=["scans"])

class ScanEvent(BaseModel):
    rfid_tag: str
    location: str
    scanner_id: Optional[str] = None

class ScanResponse(BaseModel):
    rfid_tag: str
    action: str
    location: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/")
async def process_scan(scan: ScanEvent, db: Session = Depends(get_db)):
    # Find the inventory item
    item = db.query(models.InventoryItem).filter(
        models.InventoryItem.rfid_tag == scan.rfid_tag
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail=f"Unknown RFID tag: {scan.rfid_tag}")
    
    # Update item location and timestamp
    old_location = item.location_zone
    item.location_zone = scan.location
    item.last_scanned_at = datetime.utcnow()
    
    # Log transaction
    transaction = models.Transaction(
        rfid_tag=scan.rfid_tag,
        action="SCANNED",
        location=f"{old_location} -> {scan.location}",
        scanned_by=scan.scanner_id
    )
    db.add(transaction)
    db.commit()
    
    return {
        "message": "Scan processed successfully", 
        "rfid": scan.rfid_tag,
        "new_location": scan.location
    }

@router.get("/recent", response_model=List[ScanResponse])
async def get_recent_scans(limit: int = 50, db: Session = Depends(get_db)):
    scans = db.query(models.Transaction).order_by(
        models.Transaction.created_at.desc()
    ).limit(limit).all()
    return scans
