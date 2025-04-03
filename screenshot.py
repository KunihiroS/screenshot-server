from mcp.server.fastmcp import FastMCP, Image # Image might still be needed internally
import io
import os
from pathlib import Path
import pyautogui
from mcp.types import ImageContent # Keep ImageContent for potential future use or internal conversion
import base64 # Import base64 module
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
# The current approach focuses on saving the image to a file and returning the path or base64 data.

@mcp.tool()
def take_screenshot_path(path: str = "./", name: str = "screenshot.jpg") -> str:
    """Takes a screenshot and saves it to a specified path and filename.

    Provides flexibility in choosing the save location and filename on the server machine.

    **AI Assistant Usage Guideline:**
    - **Always ask the user for the desired save path and filename before using this tool.**
    - If the user says "save it here" or "save to the current workspace", ask for the explicit, absolute path.
    - For WSL environments where the Host is in WSL and the server is on Windows:
        - If the user provides a WSL path (e.g., /home/user/...), convert it to the corresponding Windows UNC path (e.g., \\\\wsl$\\DistroName\\home\\user\\...) before passing it to the 'path' argument.
        - If the user provides a Windows path (e.g., C:\\Users\\...), pass it directly.
    - Use the 'name' argument for the desired filename.

    Args:
        path (str, optional): The **Windows path** (or UNC path to WSL) where the server should save the screenshot directory.
                              Defaults to the server's current working directory (`./`).
        name (str, optional): The filename for the screenshot (e.g., "my_capture.jpg").
                              Defaults to "screenshot.jpg".

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
def take_screenshot_and_return_path(name: str = "latest_screenshot.jpg") -> str:
    """Takes a screenshot, saves it to images/ directory, and returns the absolute path.

    Saves the screenshot with the specified filename within the 'images' subdirectory
    relative to the server's execution directory. This is the primary tool for
    workflows requiring the file path for subsequent processing.

    Args:
        name (str, optional): The filename for the screenshot (e.g., "current_view.jpg").
                              Defaults to "latest_screenshot.jpg".

    Returns:
        str: The absolute path (e.g., Windows path like C:\\...) to the saved screenshot file,
             or "failed: [error message]" if an error occurs.
    """
    logger.info(f"take_screenshot_and_return_path called with name='{name}'")
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

# --- New Tool to Return Base64 Encoded Image ---
@mcp.tool()
def take_screenshot_and_return_base64() -> str:
    """Takes a screenshot and returns the image data as a Base64 encoded string.

    This allows the MCP Host (like an AI assistant) to potentially receive
    the image data directly for processing, compatible with APIs like Gemini.

    Returns:
        str: A Base64 encoded string representing the JPEG image,
             or a string starting with "failed: " on error.
    """
    logger.info("take_screenshot_and_return_base64 called")
    buffer = io.BytesIO()
    try:
        # Capture the screenshot
        screenshot = pyautogui.screenshot()
        # Convert and save to buffer as JPEG
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data_bytes = buffer.getvalue()
        logger.debug(f"Image data length (bytes): {len(image_data_bytes)}")

        # Encode the byte data to Base64
        base64_encoded_data = base64.b64encode(image_data_bytes)
        # Decode the base64 bytes into a UTF-8 string for returning
        base64_string = base64_encoded_data.decode('utf-8')
        logger.info(f"Returning Base64 encoded string (length: {len(base64_string)} chars)")

        return base64_string

    except Exception as e:
        logger.error(f"Error in take_screenshot_and_return_base64: {e}", exc_info=True)
        return f"failed: {e}" # Return error message
# --- End New Tool ---

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