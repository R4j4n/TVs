import os
import threading
import time
from datetime import datetime
from typing import Dict, Optional

import schedule
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

app = APIRouter()


# Pydantic model for schedules
class DaySchedule(BaseModel):
    turn_on_time: Optional[str] = None  # Optional turn-on time
    turn_off_time: Optional[str] = None  # Optional turn-off time


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


# Function to send CEC commands
def turn_on_tv():
    os.system('echo "on 0" | cec-client -s -d 1')


def turn_off_tv():

    os.system('echo "standby 0" | cec-client -s -d 1')


# Background scheduler thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Start the scheduler in a separate thread
threading.Thread(target=run_scheduler, daemon=True).start()


# Helper function to clear existing schedules
def clear_schedules():
    schedule.clear()


# Global storage for the current schedule
current_schedule = WeeklySchedule()


@app.post("/set_schedule")
def set_schedule(schedules: WeeklySchedule):
    global current_schedule

    # Validate input and clear current schedules
    schedule_data = schedules.dict()
    valid_days = {
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    }
    clear_schedules()

    for day, times in schedule_data.items():
        if day in valid_days and times:
            turn_on_time = times.get("turn_on_time")
            turn_off_time = times.get("turn_off_time")

            if turn_on_time:
                schedule.every().day.at(turn_on_time).do(turn_on_tv).tag(day)

            if turn_off_time:
                schedule.every().day.at(turn_off_time).do(turn_off_tv).tag(day)

    current_schedule = schedules
    return {"message": "Schedules set successfully"}


@app.get("/get_schedule")
def get_schedule():
    # Return the current schedule in JSON format
    return current_schedule.dict()


@app.delete("/clear_schedule")
def clear_schedule():
    global current_schedule

    clear_schedules()
    current_schedule = WeeklySchedule()  # Reset to default
    return {"message": "All schedules cleared successfully"}
