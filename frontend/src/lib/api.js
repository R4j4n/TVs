// Pis API functions (Port 7777)
export async function fetchPis(host) {
  const response = await fetch(`http://${host}:7777/pis`);
  if (!response.ok) throw new Error("Failed to fetch Pis, received ");
  return response.json();
}

// Individual pi API functions (Port 8000)

export async function fetchPiStatus(host) {
  const response = await fetch(`http://${host}:8000/status`, {method:"GET"});
  if (!response.ok) throw new Error("Failed to fetch status");
  return response.json();
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

export async function playVideo(host, videoName) {
  const response = await fetch(`http://${host}:8000/play`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_name: videoName }),
  });
  if (!response.ok) throw new Error("Failed to play video");
}

export async function pauseVideo(host) {
  const response = await fetch(`http://${host}:8000/pause`, { method: "POST" });
  if (!response.ok) throw new Error("Failed to pause video");
}

export async function resumeVideo(host) {
  const response = await fetch(`http://${host}:8000/resume`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Failed to resume video");
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

// export async function loopVideo(host, loopEnable) {
//   const response = await fetch(`http://${host}:8000/loop`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ enabled: loopEnable }),
//   });
//   if (!response.ok) throw new Error("Failed to enable loop for video");
// }

// TV controls API functions (port 8000/tv/)
export async function isTVOn(host) {
  const response = await fetch(`http://${host}:8000/tv/status`, {
    method: "GET",
  });
  if (!response.ok) throw new Error("Failed to fetch the tv status.");
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
    const response = await fetch(`http://${host}:8000/tv/clear_schedule`, {
      method: "DELETE",
    });
    if (!response.ok) throw new Error("Failed to clear the schedule");
    return response.json();
  } catch {
    console.log("Failed to delete the schedule. . . .");
  }
}

// TV Devices control API functions
export async function check_json(host) {
  const response = await fetch(`http://${host}:8000/tv/check_json`, {
    method: "GET",
  });
  if (!response.ok) throw new Error("Failed to fetch if the json file exists.");
  return response.json();
}

export async function set_hdmi_map(host, formData) {
  const response = await fetch(`http://${host}:8000/tv/set_hdmi_map`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body:JSON.stringify(formData),
  });
  console.log("The response is: ", response.status);
  if (!response.ok)
    throw new Error("Failed to set the hdmi map.");
}

export async function fetch_hdmi_map(host) {
  const response = await fetch(`http://${host}:8000/tv/fetch_hdmi_map`, {
    method: "GET",
  });
  if (!response.ok) throw new Error("Failed to fetch the hdmi map.");
  return response.json();
}

export async function getCurrentActiveDevice(host) {
  try {
    const response = await fetch(`http://${host}:8000/tv/current`, { method: 'GET' });
    if (!response.ok) throw new Error("Failed to fetch the current device");
    return response.json();
  } catch {
    console.log("Failed to fetch the current device. . . .");
  }
}


export async function reset_hdmi_map(host) {
  const response = await fetch(`http://${host}:8000/tv/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) throw new Error("Failed to reset the hdmi map.");
}


export async function switchDevice(host, new_device) {
  const response = await fetch(`http://${host}:8000/tv/switch/${new_device}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(new_device),
  });
  if (!response.ok) throw new Error("Failed to switch to new device");
}







