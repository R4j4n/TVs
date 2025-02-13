import json
import logging
import time
from enum import Enum
from pathlib import Path
from typing import Dict

import vlc

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


from src.video_compressor import VideoCompressor


class PlayerState(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    NO_MEDIA = "no_media"


class VideoManager:
    def __init__(self):
        self.upload_dir = Path("uploaded_videos")
        self.compressed_dir = self.upload_dir / "compressed"
        self.upload_dir.mkdir(exist_ok=True)
        self.compressed_dir.mkdir(exist_ok=True)
        self.last_played_file = Path("last_played.json")
        self.error_count = 0
        self.max_retry_attempts = 3
        self.retry_delay = 1
        self.current_video = None
        self.is_playing = False

        self.setup_vlc()
        self.load_last_played()
        self.compressor = VideoCompressor(target_resolution=240, target_fps=10)

    def setup_vlc(self):
        """Initialize VLC with robust settings"""
        try:
            vlc_args = [
                "--no-video-title-show",  # Hide title
                "--fullscreen",  # Force fullscreen
                "--mouse-hide-timeout=0",  # Hide mouse
                "--no-quiet",  # Show errors
                "--no-xlib",  # Better compatibility
                "--aout=alsa",  # Stable audio output
                "--file-logging",  # Enable logging
                "--logfile=vlc_log.txt",  # Log file
            ]

            self.instance = vlc.Instance(*vlc_args)
            self.media_list = self.instance.media_list_new()
            self.list_player = self.instance.media_list_player_new()
            self.list_player.set_media_list(self.media_list)
            self.list_player.set_playback_mode(vlc.PlaybackMode.loop)

            # Get the underlying media player for more control
            self.player = self.list_player.get_media_player()
            self.player.audio_set_volume(100)

            logger.info("VLC setup completed successfully")
        except Exception as e:
            logger.error(f"Failed to setup VLC: {e}")
            raise RuntimeError(f"Failed to initialize video player: {e}")

    def validate_video(self, video_path: str) -> bool:
        """Validate video file before playing"""
        try:
            test_media = self.instance.media_new(video_path)
            test_media.parse()
            duration = test_media.get_duration()

            if duration <= 0:
                logger.error(f"Invalid video duration: {duration}ms")
                return False

            # Check if file is readable
            with open(video_path, "rb") as f:
                f.seek(0, 2)  # Seek to end to verify file is readable

            logger.info(f"Video validation successful: {video_path}")
            return True

        except Exception as e:
            logger.error(f"Video validation failed: {e}")
            return False

    def load_video(self, video_path: str):
        if not Path(video_path).is_file():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not self.validate_video(video_path):
            raise ValueError("Invalid video file")

        try:
            self.media_list = self.instance.media_list_new()
            media = self.instance.media_new(video_path)
            media.parse()  # Wait for media to be parsed
            time.sleep(0.5)  # Small delay to ensure media is ready
            self.media_list.add_media(media)
            self.list_player.set_media_list(self.media_list)
            self.list_player.set_playback_mode(
                vlc.PlaybackMode.loop
            )  # Ensure loop mode

            self.error_count = 0
            self.current_video = video_path
            self.save_last_played()
            logger.info(f"Video loaded successfully: {video_path}")

        except Exception as e:
            logger.error(f"Failed to load video: {e}")
            self.error_count += 1
            raise

    def play(self):
        """Play video with error recovery"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            self.list_player.play()
            self.is_playing = True
            logger.info("Video playback started")

        except Exception as e:
            logger.error(f"Playback error: {e}")
            if self.error_count < self.max_retry_attempts:
                logger.info("Attempting playback recovery...")
                self.error_count += 1
                time.sleep(self.retry_delay)
                try:
                    # Reload video and try again
                    self.load_video(self.current_video)
                    self.list_player.play()
                    self.is_playing = True
                    logger.info("Playback recovery successful")
                except Exception as retry_error:
                    logger.error(f"Recovery failed: {retry_error}")
                    raise
            else:
                raise RuntimeError("Max retry attempts reached")

    def pause(self):
        """Pause video with state verification"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            self.list_player.pause()
            # Verify pause state
            time.sleep(0.1)  # Brief delay to let state update
            if self.list_player.get_state() == vlc.State.Paused:
                self.is_playing = False
                logger.info("Video paused successfully")
            else:
                raise RuntimeError("Failed to verify pause state")

        except Exception as e:
            logger.error(f"Failed to pause video: {e}")
            raise

    def stop(self):
        """Stop video with cleanup"""
        if not self.current_video:
            raise ValueError("No video loaded")

        try:
            self.list_player.stop()
            self.is_playing = False
            self.error_count = 0  # Reset error count
            logger.info("Video stopped successfully")

        except Exception as e:
            logger.error(f"Failed to stop video: {e}")
            raise

    def get_status(self) -> Dict:
        """Get comprehensive player status"""
        if not self.current_video:
            return {
                "current_video": None,
                "status": PlayerState.NO_MEDIA,
                "is_playing": False,
                "is_looping": True,
                "error_count": self.error_count,
                "volume": 0,
            }

        try:
            player_state = self.list_player.get_state()
            volume = self.player.audio_get_volume()

            status = {
                "current_video": Path(self.current_video).name,
                "status": self._map_vlc_state(player_state),
                "is_playing": self.is_playing,
                "is_looping": True,
                "error_count": self.error_count,
                "volume": volume,
            }

            # Add position info if playing
            if self.is_playing:
                status["position"] = self.player.get_position()
                status["time"] = self.player.get_time()

            return status

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"status": PlayerState.ERROR, "error": str(e)}

    def _map_vlc_state(self, state):
        """Map VLC states to PlayerState enum"""
        state_map = {
            vlc.State.Playing: PlayerState.PLAYING,
            vlc.State.Paused: PlayerState.PAUSED,
            vlc.State.Stopped: PlayerState.STOPPED,
            vlc.State.Error: PlayerState.ERROR,
        }
        return state_map.get(state, PlayerState.ERROR)

    def load_last_played(self):
        try:
            if self.last_played_file.exists():
                with open(self.last_played_file, "r") as f:
                    data = json.load(f)
                    if "last_video" in data:
                        video_path = self.upload_dir / data["last_video"]
                        if video_path.exists():
                            self.load_video(str(video_path))
                            self.play()  # Start playing the loaded video
                            logger.info(
                                f"Loaded and started playing last video: {data['last_video']}"
                            )
        except Exception as e:
            logger.error(f"Error loading last played video: {e}")

    def save_last_played(self):
        try:
            with open(self.last_played_file, "w") as f:
                json.dump({"last_video": Path(self.current_video).name}, f)
            logger.info(f"Saved last played video: {Path(self.current_video).name}")
        except Exception as e:
            logger.error(f"Error saving last played video: {e}")


# Create global video manager instance
video_manager = VideoManager()
