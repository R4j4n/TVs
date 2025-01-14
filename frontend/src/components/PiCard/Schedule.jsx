"use client";

import { ChevronDown, ChevronUp } from "lucide-react";
import { useState, useEffect } from "react";
import { getSchedule, saveSchedule } from "@/lib/api";

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
      alert("Failed to save schedule");
    }
  };

  return (
    <div className="space-y-2">
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded((prev) => !prev)}
      >
        <p className="font-medium">Schedule</p>
        {isExpanded ? (
          <ChevronUp className="h-4 w-4" />
        ) : (
          <ChevronDown className="h-4 w-4" />
        )}
      </div>

      {isExpanded && (
        <div className="pt-4 space-y-4">
          {loading ? (
            <p>Loading schedule...</p>
          ) : error ? (
            <p>{error}</p>
          ) : (
            daysOfWeek.map((day) => (
              <div key={day} className="space-y-2">
                <p className="font-medium capitalize">{day}</p>
                <div className="flex items-center gap-4">
                  <div>
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
                  <p>--</p>
                  </div>
                  <div>
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
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Save Schedule
          </button>
        </div>
      )}
    </div>
  );
};

export default Schedule;
