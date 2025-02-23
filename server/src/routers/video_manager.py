import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    Response,
    UploadFile,
)
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from src.video_manager import PlayerState

# Store the controller reference
video_manager = None
logger = None


def initialize_router_video_manager(controller):
    """Initialize the router with a CEC controller instance"""
    global video_manager
    video_manager = controller


def initialize_router_video_manager_logger(controller):
    """Initialize the router with a CEC controller instance"""
    global logger
    logger = controller


class PlayRequest(BaseModel):
    video_name: str


router_main = APIRouter(tags=["Video Controls"])


@router_main.post("/upload")
async def upload_video(
    original_file: UploadFile = File(...),
    compressed_file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """Upload and validate both original and compressed video files"""
    if not original_file.filename or not compressed_file.filename:
        raise HTTPException(400, "Both files must be provided")

    allowed_extensions = {".mp4", ".avi", ".mkv", ".mov"}
    original_ext = Path(original_file.filename).suffix.lower()
    if original_ext not in allowed_extensions:
        raise HTTPException(
            400, f"Unsupported file type. Allowed types: {allowed_extensions}"
        )

    try:
        # Save original file
        original_path = video_manager.upload_dir / original_file.filename
        with original_path.open("wb") as buffer:
            shutil.copyfileobj(original_file.file, buffer)

        # Save compressed file
        compressed_filename = compressed_file.filename.removeprefix("compressed_")
        compressed_path = video_manager.compressed_dir / compressed_filename
        with compressed_path.open("wb") as buffer:
            shutil.copyfileobj(compressed_file.file, buffer)

        # Load the original video for playback
        video_manager.load_video(str(original_path))

        # Add cleanup task
        background_tasks.add_task(
            logger.info, f"Videos uploaded: {original_file.filename}"
        )

        return JSONResponse(
            {
                "message": "Videos uploaded and loaded successfully",
                "original_filename": original_file.filename,
                "compressed_filename": compressed_file.filename,
            }
        )
    except Exception as e:
        logger.error(f"Failed to process videos: {e}")
        # Clean up failed uploads
        original_path.unlink(missing_ok=True)
        compressed_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to process videos: {str(e)}")


@router_main.post("/play")
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


@router_main.post("/pause")
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


@router_main.post("/stop")
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


@router_main.get("/status")
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


@router_main.post("/resume")
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


@router_main.get("/videos")
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


@router_main.get("/preview")
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


@router_main.delete("/video/{video_name}")
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
