from mcp.server.fastmcp import FastMCP, Image
import io
import os
from pathlib import Path
import pyautogui
from mcp.types import ImageContent

# Create server
mcp = FastMCP("screenshot server")

@mcp.tool()
def take_screenshot() -> Image:
    """
    Take a screenshot of the user's screen and return it as an image. Use
    this tool anytime the user wants you to look at something they're doing.
    """
    buffer = io.BytesIO()

    # Claude will refuse to process if the file size exceeds approximately 1MB.
    screenshot = pyautogui.screenshot()
    screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
    image_data = buffer.getvalue()
    print(f"Image data length: {len(image_data)}")  # Debug output
    return Image(data=image_data, format="jpeg")

@mcp.tool()
def take_screenshot_image() -> ImageContent:
    """
    Take a screenshot of the user's screen and return it as an image. Use
    """
    buffer = io.BytesIO()

    # Claude will refuse to process if the file size exceeds approximately 1MB.
    screenshot = pyautogui.screenshot()
    screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
    image_data = buffer.getvalue()
    print(f"Image data length: {len(image_data)}")  # Debug output
    return Image(data=image_data, format="jpeg").to_image_content()

@mcp.tool()
def take_screenshot_path(path: str="./", name: str="screenshot.jpg") -> str:
    """
    Take a screenshot of the user's screen and save it to a specified path. Use
    this tool anytime the user wants you to look at something they're doing.
    """
    buffer = io.BytesIO()

    # Claude will refuse to process if the file size exceeds approximately 1MB.
    screenshot = pyautogui.screenshot()
    screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
    # Save to local, capture exceptions

    try:
        # Use pathlib for safer path handling and validation
        base_path = Path(path).resolve()
        save_path = (base_path / name).resolve()

        # Ensure the save path is within the intended base directory
        if not str(save_path).startswith(str(base_path)):
            print(f"Error: Invalid path specified. Attempted to save outside of {base_path}")
            return "failed: invalid path"

        # Create directories if they don't exist
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(buffer.getvalue())
        return "success"
    except Exception as e:
        print(f"Error writing to file: {e}")
        return "failed"

def run():
    mcp.run(transport="stdio")

def test_run():
    print(take_screenshot())

if __name__ == "__main__":
    run()
    # test_run()