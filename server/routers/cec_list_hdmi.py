import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils.list_hdmi import cache, controller

INPUT_FILE = "current_input.json"


@asynccontextmanager
async def lifespan(router: FastAPI):
    yield


router_cec = APIRouter(lifespan=lifespan)


def load_current_input():
    try:
        with open(INPUT_FILE, "r") as file:
            return json.load(file)["current_input"]
    except (FileNotFoundError, KeyError):
        cached_data = cache.get()
        if cached_data:
            return cached_data.get("default_input", 0)
        return 2


def save_current_input(device_number):
    with open(INPUT_FILE, "w") as file:
        json.dump({"current_input": device_number}, file)


@router_cec.get("/devices")
async def get_devices():
    try:
        cached_data = cache.get()
        if not cached_data:
            cached_data = controller.scan_devices()
            cache.set(cached_data)
        return cached_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_cec.post("/rescan")
async def rescan_devices():
    try:
        devices = controller.scan_devices()
        cache.set(devices)
        return devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_cec.post("/switch/{device_number}")
async def switch_input(device_number: int):
    try:
        success = controller.switch_input(device_number)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to switch input")
        current_input = device_number
        save_current_input(device_number)
        return {"message": f"Successfully switched to input {device_number}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_cec.get("/current")
async def get_current_input():
    current_input = load_current_input()
    return {"current_input": current_input}


@router_cec.get("/devices_dummy")
async def return_dummy():
    return {
        "devices": [
            {
                "number": 0,
                "name": "TV",
                "address": "0.0.0.0",
                "vendor": "Philips",
                "osd_string": "TV",
                "active": True,
            },
            {
                "number": 2,
                "name": "Recorder 1",
                "address": "2.0.0.0",
                "vendor": "Philips",
                "osd_string": "RaspberryPi",
                "active": False,
            },
            {
                "number": 3,
                "name": "Tuner 1",
                "address": "3.0.0.0",
                "vendor": "Unknown",
                "osd_string": "Rogers",
                "active": False,
            },
        ],
        "default_input": 2,
    }
