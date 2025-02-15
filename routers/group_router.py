import json
import logging
import time as import_time
from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

group_router = APIRouter()

GROUPS_FILE = Path("groups.json")


class Device(BaseModel):
    name: str
    host: str


class Group(BaseModel):
    name: str
    devices: List[Device]


class GroupUpdate(BaseModel):
    name: str
    devices: List[Device]


def load_groups() -> Dict:
    """Load groups from JSON file"""
    try:
        if GROUPS_FILE.exists():
            with open(GROUPS_FILE, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading groups: {e}")
        return {}


def save_groups(groups: Dict) -> None:
    """Save groups to JSON file"""
    try:
        with open(GROUPS_FILE, "w") as f:
            json.dump(groups, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving groups: {e}")
        raise HTTPException(status_code=500, detail="Failed to save groups")


@group_router.get("")
async def get_groups():
    """Get all groups"""
    try:
        groups = load_groups()
        return groups
    except Exception as e:
        logger.error(f"Error getting groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@group_router.post("")
async def create_group(group: Group):
    """Create a new group"""
    try:
        groups = load_groups()
        group_id = f"group_{len(groups) + 1}"

        groups[group_id] = {
            "name": group.name,
            "devices": [device.dict() for device in group.devices],
            "createdAt": import_time.time(),
        }

        save_groups(groups)
        return {"id": group_id, **groups[group_id]}
    except Exception as e:
        logger.error(f"Error creating group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@group_router.put("/{group_id}")
async def update_group(group_id: str, group_update: GroupUpdate):
    """Update an existing group"""
    try:
        groups = load_groups()
        if group_id not in groups:
            raise HTTPException(status_code=404, detail="Group not found")

        groups[group_id].update(
            {
                "name": group_update.name,
                "devices": [device.dict() for device in group_update.devices],
            }
        )

        save_groups(groups)
        return groups[group_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating group: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@group_router.delete("/{group_id}")
async def delete_group(group_id: str):
    """Delete a group"""
    try:
        groups = load_groups()
        if group_id not in groups:
            raise HTTPException(status_code=404, detail="Group not found")

        del groups[group_id]
        save_groups(groups)
        return {"message": "Group deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        raise HTTPException(status_code=500, detail=str(e))
