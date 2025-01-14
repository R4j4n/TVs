# import os
# import threading
# import time
# from datetime import datetime
# from typing import Dict, Optional

# import schedule
# from fastapi import APIRouter, FastAPI, HTTPException
# from pydantic import BaseModel

# # class DaySchedule(BaseModel):
# #     turn_on_time: Optional[str] = None
# #     turn_off_time: Optional[str] = None


# # class WeeklySchedule(BaseModel):
# #     sunday: Optional[DaySchedule] = None
# #     monday: Optional[DaySchedule] = None
# #     tuesday: Optional[DaySchedule] = None
# #     wednesday: Optional[DaySchedule] = None
# #     thursday: Optional[DaySchedule] = None
# #     friday: Optional[DaySchedule] = None
# #     saturday: Optional[DaySchedule] = None


# class DaySchedule(BaseModel):
#     turn_on_time: Optional[str] = None  # Optional turn-on time
#     turn_off_time: Optional[str] = None  # Optional turn-off time


# class WeeklySchedule(BaseModel):
#     sunday: Optional[DaySchedule] = DaySchedule(
#         turn_on_time="09:30", turn_off_time="20:15"
#     )
#     monday: Optional[DaySchedule] = DaySchedule(
#         turn_on_time="09:30", turn_off_time="20:15"
#     )
#     tuesday: Optional[DaySchedule] = DaySchedule(
#         turn_on_time="09:30", turn_off_time="20:15"
#     )
#     wednesday: Optional[DaySchedule] = DaySchedule(
#         turn_on_time="09:30", turn_off_time="20:15"
#     )
#     thursday: Optional[DaySchedule] = DaySchedule(
#         turn_on_time="09:30", turn_off_time="20:15"
#     )
#     friday: Optional[DaySchedule] = DaySchedule(
#         turn_on_time="09:30", turn_off_time="22:15"
#     )
#     saturday: Optional[DaySchedule] = DaySchedule(
#         turn_on_time="09:30", turn_off_time="22:15"
#     )


# class TVController:
#     def __init__(self):
#         self.router = APIRouter()
#         self.current_schedule = WeeklySchedule()
#         self.setup_routes()
#         self.start_scheduler()

#     def turn_on_tv(self):
#         print(f"Turning on TV at {datetime.now()}")  # Debug log
#         result = os.system('echo "on 0" | cec-client -s -d 1')
#         print(f"TV turn on command result: {result}")  # Debug log
#         return result

#     def turn_off_tv(self):
#         print(f"Turning off TV at {datetime.now()}")  # Debug log
#         result = os.system('echo "standby 0" | cec-client -s -d 1')
#         print(f"TV turn off command result: {result}")  # Debug log
#         return result

#     def run_scheduler(self):
#         while True:
#             schedule.run_pending()
#             time.sleep(30)  # Check every 30 seconds instead of 1 second

#     def start_scheduler(self):
#         scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
#         scheduler_thread.start()

#     def should_run_today(self, day_tag: str) -> bool:
#         current_day = datetime.now().strftime("%A").lower()
#         return current_day == day_tag

#     def schedule_day(self, day: str, times: DaySchedule):
#         if times and (times.turn_on_time or times.turn_off_time):
#             # Clear existing schedules for this day
#             schedule.clear(day)

#             if times.turn_on_time:
#                 schedule.every().day.at(times.turn_on_time).do(
#                     lambda: self.turn_on_tv() if self.should_run_today(day) else None
#                 ).tag(day)

#             if times.turn_off_time:
#                 schedule.every().day.at(times.turn_off_time).do(
#                     lambda: self.turn_off_tv() if self.should_run_today(day) else None
#                 ).tag(day)

#     def setup_routes(self):
#         @self.router.post("/set_schedule")
#         async def set_schedule(schedules: WeeklySchedule):
#             schedule_dict = schedules.model_dump()

#             for day, times in schedule_dict.items():
#                 if times:
#                     self.schedule_day(day, DaySchedule(**times))

#             self.current_schedule = schedules
#             return {"message": "Schedules set successfully", "schedule": schedule_dict}

