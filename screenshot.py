from mcp.server.fastmcp import FastMCP, Image # Image is still used internally by to_image_content, keep it for now or refactor if possible
import io
import os
from pathlib import Path
import pyautogui
from mcp.types import ImageContent # Keep ImageContent if take_screenshot_image is kept, otherwise remove
import logging
import sys
import datetime

# --- Logger Setup ---
log_file = "server.log"
logging.basicConfig(
    level=logging.INFO, # Change level to INFO for production, DEBUG if needed
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info("--- Screenshot Server Starting ---")
# --- End Logger Setup ---

# Create server
mcp = FastMCP("screenshot server")

# Removed take_screenshot and take_screenshot_image as direct AI interpretation is problematic

@mcp.tool()
def take_screenshot_path(path: str="./", name: str="screenshot.jpg") -> str:
    """Takes a screenshot and saves it to a specified path on the server machine."""
    logger.info(f"take_screenshot_path called with path='{path}', name='{name}'")
    buffer = io.BytesIO()
    try:
        screenshot = pyautogui.screenshot()
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data = buffer.getvalue()
        try:
            base_path = Path(path).resolve()
            save_path = (base_path / name).resolve()
            if not str(save_path).startswith(str(base_path)):
                logger.error(f"Invalid path specified. Attempted to save outside of {base_path}")
                return "failed: invalid path"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(image_data)
            logger.info(f"Successfully saved screenshot to {save_path}")
            return "success"
        except Exception as e:
            logger.error(f"Error writing screenshot to file: {e}", exc_info=True)
            return "failed: file write error"
    except Exception as e:
        logger.error(f"Error in take_screenshot_path (screenshot capture): {e}", exc_info=True)
        return "failed: screenshot capture error"

@mcp.tool()
def take_screenshot_and_return_path() -> str:
    """Takes a screenshot, saves it to images/latest_screenshot.jpg, and returns the absolute Windows path."""
    logger.info("take_screenshot_and_return_path called")
    buffer = io.BytesIO()
    try:
        screenshot = pyautogui.screenshot()
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data = buffer.getvalue()
        logger.debug(f"Image data length: {len(image_data)}")

        save_dir = Path("images")
        save_filename = "latest_screenshot.jpg"
        save_path = (save_dir / save_filename).resolve()
        save_dir.mkdir(parents=True, exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(image_data)
        logger.info(f"Screenshot saved to: {save_path}")
        return str(save_path)
    except Exception as e:
        logger.error(f"Error in take_screenshot_and_return_path: {e}", exc_info=True)
        return f"failed: {e}"

# Removed take_screenshot_and_create_resource (commented out placeholder)

def run():
    logger.info("Starting MCP server...")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.critical(f"MCP server failed to run: {e}", exc_info=True)
    finally:
        logger.info("--- Screenshot Server Stopping ---")

# Removed test_run function as clint.py will be removed

if __name__ == "__main__":
    run()