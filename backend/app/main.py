from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import scans, inventory

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart WMS API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scans.router)
app.include_router(inventory.router)

@app.get("/")
async def root():
    return {"message": "Smart Warehouse Management System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
