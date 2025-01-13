import os
import threading
import time
from typing import List

import schedule
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Request model
class ScheduleRequest(BaseModel):
    day: str  # e.g., "monday", "tuesday", etc.
    turn_on_time: str  # e.g., "09:30"
    turn_off_time: str  # e.g., "20:15"


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


@app.post("/set_schedule")
def set_schedule(schedules: List[ScheduleRequest]):
    # Validate input and clear current schedules
    valid_days = {
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    }
    clear_schedules()

    for sched in schedules:
        if sched.day.lower() not in valid_days:
            raise HTTPException(status_code=400, detail=f"Invalid day: {sched.day}")

        try:
            # Schedule turn on and off tasks
            schedule.every().day.at(sched.turn_on_time).do(turn_on_tv).tag(
                sched.day.lower()
            )
            schedule.every().day.at(sched.turn_off_time).do(turn_off_tv).tag(
                sched.day.lower()
            )
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error scheduling task: {str(e)}"
            )

    return {"message": "Schedules set successfully"}


@app.get("/get_schedule")
def get_schedule():
    # Retrieve all current schedules
    jobs = schedule.get_jobs()
    if not jobs:
        return {"message": "No schedules currently set"}

    schedule_list = []
    for job in jobs:
        schedule_list.append(
            {"tags": list(job.tags), "next_run": job.next_run, "interval": job.interval}
        )

    return schedule_list


@app.delete("/clear_schedule")
def clear_schedule():
    clear_schedules()
    return {"message": "All schedules cleared successfully"}


# Main API remains live, and scheduler runs in the background
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
