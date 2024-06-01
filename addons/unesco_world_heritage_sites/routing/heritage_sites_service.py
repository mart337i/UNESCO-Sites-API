from fastapi.routing import APIRouter
from fastapi import HTTPException, Depends
from typing import Any
from datetime import timedelta

from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64

from base.logger import logger as _logger
import os

router = APIRouter(
    prefix=f"/sites",
    tags=["Accses and filter sites"],
)

@router.get("/")
def heritage_sites_root():
    return {"OK" : 200}