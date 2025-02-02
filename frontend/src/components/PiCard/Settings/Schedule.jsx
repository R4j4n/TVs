// components/PiCard/Settings/Schedule.jsx


"use client";

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
  const [schedule, setSchedule] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [showToast, setShowToast] = useState(null);

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
      setShowToast("Schedule saved successfully!");
      setTimeout(() => setShowToast(null), 3000);
    } catch (err) {
      console.error("Failed to save schedule:", err);
    }
  };

  const handleClear = async () => {
    try {
      await deleteSchedule(host);
      setSchedule({}); // Clear schedule locally
      setShowToast("Schedule cleared successfully!");
      setTimeout(() => setShowToast(null), 3000);
      setShowModal(false);
    } catch (err) {
      console.error("Failed to clear schedule:", err);
    }
  };

  return (
    <div className="space-y-2">
      <div className="pt-4 space-y-4 text-center">
        <h1 className="text-lg text-left pt-6 font-semibold">TV on/off Schedule</h1>
        {loading ? (
          <p>Loading schedule...</p>
        ) : error ? (
          <p>{error}</p>
        ) : (
          daysOfWeek.map((day) => (
            <div
              key={day}
              className="flex items-center justify-start w-full gap-4 py-1"
            >
              <p className="font-lg font-bold capitalize w-1/5 ">
                {day.slice(0, 3)}:{" "}
              </p>
              <div className="flex w-full items-center justify-center text-center gap-1 ">
                <div className="">
                  <input
                    type="time"
                    value={schedule[day]?.turn_on_time || ""}
                    onChange={(e) =>
                      handleChange(day, "turn_on_time", e.target.value)
                    }
                    className="border text-sm rounded-md"
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
                    className="border text-sm rounded-md"
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
            onClick={() => setShowModal(true)}
            className="px-4 py-2 w-fit bg-gradient-to-b from-red-400 to-red-800 text-white rounded-md drop-shadow-lg hover:-translate-y-0.5 transition-all ease-in duration-400"
          >
            Clear Schedule
          </button>
        </div>
      </div>

      {/* Toast Notification */}
      {showToast && (
        <div className="fixed bottom-4 right-4 bg-emerald-600 text-white px-4 py-2 rounded-lg shadow-lg">
          {showToast}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-rose-800 bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h2 className="text-lg font-semibold">Confirm Clear Schedule</h2>
            <p className="text-sm text-gray-600 my-4">
              Are you sure you want to clear the schedule?
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 bg-gray-300 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={handleClear}
                className="px-4 py-2 bg-red-500 text-white rounded-lg"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Schedule;
