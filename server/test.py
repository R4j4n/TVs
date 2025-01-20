import asyncio
import io
import json
import logging
import os
import socket
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import uvicorn
import vlc
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image
from pydantic import BaseModel

from routers.control_tv import tv_controller

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoServer:
    def __init__(self, video_dir: str = "videos"):
        self.video_dir = Path(video_dir)
        self.video_dir.mkdir(exist_ok=True)

        # Create a hidden temporary directory for preview captures
        self.temp_dir = Path(tempfile.mkdtemp())
        self.preview_path = self.temp_dir / ".preview.png"

        # Initialize VLC instance with specific parameters
        self.vlc_instance = vlc.Instance("--no-snapshot-preview --quiet --no-overlay")
        self.player = self.vlc_instance.media_player_new()

        # Server state
        self.current_video: Optional[str] = None
        self.is_playing: bool = False
        self.last_played_file = Path("last_played.json")

        # Preview state
        self.preview_frame = None
        self.preview_lock = threading.Lock()
        self.last_preview_time = 0
        self.preview_interval = 1 / 30  # 30 FPS cap

        # Start preview capture thread
        self.preview_thread = threading.Thread(
            target=self._capture_preview, daemon=True
        )
        self.preview_thread.start()

        # Load last played video if exists
        self.load_last_played()

        # Attach event listener to handle loop playback
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(
            vlc.EventType.MediaPlayerEndReached, self._restart_video
        )

    def __del__(self):
        """Cleanup temporary directory on shutdown."""
        try:
            if self.temp_dir.exists():
                for file in self.temp_dir.iterdir():
                    file.unlink()
                self.temp_dir.rmdir()
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory: {e}")

    def _restart_video(self, event):
        """Restart the video when it ends."""
        logger.info(f"Restarting video: {self.current_video}")
        if self.current_video:
            self.play_video(self.current_video)

    def _capture_preview(self):
        """Continuously capture preview frames using a hidden temporary file."""
        while True:
            current_time = time.time()

            if (
                self.is_playing
                and (current_time - self.last_preview_time) >= self.preview_interval
            ):
                try:
                    # Take snapshot to hidden file
                    self.player.video_take_snapshot(0, str(self.preview_path), 0, 0)

                    # Quick check if file exists and has content
                    if (
                        self.preview_path.exists()
                        and self.preview_path.stat().st_size > 0
                    ):
                        with open(self.preview_path, "rb") as f:
                            frame_data = f.read()

                        # Update preview frame
                        with self.preview_lock:
                            self.preview_frame = frame_data

                        self.last_preview_time = current_time

                except Exception as e:
                    logger.error(f"Error capturing preview: {e}")

            time.sleep(0.01)  # Small sleep to prevent CPU overuse

    def get_preview_frame(self):
        """Get the latest preview frame."""
        with self.preview_lock:
            return self.preview_frame

    def load_last_played(self):
        """Load and automatically play the last played video on startup."""
        try:
            if self.last_played_file.exists():
                with open(self.last_played_file, "r") as f:
                    data = json.load(f)
                    if "last_video" in data:
                        self.play_video(data["last_video"])
        except Exception as e:
            logger.error(f"Error loading last played video: {e}")

    def save_last_played(self):
        """Save the currently playing video to persist between restarts."""
        try:
            with open(self.last_played_file, "w") as f:
                json.dump({"last_video": self.current_video}, f)
        except Exception as e:
            logger.error(f"Error saving last played video: {e}")

    def play_video(self, video_name: str) -> bool:
        """Play a video from the video directory."""
        video_path = self.video_dir / video_name
        if not video_path.exists():
            return False

        media = self.vlc_instance.media_new(str(video_path))
        self.player.set_media(media)
        self.player.play()
        self.current_video = video_name
        self.is_playing = True
        self.save_last_played()
        return True

    def stop_video(self):
        """Stop the currently playing video."""
        self.player.stop()
        self.is_playing = False

    def delete_video(self, video_name: str) -> bool:
        """Delete a video from the video directory."""
        video_path = self.video_dir / video_name
        if not video_path.exists():
            return False

        # Stop if this is the current video
        if self.current_video == video_name:
            self.stop_video()
            self.current_video = None

        try:
            video_path.unlink()
            return True
        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False

    def get_status(self) -> Dict:
        """Get the current player status."""
        return {
            "current_video": self.current_video,
            "is_playing": self.is_playing,
            "available_videos": [f.name for f in self.video_dir.glob("*")],
            "date_uploaded": [
                datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(self.video_dir, f.name))
                ).strftime("%I:%M %p %b %d %Y")
                for f in self.video_dir.glob("*")
            ],
        }


# FastAPI application
app = FastAPI()
app.include_router(tv_controller.router, prefix="/tv", tags=["TV Schedule APIs"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your client domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
video_server = VideoServer()


class PlayRequest(BaseModel):
    video_name: str


@app.post("/play")
async def play_video(request: PlayRequest):
    success = video_server.play_video(request.video_name)
    if success:
        return {"status": "success", "message": f"Playing {request.video_name}"}
    return JSONResponse(
        status_code=404, content={"status": "error", "message": "Video not found"}
    )


@app.post("/stop")
async def stop_video():
    video_server.stop_video()
    return {"status": "success", "message": "Video stopped"}


@app.get("/status")
async def get_status():
    return video_server.get_status()


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with open(video_server.video_dir / file.filename, "wb") as f:
            f.write(contents)
        return {"status": "success", "message": f"Uploaded {file.filename}"}
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "error", "message": str(e)}
        )


@app.delete("/video/{video_name}")
async def delete_video(video_name: str):
    success = video_server.delete_video(video_name)
    if success:
        return {"status": "success", "message": f"Deleted {video_name}"}
    return JSONResponse(
        status_code=404, content={"status": "error", "message": "Video not found"}
    )


async def preview_stream():
    """Generate preview frames for streaming."""
    while True:
        frame = video_server.get_preview_frame()
        if frame is not None:
            yield (b"--frame\r\n" b"Content-Type: image/png\r\n\r\n" + frame + b"\r\n")
        await asyncio.sleep(1 / 30)  # Cap at 30 FPS


@app.get("/preview")
async def get_preview():
    """Stream the video preview."""
    return StreamingResponse(
        preview_stream(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


import netifaces
from zeroconf import ServiceInfo, Zeroconf


def get_ip_address():
    """Get the IP address of the first available network interface"""
    interfaces = netifaces.interfaces()

    # Remove the loopback interface
    if "lo" in interfaces:
        interfaces.remove("lo")

    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            return addrs[netifaces.AF_INET][0]["addr"]

    # Fallback to localhost if no interface is found
    return "127.0.0.1"


def register_service():
    ip = get_ip_address()
    hostname = socket.gethostname()

    print(f"Registering service with IP: {ip}")  # Debug print

    info = ServiceInfo(
        "_pivideo._tcp.local.",
        f"{hostname}._pivideo._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=5000,
        properties={"hostname": hostname},
    )

    zeroconf = Zeroconf()
    zeroconf.register_service(info)
    return zeroconf


if __name__ == "__main__":
    zeroconf = register_service()
    uvicorn.run(app, host="0.0.0.0", port=8000)
