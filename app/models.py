from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    reorder_point = Column(Integer, nullable=False, default=10)
    reorder_quantity = Column(Integer, nullable=False, default=50)
    unit_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    inventory_items = relationship("InventoryItem", back_populates="product")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    rfid_tag = Column(String(50), unique=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    status = Column(String(20), default="in_stock")
    location_zone = Column(String(50), nullable=False)
    last_scanned_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="inventory_items")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    rfid_tag = Column(String(50), ForeignKey("inventory_items.rfid_tag"))
    action = Column(String(20), nullable=False)
    location = Column(String(50))
    scanned_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
class ReorderAlert(Base):
    __tablename__ = "reorder_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    current_quantity = Column(Integer, nullable=False)
    reorder_point = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product")
