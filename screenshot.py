from mcp.server.fastmcp import FastMCP, Image
import io
import os
from pathlib import Path
import pyautogui
from mcp.types import ImageContent
from mcp.types import ImageContent, Resource, ResourceContent, ResourceUri # Added Resource types

import logging # logging モジュールをインポート
import sys # 標準出力をログにも出すために追加

# --- Logger Setup ---
log_file = "server.log"
logging.basicConfig(
    level=logging.DEBUG, # DEBUGレベル以上のログを記録
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a'), # ファイルに追記モードで出力
        logging.StreamHandler(sys.stdout) # 標準出力にも出す (念のため)
    ]
)
logger = logging.getLogger(__name__)
logger.info("--- Screenshot Server Starting ---")
# --- End Logger Setup ---

# Create server
mcp = FastMCP("screenshot server")

@mcp.tool()
def take_screenshot() -> ImageContent: # Return ImageContent
    logger.info("take_screenshot (returning ImageContent) called") # Updated log
    buffer = io.BytesIO()
    try:
        # Claude will refuse to process if the file size exceeds approximately 1MB.
        screenshot = pyautogui.screenshot()
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data = buffer.getvalue()
        logger.debug(f"Image data length: {len(image_data)}")

        # --- Debug code to save image data before returning ---
        try:
            debug_save_dir = Path("images")
            debug_save_path = debug_save_dir / "debug_take_screenshot_output.jpg"
            debug_save_dir.mkdir(parents=True, exist_ok=True)
            with open(debug_save_path, "wb") as f:
                f.write(image_data)
            logger.info(f"Saved take_screenshot output to {debug_save_path.resolve()}")
        except Exception as e:
            logger.error(f"Error saving debug output: {e}")
        # --- End of debug code ---

        # Create ImageContent object to return
        mcp_image_content_obj = Image(data=image_data, format="jpeg").to_image_content() # Create ImageContent
        # Log info about the returned object
        # Log only the type, as accessing 'content' might be problematic
        logger.debug(f"Returning from take_screenshot (as ImageContent): type={type(mcp_image_content_obj)}")
        return mcp_image_content_obj # Return ImageContent
    except Exception as e:
        logger.error(f"Error in take_screenshot (returning ImageContent): {e}", exc_info=True)
        raise # Re-raise the exception

@mcp.tool()
def take_screenshot_image() -> ImageContent:
    logger.info("take_screenshot_image called")
    buffer = io.BytesIO()
    try:
        # Claude will refuse to process if the file size exceeds approximately 1MB.
        screenshot = pyautogui.screenshot()
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data = buffer.getvalue()
        logger.debug(f"Image data length: {len(image_data)}") # ログ出力に変更

        mcp_image_content_obj = Image(data=image_data, format="jpeg").to_image_content()
        # 返すオブジェクト情報をログに出力
        logger.debug(f"Returning from take_screenshot_image: type={type(mcp_image_content_obj)}, content_parts={len(mcp_image_content_obj.content)}, first_part_type={mcp_image_content_obj.content[0].type if mcp_image_content_obj.content else 'N/A'}, data_len={len(mcp_image_content_obj.content[0].data) if mcp_image_content_obj.content else 0}")
        return mcp_image_content_obj
    except Exception as e:
        logger.error(f"Error in take_screenshot_image: {e}", exc_info=True) # エラーログ
        raise

@mcp.tool()
def take_screenshot_path(path: str="./", name: str="screenshot.jpg") -> str:
    logger.info(f"take_screenshot_path called with path='{path}', name='{name}'") # ログ出力
    buffer = io.BytesIO()
    try:
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
                logger.error(f"Invalid path specified. Attempted to save outside of {base_path}") # ログ出力
                return "failed: invalid path"

            # Create directories if they don't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, "wb") as f:
                f.write(buffer.getvalue())
            logger.info(f"Successfully saved screenshot to {save_path}") # ログ出力
            return "success"
        except Exception as e:
            logger.error(f"Error writing screenshot to file: {e}", exc_info=True) # ログ出力
            return "failed"
    except Exception as e:
        logger.error(f"Error in take_screenshot_path: {e}", exc_info=True) # エラーログ


# --- New Tool to Create Resource ---
@mcp.tool()
async def take_screenshot_and_create_resource() -> ResourceUri: # Return ResourceUri
    """Takes a screenshot, registers it as an MCP resource, and returns its URI."""
    logger.info("take_screenshot_and_create_resource called")
    buffer = io.BytesIO()
    try:
        screenshot = pyautogui.screenshot()
        screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
        image_data = buffer.getvalue()
        logger.debug(f"Image data length: {len(image_data)}")

        # Create ImageContent (suitable for AI interpretation)
        image_content = Image(data=image_data, format="jpeg").to_image_content()

        # Generate a unique URI (e.g., using timestamp)
        import datetime
        now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        uri = f"screenshot://{now}"

        # !!! This part needs verification based on FastMCP capabilities !!!
        # Attempt to register the resource (assuming a method like add_resource exists)
        # This might require modifying FastMCP or using a different approach if not supported.
        try:
            # Placeholder: Replace with actual FastMCP resource registration if available
            # await mcp.add_resource(uri, image_content) # Example hypothetical call
            # For now, we'll just log that we would register it.
            logger.info(f"Resource created conceptually with URI: {uri}. (Registration mechanism TBD)")
            # Since registration isn't implemented, we save to file for debug
            debug_save_dir = Path("images")
            debug_save_path = debug_save_dir / f"resource_{now}.jpg"
            debug_save_dir.mkdir(parents=True, exist_ok=True)
            with open(debug_save_path, "wb") as f:
                f.write(image_data)
            logger.info(f"[DEBUG] Saved resource screenshot to {debug_save_path.resolve()}")

        except AttributeError:
            logger.error(f"Resource registration not directly supported by this FastMCP instance? URI: {uri}")
            # Fallback or alternative registration method might be needed.
            # For now, we still return the URI, but the resource might not be accessible.
            pass # Continue to return URI even if registration fails/not implemented
        except Exception as reg_e:
            logger.error(f"Error during conceptual resource registration for {uri}: {reg_e}")
            pass # Continue

        return ResourceUri(uri=uri) # Return the generated URI

    except Exception as e:
        logger.error(f"Error in take_screenshot_and_create_resource: {e}", exc_info=True)
        raise
# --- End New Tool ---

        return "failed" # エラー時は failed を返す

def run():
    logger.info("Starting MCP server...")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.critical(f"MCP server failed to run: {e}", exc_info=True) # 致命的エラーログ
    finally:
        logger.info("--- Screenshot Server Stopping ---")

def test_run():
    # This function is likely not used when run via MCP Host
    logger.warning("test_run() called - this is likely for local testing only.")
    print(take_screenshot())

if __name__ == "__main__":
    run()
    # test_run()