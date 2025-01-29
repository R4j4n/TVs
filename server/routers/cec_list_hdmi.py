# import json
# from contextlib import asynccontextmanager

# import uvicorn
# from fastapi import APIRouter, FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from utils.list_hdmi import cache, controller

# INPUT_FILE = "current_input.json"


# @asynccontextmanager
# async def lifespan(router: FastAPI):
#     yield


# router_cec = APIRouter(lifespan=lifespan)


# def load_current_input():
#     try:
#         with open(INPUT_FILE, "r") as file:
#             return json.load(file)["current_input"]
#     except (FileNotFoundError, KeyError):
#         cached_data = cache.get()
#         if cached_data:
#             return cached_data.get("default_input", 0)
#         return 2


# def save_current_input(device_number):
#     with open(INPUT_FILE, "w") as file:
#         json.dump({"current_input": device_number}, file)


# @router_cec.get("/devices")
# async def get_devices():
#     try:
#         cached_data = cache.get()
#         if not cached_data:
#             cached_data = controller.scan_devices()
#             cache.set(cached_data)
#         return cached_data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router_cec.post("/rescan")
# async def rescan_devices():
#     try:
#         devices = controller.scan_devices()
#         cache.set(devices)
#         return devices
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router_cec.post("/switch/{device_number}")
# async def switch_input(device_number: int):
#     try:
#         success = controller.switch_input(device_number)
#         if not success:
#             raise HTTPException(status_code=500, detail="Failed to switch input")
#         current_input = device_number
#         save_current_input(device_number)
#         return {"message": f"Successfully switched to input {device_number}"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router_cec.get("/current")
# async def get_current_input():
#     current_input = load_current_input()
#     return {"current_input": current_input}


# @router_cec.get("/devices_dummy")
# async def return_dummy():
#     return {
#         "devices": [
#             {
#                 "number": 0,
#                 "name": "TV",
#                 "address": "0.0.0.0",
#                 "vendor": "Philips",
#                 "osd_string": "TV",
#                 "active": True,
#             },
#             {
#                 "number": 2,
#                 "name": "Recorder 1",
#                 "address": "2.0.0.0",
#                 "vendor": "Philips",
#                 "osd_string": "RaspberryPi",
#                 "active": False,
#             },
#             {
#                 "number": 3,
#                 "name": "Tuner 1",
#                 "address": "3.0.0.0",
#                 "vendor": "Unknown",
#                 "osd_string": "Rogers",
#                 "active": False,
#             },
#         ],
#         "default_input": 2,
#     }

import json
import logging
import os
import subprocess
from typing import Dict

from fastapi import APIRouter, FastAPI, HTTPException, Response

router_cec = APIRouter()

HDMI_DEVICES_FILE = "hdmi_devices.json"
CURRENT_INPUT_FILE = "current_input.json"


class CECController:
    def __init__(self):
        self.logger = self._setup_logging()

    def _setup_logging(self):
        logger = logging.getLogger("cec_controller")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _execute_cec_command(self, command: str) -> str:
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"CEC command failed: {e}")
            raise

    def switch_input(self, device_number: int) -> bool:
        try:
            device_hex = format(device_number * 16, "02x").upper()
            command = f'echo "tx 1F:82:{device_hex}:00" | cec-client -s -d 1'
            self._execute_cec_command(command)
            self.logger.info(f"Switched to input {device_number}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch input: {e}")
            return False


def load_current_input():
    try:
        with open(CURRENT_INPUT_FILE, "r") as file:
            return json.load(file)["current_input"]
    except (FileNotFoundError, KeyError):
        return 0


def save_current_input(device_number):
    with open(CURRENT_INPUT_FILE, "w") as file:
        json.dump({"current_input": device_number}, file)


cec_controller = CECController()


@router_cec.get("/check_json")
async def check_json() -> bool:
    """
    Check if hdmi_devices.json exists
    Returns:
        bool: True if file exists, False otherwise
    """
    return os.path.exists(HDMI_DEVICES_FILE)


@router_cec.post("/set_hdmi_map")
async def set_hdmi_map(hdmi_map: Dict[str, str]):
    """
    Save HDMI device mapping and update current input
    Args:
        hdmi_map: Dictionary mapping HDMI ports to device names
    Returns:
        dict: Success message
    """
    try:
        # Save the HDMI map
        with open(HDMI_DEVICES_FILE, "w") as f:
            json.dump(hdmi_map, f, indent=2)

        # Find the key for "raspberry pi" and update current_input.json
        raspberry_pi_port = None
        for port, device in hdmi_map.items():
            if device.lower() == "raspberry pi":
                raspberry_pi_port = port
                break

        # Switch TV to that HDMI
        cec_controller.switch_input(device_number=int(raspberry_pi_port))

        # Initialize current_input if it doesn't exist
        current_input = {"current_input": "1"}  # Default value
        if os.path.exists(CURRENT_INPUT_FILE):
            try:
                with open(CURRENT_INPUT_FILE, "r") as f:
                    current_input = json.load(f)
            except json.JSONDecodeError:
                pass

        # Update current_input if raspberry pi is found
        if raspberry_pi_port:
            current_input["current_input"] = raspberry_pi_port

        # Save the updated current_input
        with open(CURRENT_INPUT_FILE, "w") as f:
            json.dump(current_input, f, indent=2)

        return Response(content="HDMI mapped Sucessfully", status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving HDMI map: {str(e)}")


@router_cec.get("/fetch_hdmi_map")
async def fetch_hdmi_map():
    """
    Read and return the HDMI device mapping
    Returns:
        dict: HDMI device mapping
    """
    try:
        if not os.path.exists(HDMI_DEVICES_FILE):
            raise HTTPException(status_code=404, detail="HDMI devices file not found")

        with open(HDMI_DEVICES_FILE, "r") as f:
            hdmi_map = json.load(f)

        return hdmi_map

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in HDMI devices file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading HDMI map: {str(e)}")


@router_cec.get("/current")
async def get_current_input():
    current_input = load_current_input()
    return {"current_input": current_input}


@router_cec.post("/switch/{device_number}")
async def switch_input(device_number: int):
    try:
        success = cec_controller.switch_input(device_number)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to switch input")
        save_current_input(device_number)
        return {"message": f"Successfully switched to input {device_number}"}
        save_current_input(device_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router_cec.post("/reset")
async def reset_files():
    """
    Delete both hdmi_devices.json and current_input.json files
    Returns:
        dict: Status message indicating which files were deleted
    """
    deleted_files = []

    try:
        # Delete hdmi_devices.json if it exists
        if os.path.exists(HDMI_DEVICES_FILE):
            os.remove(HDMI_DEVICES_FILE)
            deleted_files.append(HDMI_DEVICES_FILE)

        # Delete current_input.json if it exists
        if os.path.exists(CURRENT_INPUT_FILE):
            os.remove(CURRENT_INPUT_FILE)
            deleted_files.append(CURRENT_INPUT_FILE)

        if deleted_files:
            return {"message": f"Successfully deleted: {', '.join(deleted_files)}"}
        else:
            return {"message": "No files found to delete"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting files: {str(e)}")
