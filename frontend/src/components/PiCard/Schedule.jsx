"use client";

import { ChevronDown, ChevronUp } from "lucide-react";
import { useState, useEffect } from "react";
import { deleteSchedule, getSchedule, saveSchedule } from "@/lib/api";

const daysOfWeek = [
  "sunday",
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
];

const Schedule = ({ host }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [schedule, setSchedule] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchSchedule() {
      try {
        const result = await getSchedule(host);
        setSchedule(result);
        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch schedule:", err);
        setError("Failed to load schedule");
        setLoading(false);
      }
    }
    fetchSchedule();
  }, [host]);

  const handleChange = (day, type, value) => {
    setSchedule((prev) => ({
      ...prev,
      [day]: { ...prev[day], [type]: value },
    }));
  };

  const handleSave = async () => {
    try {
      await saveSchedule(host, schedule);
      console.log(schedule);
      alert("Schedule saved successfully!");
    } catch (err) {
      console.error("Failed to save schedule:", err);
      // alert("Failed to save schedule");
    }
  };

  const handleClear = async () => {
    try {
      await deleteSchedule(host);
      console.log("Schedule removed successfully !!");
      alert("Schedule cleared !!!");
    } catch (err) {
      console.error("Failed to clear schedule:", err);
      // alert("Failed to clear schedule");
    }
  };

  return (
    <div className="space-y-2">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded((prev) => !prev)}
      >
        <p className="font-medium">Schedule TV on and Off Time</p>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </div>

      {isExpanded && (
        <div className="pt-4 space-y-4 text-center">
          {loading ? (
            <p>Loading schedule...</p>
          ) : error ? (
            <p>{error}</p>
          ) : (
            daysOfWeek.map((day) => (
              <div key={day} className=" py-2">
                <p className="font-lg font-bold capitalize text-center">
                  {day}
                </p>
                <div className=" w-full  flex items-center justify-center gap-3">
                  <div className="">
                    <input
                      type="time"
                      value={schedule[day]?.turn_on_time || ""}
                      onChange={(e) =>
                        handleChange(day, "turn_on_time", e.target.value)
                      }
                      className="border rounded-md p-2"
                    />
                  </div>
                  <div>
                    <p>-</p>
                  </div>
                  <div className="">
                    <input
                      type="time"
                      value={schedule[day]?.turn_off_time || ""}
                      onChange={(e) =>
                        handleChange(day, "turn_off_time", e.target.value)
                      }
                      className="border rounded-md p-2"
                    />
                  </div>
                </div>
              </div>
            ))
          )}

          <div className="flex flex-col justify-center items-center w-full gap-4">
            <button
              onClick={handleSave}
              className="px-4 py-2 w-fit bg-gradient-to-b from-emerald-400 to-emerald-800 text-white rounded-md drop-shadow-lg hover:-translate-y-0.5 transition-all ease-in duration-400"
            >
              Save Schedule
            </button>
            <button
              onClick={handleClear}
              className="px-4 py-2 w-fit bg-gradient-to-b from-red-400 to-red-800 text-white rounded-md drop-shadow-lg hover:-translate-y-0.5 transition-all ease-in duration-400"
            >
              Clear Schedule
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Schedule;
