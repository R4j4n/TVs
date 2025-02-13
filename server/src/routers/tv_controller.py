import time
from datetime import datetime
from typing import Optional

import schedule
from fastapi import APIRouter
from pydantic import BaseModel


class DaySchedule(BaseModel):
    turn_on_time: Optional[str] = None
    turn_off_time: Optional[str] = None


class WeeklySchedule(BaseModel):
    sunday: Optional[DaySchedule] = DaySchedule(
        turn_on_time="09:30", turn_off_time="20:15"
    )
    monday: Optional[DaySchedule] = DaySchedule(
        turn_on_time="09:30", turn_off_time="20:15"
    )
    tuesday: Optional[DaySchedule] = DaySchedule(
        turn_on_time="09:30", turn_off_time="20:15"
    )
    wednesday: Optional[DaySchedule] = DaySchedule(
        turn_on_time="09:30", turn_off_time="20:15"
    )
    thursday: Optional[DaySchedule] = DaySchedule(
        turn_on_time="09:30", turn_off_time="20:15"
    )
    friday: Optional[DaySchedule] = DaySchedule(
        turn_on_time="09:30", turn_off_time="22:15"
    )
    saturday: Optional[DaySchedule] = DaySchedule(
        turn_on_time="09:30", turn_off_time="22:15"
    )


# Create the router
tv_router = APIRouter(tags=["TV Controls"])

# Store the controller reference
_tv_controller = None


def initialize_router_tv_controller(controller):
    """Initialize the router with a TV controller instance"""
    global _tv_controller
    _tv_controller = controller


@tv_router.post("/set_schedule")
async def set_schedule(schedules: WeeklySchedule):
    schedule_dict = schedules.model_dump()

    for day, times in schedule_dict.items():
        if times:
            _tv_controller.schedule_day(day, DaySchedule(**times))

    _tv_controller.current_schedule = schedules
    _tv_controller.save_schedule()
    return {"message": "Schedules set successfully", "schedule": schedule_dict}


@tv_router.get("/get_schedule")
async def get_schedule():
    return _tv_controller.current_schedule.model_dump()


@tv_router.delete("/clear_schedule")
async def clear_schedule():
    schedule.clear()
    _tv_controller.current_schedule = WeeklySchedule()
    _tv_controller.save_schedule()
    return {"message": "All schedules cleared successfully"}


@tv_router.post("/test_tv")
async def test_tv_controls():
    on_result = _tv_controller.turn_on_tv()
    time.sleep(5)  # Wait 5 seconds
    off_result = _tv_controller.turn_off_tv()
    return {
        "turn_on_result": on_result == 0,
        "turn_off_result": off_result == 0,
    }


@tv_router.get("/status")
async def get_tv_status():
    is_on = _tv_controller.get_tv_status()
    return {
        "status": "on" if is_on else "off",
        "timestamp": datetime.now().isoformat(),
    }
