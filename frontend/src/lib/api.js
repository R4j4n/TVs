export async function fetchPiStatus(host) {
  const response = await fetch(`http://${host}:8000/status`);
  if (!response.ok) throw new Error("Failed to fetch status");
  return response.json();
}

export async function playVideo(host, videoName) {
  const response = await fetch(`http://${host}:8000/play`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_name: videoName }),
  });
  if (!response.ok) throw new Error("Failed to play video");
}

export async function stopVideo(host) {
  const response = await fetch(`http://${host}:8000/stop`, { method: "POST" });
  if (!response.ok) throw new Error("Failed to stop video");
}

export async function deleteVideo(host, videoName) {
  const response = await fetch(`http://${host}:8000/video/${videoName}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete video");
}

export async function uploadVideo(host, file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`http://${host}:8000/upload`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error("Failed to upload video");
}

export async function fetchPis(host) {
  const response = await fetch(`http://${host}:7777/pis`);
  if (!response.ok) throw new Error("Failed to fetch Pis");
  return response.json();
}

export async function getSchedule(host) {
  try {
    const response = await fetch(`http://${host}:8000/tv/get_schedule`);
    if (!response.ok) throw new Error("Failed to fetch the schedule");
    return response.json();
  } catch {
    console.log("Failed to fetch the schedule. . . .");
  }
}

export async function saveSchedule(host, schedule) {
  const response = await fetch(`http://${host}:8000/tv/set_schedule`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(schedule),
  });
  if (!response.ok) throw new Error("Failed to save schedule");
}

export async function deleteSchedule(host) {
  try {
    const response = await fetch(`http://${host}:8000/tv/delete_schedule`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to delete the schedule");
    return response.json();
  } catch {
    console.log("Failed to delete the schedule. . . .");
  }
}
