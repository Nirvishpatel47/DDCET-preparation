from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict
from database.db import get_all_settings, update_setting

router = APIRouter(prefix="/api/settings", tags=["Settings"])


class SettingsUpdatePayload(BaseModel):
    settings: Dict[str, str]


@router.get("")
def read_settings():
    """Fetches all configuration parameters."""
    return {"settings": get_all_settings()}


@router.post("")
def save_settings(payload: SettingsUpdatePayload):
    """Updates configuration parameters."""
    for k, v in payload.settings.items():
        update_setting(k, str(v))
    return {"status": "updated", "settings": get_all_settings()}