#         @self.router.get("/get_schedule")
#         async def get_schedule():
#             return self.current_schedule.model_dump()

#         @self.router.delete("/clear_schedule")
#         async def clear_schedule():
#             schedule.clear()
#             self.current_schedule = WeeklySchedule()
#             return {"message": "All schedules cleared successfully"}

#         @self.router.post("/test_tv")
#         async def test_tv_controls():
#             on_result = self.turn_on_tv()
#             time.sleep(5)  # Wait 5 seconds
#             off_result = self.turn_off_tv()
#             return {
#                 "turn_on_result": on_result == 0,
#                 "turn_off_result": off_result == 0,
#             }


# tv_controller = TVController()


import json
import os
import threading
import time
from datetime import datetime
from typing import Dict, Optional

import schedule
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

# Define the schedule file for persistence
SCHEDULE_FILE = "schedule.json"


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


class TVController:
    def __init__(self):
        self.router = APIRouter()
        self.current_schedule = self.load_schedule() or WeeklySchedule()
        print(self.current_schedule)
        self.setup_routes()
        self.start_scheduler()
        self.apply_schedule()

    def turn_on_tv(self):
        print(f"Turning on TV at {datetime.now()}")  # Debug log
        result = os.system('echo "on 0" | cec-client -s -d 1')
        print(f"TV turn on command result: {result}")  # Debug log
        return result

    def turn_off_tv(self):
        print(f"Turning off TV at {datetime.now()}")  # Debug log
        result = os.system('echo "standby 0" | cec-client -s -d 1')
        print(f"TV turn off command result: {result}")  # Debug log
        return result

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds instead of 1 second

    def start_scheduler(self):
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()

    def should_run_today(self, day_tag: str) -> bool:
        current_day = datetime.now().strftime("%A").lower()
        return current_day == day_tag

    def schedule_day(self, day: str, times: DaySchedule):
        if times and (times.turn_on_time or times.turn_off_time):
            # Clear existing schedules for this day
            schedule.clear(day)

            if times.turn_on_time:
                schedule.every().day.at(times.turn_on_time).do(
                    lambda: self.turn_on_tv() if self.should_run_today(day) else None
                ).tag(day)

            if times.turn_off_time:
                schedule.every().day.at(times.turn_off_time).do(
                    lambda: self.turn_off_tv() if self.should_run_today(day) else None
                ).tag(day)

    def apply_schedule(self):
        schedule_dict = self.current_schedule.model_dump()
        for day, times in schedule_dict.items():
            if times:
                self.schedule_day(day, DaySchedule(**times))

    def save_schedule(self):
        with open(SCHEDULE_FILE, "w") as file:
            json.dump(self.current_schedule.model_dump(), file)

    def load_schedule(self) -> Optional[WeeklySchedule]:
        if os.path.exists(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE, "r") as file:
                    schedule_data = json.load(file)
                return WeeklySchedule(**schedule_data)
            except Exception as e:
                print(f"Error loading schedule: {e}")
        return None

    def setup_routes(self):
        @self.router.post("/set_schedule")
        async def set_schedule(schedules: WeeklySchedule):
            schedule_dict = schedules.model_dump()

            for day, times in schedule_dict.items():
                if times:
                    self.schedule_day(day, DaySchedule(**times))

            self.current_schedule = schedules
            self.save_schedule()
            return {"message": "Schedules set successfully", "schedule": schedule_dict}

        @self.router.get("/get_schedule")
        async def get_schedule():
            return self.current_schedule.model_dump()

        @self.router.delete("/clear_schedule")
        async def clear_schedule():
            schedule.clear()
            self.current_schedule = WeeklySchedule()
            self.save_schedule()
            return {"message": "All schedules cleared successfully"}

        @self.router.post("/test_tv")
        async def test_tv_controls():
            on_result = self.turn_on_tv()
            time.sleep(5)  # Wait 5 seconds
            off_result = self.turn_off_tv()
            return {
                "turn_on_result": on_result == 0,
                "turn_off_result": off_result == 0,
            }


tv_controller = TVController()
