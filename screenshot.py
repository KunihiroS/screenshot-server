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
            # Resolve the path - this works for both Windows and UNC paths
            save_path_obj = Path(path) / name
            # Ensure the directory exists
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            # Resolve after ensuring directory exists, especially for UNC
            save_path = save_path_obj.resolve()

            # Security check (more robust check might be needed for UNC paths if strict confinement is required)
            # For simple cases, checking if the resolved path is valid might suffice here.
            # A basic check could involve ensuring it's not trying to write to system dirs, but UNC makes it tricky.
            # For now, we rely on the OS permissions and the user providing a valid target.
            # Consider adding checks based on expected base paths if needed.

            # Write the image data to the file
            with open(save_path, "wb") as f:
                f.write(image_data)
            logger.info(f"Successfully saved screenshot to {save_path}")
            return "success"
        except Exception as e:
            # Log the specific path that failed if possible
            logger.error(f"Error writing screenshot to file '{path}/{name}': {e}", exc_info=True)
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

# --- New Tool to Save to Host Workspace ---
@mcp.tool()
def save_screenshot_to_host_workspace(host_workspace_path: str, name: str = "workspace_screenshot.jpg") -> str:
    """Takes a screenshot and saves it to the specified Host's WSL workspace path.

    The server (running on Windows) converts the provided WSL path
    (e.g., /home/user/project) to a UNC path (e.g., \\\\wsl$\\Distro\\home\\user\\project)
    before saving.

    Args:
        host_workspace_path (str): The absolute WSL path of the Host's workspace.
        name (str, optional): The desired filename for the screenshot.
                              Defaults to "workspace_screenshot.jpg".

    Returns:
        str: "success" if saved successfully, otherwise "failed: [error message]".
    """
    logger.info(f"save_screenshot_to_host_workspace called with host_path='{host_workspace_path}', name='{name}'")
    buffer = io.BytesIO()
    try:
        # --- Convert WSL path to UNC path (with auto-detection attempt) ---
        if host_workspace_path.startswith('/'):
            distro_name = None
            try:
                import subprocess
                # Try to get the default WSL distribution name quietly
                result = subprocess.run(['wsl', '-l', '-q'], capture_output=True, text=True, check=True, encoding='utf-16le') # Use utf-16le for wsl output on Windows
                # Get the first line of the output, remove potential trailing "(Default)" and strip whitespace
                lines = result.stdout.strip().splitlines()
                if lines:
                    distro_name = lines[0].replace('(Default)', '').strip()
                    logger.info(f"Auto-detected WSL distribution: {distro_name}")
                else:
                    logger.warning("Could not auto-detect WSL distribution name from 'wsl -l -q'. Falling back to default.")
                    # Fallback to a common default if detection fails
                    distro_name = "Ubuntu-22.04"

            except FileNotFoundError:
                logger.error("'wsl.exe' command not found. Cannot auto-detect distribution. Falling back.")
                distro_name = "Ubuntu-22.04" # Fallback
            except subprocess.CalledProcessError as e:
                logger.error(f"Error running 'wsl -l -q': {e}. Falling back.")
                distro_name = "Ubuntu-22.04" # Fallback
            except Exception as e:
                 logger.error(f"Unexpected error during WSL distro detection: {e}. Falling back.")
                 distro_name = "Ubuntu-22.04" # Fallback

            if distro_name:
                unc_path_base = f"\\\\wsl$\\{distro_name}"
                windows_compatible_wsl_path = host_workspace_path.lstrip('/').replace('/', '\\')
                unc_save_dir = os.path.join(unc_path_base, windows_compatible_wsl_path)
                save_path_obj = Path(unc_save_dir) / name
                logger.info(f"Attempting to save to UNC path: {save_path_obj}")
            else:
                 logger.error("Failed to determine WSL distribution name.")
                 return "failed: could not determine WSL distribution"
        else:
            logger.error(f"Invalid WSL path provided: '{host_workspace_path}'. Path must start with '/'.")
            return "failed: invalid WSL path format"
        # --- End Path Conversion ---

        # Capture the screenshot
        screenshot = pyautogui.screenshot()
        # Convert and save to buffer as JPEG
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data = buffer.getvalue()
        logger.debug(f"Image data length: {len(image_data)}")

        # Process file saving using the UNC path
        try:
            # Create directory if it doesn't exist (using Path object)
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Write the image data to the file
            with open(save_path_obj, "wb") as f:
                f.write(image_data)
            logger.info(f"Successfully saved screenshot to WSL path via UNC: {save_path_obj}")
            return "success"
        except Exception as e:
            logger.error(f"Error writing screenshot to UNC path '{save_path_obj}': {e}", exc_info=True)
            # Provide more specific error if possible (e.g., permission denied, path not found)
            return f"failed: file write error to WSL path ({e})"

    except Exception as e:
        # Handle errors during screenshot capture itself
        logger.error(f"Error capturing screenshot: {e}", exc_info=True)
        return "failed: screenshot capture error"
# --- End New Tool ---

# --- Tool take_screenshot_and_return_base64 removed as direct interpretation was problematic ---

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