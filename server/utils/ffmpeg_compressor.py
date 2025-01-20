import logging
import os
import subprocess
from typing import Literal, Union


class VideoCompressor:
    """
    A class to compress videos using FFmpeg, optimized for ARM architectures.
    Supports 240p, 480p, and 720p resolutions with customizable framerate.
    Audio is stripped for preview purposes.
    """

    ResolutionType = Literal[240, 480, 720]

    def __init__(self, target_resolution: ResolutionType, target_fps: int = 14):
        """
        Initialize the video compressor with target resolution.

        Args:
            target_resolution: Output video resolution (240, 480, or 720)
        """
        self.target_resolution = target_resolution
        self.target_fps = target_fps
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

        # Resolution mappings
        self.resolution_map = {
            240: "426:240",  # 240p (maintaining 16:9 aspect ratio)
            480: "854:480",  # 480p (maintaining 16:9 aspect ratio)
            720: "1280:720",  # 720p (maintaining 16:9 aspect ratio)
        }

        # Verify FFmpeg installation
        self._check_ffmpeg()

    def _setup_logging(self):
        """Configure logging for the compressor"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def _check_ffmpeg(self):
        """Verify FFmpeg is installed and accessible"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg first.")

    def compress_video(self, input_path: str, output_path: str, crf: int = 28) -> bool:
        """
        Compress the input video according to specified parameters.
        Audio is removed for preview purposes.

        Args:
            input_path: Path to input video file
            output_path: Path where compressed video will be saved
            crf: Constant Rate Factor for compression (18-51, higher means more compression)
                 Default is 28 for good compression while maintaining decent quality

        Returns:
            bool: True if compression successful, False otherwise
        """
        if not os.path.exists(input_path):
            self.logger.error(f"Input file not found: {input_path}")
            return False

        # Get target resolution from map
        resolution = self.resolution_map[self.target_resolution]

        try:
            # Construct FFmpeg command optimized for ARM, no audio
            command = [
                "ffmpeg",
                "-i",
                input_path,
                "-vf",
                f"scale={resolution}",  # Set resolution
                "-c:v",
                "libx264",  # Use H.264 codec
                "-preset",
                "ultrafast",  # Fastest encoding for preview
                "-crf",
                str(crf),  # Compression quality
                "-r",
                str(self.target_fps),  # Set framerate
                "-an",  # Remove audio
                "-pix_fmt",
                "yuv420p",  # Widely compatible pixel format
                "-tune",
                "fastdecode",  # Optimize for fast decoding
                "-movflags",
                "+faststart",  # Enable fast start for web playback
                "-y",  # Overwrite output file if exists
                output_path,
            ]

            self.logger.info(f"Starting compression of {input_path}")
            self.logger.info(f"Target resolution: {resolution}, FPS: {self.target_fps}")

            # Run FFmpeg command
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            if process.returncode == 0:
                self.logger.info("Video compression completed successfully")
                return True
            else:
                self.logger.error(f"FFmpeg error: {process.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Compression failed: {str(e)}")
            return False

    def get_video_info(self, video_path: str) -> Union[dict, None]:
        """
        Get information about the video file using FFprobe.

        Args:
            video_path: Path to video file

        Returns:
            dict: Video information or None if failed
        """
        try:
            command = [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                video_path,
            ]

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            if result.returncode == 0:
                import json

                return json.loads(result.stdout)
            return None

        except Exception as e:
            self.logger.error(f"Failed to get video info: {str(e)}")
            return None
