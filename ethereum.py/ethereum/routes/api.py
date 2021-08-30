"""
api.py

Configures the API Router for the Fast API application
"""
from fastapi import APIRouter
from ethereum.routes import fhir

router = APIRouter()
router.include_router(fhir.router, prefix="/fhir")
