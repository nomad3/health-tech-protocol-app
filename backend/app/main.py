from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, protocols, admin, patients, therapists, ai

app = FastAPI(
    title="PsyProtocol API",
    description="AI-powered protocol platform for medical treatments including psychedelics, hormone therapy, cancer treatments, regenerative medicine, and emerging therapies",
    version="1.0.0",
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(protocols.router)
app.include_router(admin.router)
app.include_router(patients.router)
app.include_router(therapists.router)
app.include_router(ai.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "PsyProtocol API", "version": "1.0.0"}
