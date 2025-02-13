import json
import os
import threading
import time
from datetime import datetime
from typing import Optional

import schedule

from src.routers.tv_controller import DaySchedule, WeeklySchedule

SCHEDULE_FILE = "schedule.json"

from src.hdmi_controllers import CECController
from src.routers.inputs_switch import load_current_input
from src.video_manager import video_manager


class TVController:
    def __init__(self):
        self.current_schedule = self.load_schedule() or WeeklySchedule()
        print(self.current_schedule)
        self.start_scheduler()
        self.apply_schedule()

    def turn_on_tv(self):
        switch_handler = CECController()
        current_device = load_current_input()
        print(f"Turning on TV at {datetime.now()}")  # Debug log
        result = os.system('echo "on 0" | cec-client -s -d 1')
        print(f"TV turn on command result: {result}")  # Debug log

        # Whenever TV is turned on, try to switch to the last used input
        if current_device == 0:
            print("No HDMI device mapp set.")
        else:
            try:
                switch_handler.switch_input(device_number=current_device)
            except Exception as e:
                print(f"Cant switch to HDMI {current_device}")

        # Play the last played content
        video_manager.load_last_played()
        return result

    def turn_off_tv(self):

        print(f"Turning off TV at {datetime.now()}")  # Debug log
        result = os.system('echo "standby 0" | cec-client -s -d 1')
        print(f"TV turn off command result: {result}")  # Debug log

        # stop the the item which is being currently played
        video_manager.stop()

        return result

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds

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

    def get_tv_status(self) -> bool:
        """
        Query the TV power status using cec-client.
        Returns True if TV is on, False if TV is off/standby.
        """
        try:
            result = os.popen('echo "pow 0" | cec-client -s -d 1').read()

            if "power status: on" in result.lower():
                return True
            elif "power status: standby" in result.lower():
                return False
            else:
                print(f"Unexpected power status response: {result}")
                return False
        except Exception as e:
            print(f"Error getting TV status: {e}")
            return False
