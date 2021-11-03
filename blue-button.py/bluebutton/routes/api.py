"""
api.py

Configures the API Router for the Fast API application
"""
from fastapi import APIRouter
from bluebutton.routes import bluebutton

router = APIRouter()
router.include_router(bluebutton.router, prefix="/bluebutton")
