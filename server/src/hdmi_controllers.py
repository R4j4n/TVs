import logging
import subprocess


class CECController:
    def __init__(self):
        self.logger = self._setup_logging()

    def _setup_logging(self):
        logger = logging.getLogger("cec_controller")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _execute_cec_command(self, command: str) -> str:
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"CEC command failed: {e}")
            raise

    def switch_input(self, device_number: int) -> bool:
        try:
            device_hex = format(device_number * 16, "02x").upper()
            command = f'echo "tx 1F:82:{device_hex}:00" | cec-client -s -d 1'
            self._execute_cec_command(command)
            self.logger.info(f"Switched to input {device_number}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch input: {e}")
            return False
