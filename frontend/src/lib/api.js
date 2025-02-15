// lib/api.js

// Dashboard Login function (Port 8000)
export async function auth_login(host, user_entered_pw) {
  const response = await fetch(`http://${host}:8000/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            password: user_entered_pw,
          }),
        })  
  if (!response.ok) throw new Error("Failed to play video");
  return response;
}

// Pis API functions (Port 7777)
export async function fetchPis(host) {
  const response = await fetch(`http://${host}:7777/pis`);
  if (!response.ok) throw new Error("Failed to fetch Pis, received ");
  return response.json();
}

// Individual pi API functions (Port 8000)
export async function fetchPiStatus(host) {
  try {
    const auth_token = sessionStorage.getItem("authToken");
    const response = await fetch(`http://${host}:8000/status`, {
      method: "GET",
      headers: {
        "AUTH": auth_token
      }
    });
    const data = await response.json()
    if (!response.ok) {
      throw new Error(`Failed to fetch status: ${response.status}`);
    }    
    console.log(data);
    return data;
  } catch (error) {
    throw error;
  }
}

// lib/api.js
export async function uploadVideo(host, file) {
  const auth_token = sessionStorage.getItem("authToken");
  const formData = new FormData();
  formData.append('file', file, file.name);

  try {
    const response = await fetch(`http://${host}:8000/upload`, {
      method: "POST",
      headers: {
        "AUTH": auth_token  // Changed from AUTH to X-Token to match API spec
        // Remove Content-Type header completely - browser will set it automatically
      },
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Upload failed with status:', response.status);
      console.error('Error details:', errorText);
      throw new Error(`Failed to upload video: ${response.status} ${errorText}`);
    }
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
}

export async function playVideo(host, videoName) {
  const auth_token =  sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/play`, {
    method: "POST",
    headers: {"AUTH": auth_token, "Content-Type": "application/json" },
    body: JSON.stringify({ video_name: videoName }),
  });
  if (!response.ok) throw new Error("Failed to play video");
}

export async function pauseVideo(host) {
  const auth_token =  sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/pause`, { headers:{"AUTH":auth_token}, method: "POST" });
  if (!response.ok) throw new Error("Failed to pause video");
}

export async function resumeVideo(host) {
  const auth_token = sessionStorage.getItem("authToken");

  const response = await fetch(`http://${host}:8000/resume`, {
    method: "POST",
    headers:{"AUTH":auth_token}
  });
  if (!response.ok) throw new Error("Failed to resume video");
}

export async function stopVideo(host) {
  const auth_token = sessionStorage.getItem("authToken");

  const response = await fetch(`http://${host}:8000/stop`, { method: "POST", headers:{"AUTH":auth_token}  });
  if (!response.ok) throw new Error("Failed to stop video");
}

export async function deleteVideo(host, videoName) {
  const auth_token = sessionStorage.getItem("authToken");

  const response = await fetch(`http://${host}:8000/video/${videoName}`, {
    method: "DELETE",
    headers:{"AUTH":auth_token}
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
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/tv/status`, {
    method: "GET",
    headers:{"AUTH":auth_token}
  });
  if (!response.ok) throw new Error("Failed to fetch the tv status.");
  return response.json();
}

export async function getSchedule(host) {

  const auth_token = sessionStorage.getItem("authToken");
  try {
    const response = await fetch(`http://${host}:8000/tv/get_schedule`, {headers: {"AUTH":auth_token} });
    if (!response.ok) throw new Error("Failed to fetch the schedule");
    return response.json();
  } catch {
    console.log("Failed to fetch the schedule. . . .");
  }
}

export async function saveSchedule(host, schedule) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/tv/set_schedule`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "AUTH":auth_token },
    body: JSON.stringify(schedule),
  });
  if (!response.ok) throw new Error("Failed to save schedule");
}

export async function deleteSchedule(host) {
  const auth_token = sessionStorage.getItem("authToken");
  try {
    const response = await fetch(`http://${host}:8000/tv/clear_schedule`, {
      method: "DELETE",
      headers: {"AUTH":auth_token}
    });
    if (!response.ok) throw new Error("Failed to clear the schedule");
    return response.json();
  } catch {
    console.log("Failed to delete the schedule. . . .");
  }
}

// TV Devices control API functions
export async function check_json(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/tv/check_json`, {
    method: "GET",
    headers: {"AUTH":auth_token}
  });
  if (!response.ok) throw new Error("Failed to fetch if the json file exists.");
  return response.json();
}

export async function set_hdmi_map(host, formData) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/tv/set_hdmi_map`, {
    method: "POST",
    headers: {"AUTH":auth_token, "Content-Type": "application/json"},
    body:JSON.stringify(formData),
  });
  console.log("The response is: ", response.status);
  if (!response.ok)
    throw new Error("Failed to set the hdmi map.");
}

export async function fetch_hdmi_map(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/tv/fetch_hdmi_map`, {
    method: "GET",
    headers: {"AUTH":auth_token},
  });
  if (!response.ok) throw new Error("Failed to fetch the hdmi map.");
  return response.json();
}

export async function getCurrentActiveDevice(host) {
  try {
    const auth_token = sessionStorage.getItem("authToken");
    const response = await fetch(`http://${host}:8000/tv/current`, {headers:{"AUTH":auth_token}, method: 'GET' });
    if (!response.ok) throw new Error("Failed to fetch the current device");
    const data = await response.json()
    return data;
  } catch {
    console.log("Failed to fetch the current device. . . .");
  }
}


export async function reset_hdmi_map(host) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/tv/reset`, {
    method: "POST",
    headers: {"AUTH":auth_token},
  });
  if (!response.ok) throw new Error("Failed to reset the hdmi map.");
}


export async function switchDevice(host, new_device) {
  const auth_token = sessionStorage.getItem("authToken");
  const response = await fetch(`http://${host}:8000/tv/switch/${new_device}`, {
    method: "POST",
    headers: {"AUTH":auth_token},
    body: JSON.stringify(new_device),
  });
  if (response.status === 500) console.error("Unable to switch device . . .");
}







