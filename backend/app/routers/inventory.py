from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/api/inventory", tags=["inventory"])

class InventoryLevel(BaseModel):
    id: int
    sku: str
    name: str
    current_quantity: int
    reorder_point: int
    reorder_quantity: int
    needs_reorder: bool

    class Config:
        from_attributes = True

class ReorderAlertResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    current_quantity: int
    reorder_point: int
    status: str
    created_at: str

    class Config:
        from_attributes = True

@router.get("/levels", response_model=List[InventoryLevel])
async def get_inventory_levels(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    result = []
    
    for product in products:
        stock_count = db.query(models.InventoryItem).filter(
            models.InventoryItem.product_id == product.id,
            models.InventoryItem.status == 'in_stock'
        ).count()
        
        result.append({
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "current_quantity": stock_count,
            "reorder_point": product.reorder_point,
            "reorder_quantity": product.reorder_quantity,
            "needs_reorder": stock_count <= product.reorder_point
        })
    
    return result

@router.get("/alerts", response_model=List[ReorderAlertResponse])
async def get_reorder_alerts(db: Session = Depends(get_db)):
    alerts = db.query(models.ReorderAlert).filter(
        models.ReorderAlert.status == "pending"
    ).all()
    
    result = []
    for alert in alerts:
        product = db.query(models.Product).filter(
            models.Product.id == alert.product_id
        ).first()
        
        result.append({
            "id": alert.id,
            "product_id": alert.product_id,
            "product_name": product.name if product else "Unknown",
            "current_quantity": alert.current_quantity,
            "reorder_point": alert.reorder_point,
            "status": alert.status,
            "created_at": alert.created_at.strftime("%Y-%m-%d %H:%M:%S") if alert.created_at else ""
        })
    
    return result

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.ReorderAlert).filter(
        models.ReorderAlert.id == alert_id
    ).first()
    
    if alert:
        alert.status = "ordered"
        db.commit()
        return {"message": "Alert resolved", "status": "ordered"}
    
    return {"message": "Alert not found"}, 404
