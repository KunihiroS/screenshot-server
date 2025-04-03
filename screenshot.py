from mcp.server.fastmcp import FastMCP, Image # Image might still be needed internally
import io
import os
from pathlib import Path
import pyautogui
from mcp.types import ImageContent # Keep ImageContent for potential future use or internal conversion
import logging
import sys
import datetime

# --- Logger Setup ---
log_file = "server.log"
logging.basicConfig(
    level=logging.INFO, # Set to INFO for general use, DEBUG for detailed troubleshooting
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a'), # Append to log file
        logging.StreamHandler(sys.stdout)      # Also print to console (useful if run directly)
    ]
)
logger = logging.getLogger(__name__)
logger.info("--- Screenshot Server Starting ---")
# --- End Logger Setup ---

# Create server instance
mcp = FastMCP("screenshot server")

# Note: Tools returning raw image data (like the original take_screenshot/take_screenshot_image)
# were removed because AI interpretation via MCP showed inconsistencies.
# The current approach focuses on saving the image to a file and returning the path.

@mcp.tool()
def take_screenshot_path(path: str = "./", name: str = "screenshot.jpg") -> str:
    """
    Takes a screenshot and saves it to a specified path and filename on the server machine.

    This tool provides flexibility in choosing the save location and filename.

    Args:
        path (str, optional): The directory path to save the screenshot.
                              Defaults to the server's current working directory.
        name (str, optional): The filename for the screenshot. Defaults to "screenshot.jpg".

    Returns:
        str: "success" if saved successfully, otherwise "failed: [error message]".
    """
    logger.info(f"take_screenshot_path called with path='{path}', name='{name}'")
    buffer = io.BytesIO()
    try:
        # Capture the screenshot
        screenshot = pyautogui.screenshot()
        # Convert and save to buffer as JPEG
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data = buffer.getvalue()
        logger.debug(f"Image data length: {len(image_data)}")

        # Process file saving
        try:
            base_path = Path(path).resolve()
            save_path = (base_path / name).resolve()

            # Security check: Ensure the path doesn't escape the intended directory
            if not str(save_path).startswith(str(base_path)):
                logger.error(f"Invalid path specified (path traversal attempt?). Attempted save path: {save_path}, Base path: {base_path}")
                return "failed: invalid path"

            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the image data to the file
            with open(save_path, "wb") as f:
                f.write(image_data)
            logger.info(f"Successfully saved screenshot to {save_path}")
            return "success"
        except Exception as e:
            logger.error(f"Error writing screenshot to file '{save_path}': {e}", exc_info=True)
            return "failed: file write error"
    except Exception as e:
        # Handle errors during screenshot capture itself
        logger.error(f"Error capturing screenshot: {e}", exc_info=True)
        return "failed: screenshot capture error"

@mcp.tool()
# Add optional 'name' argument with default
def take_screenshot_and_return_path(name: str = "latest_screenshot.jpg") -> str:
    """
    Takes a screenshot, saves it to the 'images' directory with the specified filename,
    and returns the absolute path to the saved file.

    Args:
        name (str, optional): The filename for the screenshot.
                              Defaults to "latest_screenshot.jpg".

    Returns:
        str: The absolute path (e.g., Windows path like C:\\...) to the saved screenshot file,
             or "failed: [error message]" if an error occurs.
    """
    logger.info("take_screenshot_and_return_path called")
    buffer = io.BytesIO()
    try:
        # Capture the screenshot
        screenshot = pyautogui.screenshot()
        # Convert and save to buffer as JPEG
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data = buffer.getvalue()
        logger.debug(f"Image data length: {len(image_data)}")

        # Define the fixed save location relative to the script's execution directory
        save_dir = Path("images")
        # Use the provided 'name' argument for the filename
        # Resolve to get the absolute path where the server is running
        save_path = (save_dir / name).resolve() # Use 'name' argument

        # Create the 'images' directory if it doesn't exist
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save the file
        with open(save_path, "wb") as f:
            f.write(image_data)
        logger.info(f"Screenshot saved to: {save_path}")

        # Return the absolute path as a string
        return str(save_path)

    except Exception as e:
        # Handle errors during screenshot capture or file saving
        logger.error(f"Error in take_screenshot_and_return_path: {e}", exc_info=True)
        return f"failed: {e}" # Return a failure indicator with the error

# Removed take_screenshot_and_create_resource as resource handling in mcp library was unclear

def run():
    """Starts the MCP server."""
    logger.info("Starting MCP server...")
    try:
        # Run the server, listening via stdio
        mcp.run(transport="stdio")
    except Exception as e:
        # Log critical errors if the server fails to start or run
        logger.critical(f"MCP server failed to run: {e}", exc_info=True)
    finally:
        # Log when the server stops
        logger.info("--- Screenshot Server Stopping ---")

# Removed test_run function

if __name__ == "__main__":
    # Entry point when the script is executed directly
    run()