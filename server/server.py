import json
import logging
import os
import shutil
import socket
from datetime import datetime
from enum import Enum
from pathlib import Path

import netifaces
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from videomanager import PlayerState, logger, video_manager
from zeroconf import ServiceInfo, Zeroconf

from routers.cec_list_hdmi import router_cec as cec_routers
from routers.control_tv import tv_controller
from routers.group_management import router as group_router


class PlayRequest(BaseModel):
    video_name: str


app = FastAPI(title="Robust Video Looper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tv_controller.router, prefix="/tv", tags=["TV Schedule APIs"])
app.include_router(cec_routers, prefix="/tv", tags=["TV HDMI APIs"])
app.include_router(group_router, prefix="/groups", tags=["Groups"])


@app.post("/upload")
async def upload_video(file: UploadFile, background_tasks: BackgroundTasks):
    """Upload and validate video file"""
    if not file.filename:
        raise HTTPException(400, "No file provided")

    allowed_extensions = {".mp4", ".avi", ".mkv", ".mov"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            400, f"Unsupported file type. Allowed types: {allowed_extensions}"
        )

    file_path = video_manager.upload_dir / file.filename
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(500, f"Failed to save file: {str(e)}")

    try:
        video_manager.load_video(str(file_path))

        # Add cleanup task
        background_tasks.add_task(logger.info, f"Video uploaded: {file.filename}")

        return JSONResponse(
            {
                "message": "Video uploaded and loaded successfully",
                "filename": file.filename,
            }
        )
    except Exception as e:
        logger.error(f"Failed to load video: {e}")
        # Clean up failed upload
        file_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to load video: {str(e)}")


@app.post("/play")
async def play_video(request: PlayRequest):
    """Play a video by name."""
    try:
        file_path = video_manager.upload_dir / request.video_name
        video_manager.load_video(str(file_path))
        video_manager.play()
        return {
            "status": "success",
            "message": f"Playing {request.video_name} in loop mode",
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/pause")
async def pause_video():
    """Pause video playback"""
    try:
        video_manager.pause()
        return {"message": "Video paused"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Pause error: {e}")
        raise HTTPException(500, f"Failed to pause video: {str(e)}")


@app.post("/stop")
async def stop_video():
    """Stop video playback"""
    try:
        video_manager.stop()
        return {"message": "Video stopped"}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Stop error: {e}")
        raise HTTPException(500, f"Failed to stop video: {str(e)}")


@app.get("/status")
async def get_status():
    """Match the status format of main code."""
    status = video_manager.get_status()
    videos = list(video_manager.upload_dir.glob("*.mp4"))

    return {
        "current_video": status["current_video"],
        "is_playing": status["is_playing"],
        "is_paused": status["status"] == PlayerState.PAUSED,
        "is_looping": status["is_looping"],
        "available_videos": [f.name for f in videos],
        "date_uploaded": [
            datetime.fromtimestamp(f.stat().st_mtime).strftime("%I:%M %p %b %d %Y")
            for f in videos
        ],
    }


@app.post("/resume")
async def resume_video():
    try:
        status = video_manager.get_status()
        if status["status"] == PlayerState.PAUSED:
            video_manager.play()
            return {"status": "success", "message": "Video resumed"}
        raise HTTPException(status_code=400, detail="Video is not paused")
    except Exception as e:
        logger.error(f"Failed to resume video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/videos")
async def list_videos():
    """List all uploaded videos"""
    try:
        videos = [
            f.name
            for f in video_manager.upload_dir.glob("*")
            if f.suffix.lower() in {".mp4", ".avi", ".mkv", ".mov"}
        ]
        return {"videos": videos}
    except Exception as e:
        logger.error(f"Failed to list videos: {e}")
        raise HTTPException(500, f"Failed to list videos: {str(e)}")


@app.get("/preview")
async def get_preview():
    status = video_manager.get_status()
    if status["status"] != PlayerState.PLAYING or not status["current_video"]:
        raise HTTPException(status_code=404, detail="No video is currently playing")

    try:
        current_video = Path(status["current_video"])
        uploaded_video_dir = str(
            Path(video_manager.upload_dir).joinpath(current_video.name)
        )
        compressed_path = video_manager.compressed_dir / current_video.name

        if not compressed_path.exists():

            logger.info(f"Compressing video: {video_manager.current_video}")
            video_manager.compressor.compress_video(
                input_path=str(uploaded_video_dir),
                output_path=str(compressed_path),
            )
            logger.info(f"Compression complete: {video_manager.current_video}")

        return StreamingResponse(open(compressed_path, "rb"), media_type="video/mp4")
    except Exception as e:
        logger.error(f"Error streaming preview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/video/{video_name}")
async def delete_video(video_name: str):
    try:
        video_path = video_manager.upload_dir / video_name
        compressed_path = video_manager.compressed_dir / video_name

        # Stop if currently playing
        if (
            video_manager.current_video
            and Path(video_manager.current_video).name == video_name
        ):
            video_manager.stop()
            video_manager.current_video = None

        # Delete files
        if video_path.exists():
            video_path.unlink()
        if compressed_path.exists():
            compressed_path.unlink()

        return {"status": "success", "message": f"Deleted {video_name}"}
    except Exception as e:
        logger.error(f"Failed to delete video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_ip_address() -> str:
    """Get the IP address of the first available network interface."""
    try:
        interfaces = [i for i in netifaces.interfaces() if i != "lo"]

        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]["addr"]

        return "127.0.0.1"
    except Exception as e:
        logger.error(f"Error getting IP address: {e}")
        return "127.0.0.1"


def register_service() -> Zeroconf:
    """Register the video server service using Zeroconf."""
    try:
        ip = get_ip_address()
        hostname = socket.gethostname()

        logger.info(f"Registering service with IP: {ip}")

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
    except Exception as e:
        logger.error(f"Error registering service: {e}")
        raise


if __name__ == "__main__":
    zeroconf = register_service()
    uvicorn.run(app, host="0.0.0.0", port=8000)
