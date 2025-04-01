# Screenshot Server

This project is a screenshot server written in Python. It provides the following main functions:

1.  **Screenshot Function**: By calling the `take_screenshot_image` tool, you can take a screenshot of the user's screen and return it as image data.
2.  **Image Processing**: Uses the Pillow library to process and display the captured images.
3.  **MCP Server**: Communicates with clients via the MCP protocol to provide screenshot services.

## Usage

1.  Ensure Python and the required dependencies are installed.
    ```
    $ uv sync
    ```
2.  Run the `clint.py` file to start the screenshot client (which in turn starts the server via MCP).
    ```
    $ uv run clint.py
    ```
3.  Use an MCP client to call the `take_screenshot_image` tool to get a screenshot.


## Available Tools

This server provides the following tools via the MCP protocol:

*   **`take_screenshot()`**
    *   Description: Takes a screenshot of the user's screen.
    *   Returns: An MCP `Image` object containing the screenshot data (JPEG format, quality 60).
    *   Usage: Primarily intended for internal MCP communication where the client expects an `Image` object.

*   **`take_screenshot_image()`**
    *   Description: Takes a screenshot of the user's screen.
    *   Returns: An MCP `ImageContent` object, suitable for AI assistants capable of processing image content directly.
    *   Usage: Recommended tool for AI assistants to visually perceive the user's screen.

*   **`take_screenshot_path(path: str = "./", name: str = "screenshot.jpg")`**
    *   Description: Takes a screenshot and saves it as a JPEG file to the specified path on the machine where the *server* is running.
    *   Parameters:
        *   `path` (string, optional): The directory path where the screenshot file should be saved. Defaults to the server's current working directory (`./`).
        *   `name` (string, optional): The desired filename for the screenshot. Defaults to `screenshot.jpg`.
    *   Returns: A string indicating the result: `"success"` or `"failed"` (with details potentially printed to the server's console).
    *   Usage: Useful for saving screenshots as files for later review or sharing.

## Dependencies

- Python 3.x
- Pillow library
- MCP protocol related libraries


## WSL2 Setup for Windows Screenshots

If you are running the MCP Host (e.g., the AI assistant client) within WSL2 (like Ubuntu) but want to take screenshots of the Windows host machine, the following setup is required because `pyautogui` needs access to the Windows GUI:

1.  **Copy Project to Windows:**
    Copy the entire `screenshot-server` project directory from your WSL filesystem (e.g., `/home/user/projects/screenshot-server`) to a location on your Windows filesystem (e.g., `C:\Users\YourUser\projects\screenshot-server`).

2.  **Install Dependencies on Windows:**
    *   Ensure you have Python and `uv` installed on Windows.
    *   Open PowerShell or Command Prompt **on Windows**.
    *   Navigate (`cd`) to the project directory **on Windows** where you copied the files.
    *   Install the dependencies using `uv`, explicitly specifying your Windows Python executable path:
        ```powershell
        # Example using uv, replace paths as needed
        C:\path\to\your\windows\uv.exe sync -p C:\path\to\your\windows\python.exe
        ```
        (You might need to delete the `.venv` folder copied from WSL first if `uv sync` fails: `Remove-Item -Recurse -Force .venv`)

3.  **Configure MCP Host (on WSL):**
    Modify your MCP client's settings (e.g., `mcp_settings.json` used by the AI assistant) to launch the screenshot server **on Windows** via PowerShell. The MCP Host itself remains running in WSL.

    ```json
    {
      "mcpServers": {
        "Screenshot-server": {
          "command": "powershell.exe", // Call PowerShell from WSL
          "args": [
            "-Command",
            // Use Invoke-Command for robustness
            "Invoke-Command -ScriptBlock { cd '<YOUR_WINDOWS_PROJECT_COPY_PATH>'; & '<YOUR_WINDOWS_UV_PATH>' run screenshot.py }"
            // Example: "Invoke-Command -ScriptBlock { cd 'C:\\Users\\YourUser\\projects\\screenshot-server'; & 'C:\\Users\\YourUser\\.local\\bin\\uv.exe' run screenshot.py }"
          ]
        }
        // ... other servers
      }
    }
    ```
    *   Replace `<YOUR_WINDOWS_PROJECT_COPY_PATH>` with the actual path where you copied the project on Windows.
    *   Replace `<YOUR_WINDOWS_UV_PATH>` with the actual path to `uv.exe` on Windows.

This setup allows the WSL-based MCP Host to trigger the screenshot server on the Windows host, enabling `pyautogui` to capture the correct screen.

## MCP Configuration Example

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/Users/username/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/username/MCP",
        "run",
        "screenshot.py"
      ]
    }
  }
}
```
*(Note: The MCP configuration example shows how to configure a client to connect to this server. The paths should be adjusted based on the actual environment.)*

## File Structure

- `screenshot.py`: The MCP server providing the screenshot functionality.
- `clint.py`: An example MCP client used to call the screenshot server's tools.
- `README.md`: Project documentation.