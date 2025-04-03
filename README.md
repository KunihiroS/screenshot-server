# Screenshot Server

This project is an MCP (Modular Communication Protocol) server written in Python. Its primary function is to take screenshots of the host machine's screen, save them as image files, and return the absolute path to the saved file. This is particularly useful in scenarios where an AI assistant (acting as an MCP Host) needs to visually perceive the user's screen but cannot directly process image data reliably via MCP.

The intended workflow is:
1. AI assistant calls the `take_screenshot_and_return_path` tool on this server.
2. This server takes a screenshot, saves it (e.g., to `images/latest_screenshot.jpg`).
3. This server returns the absolute Windows path to the saved file.
4. The AI assistant receives the path.
5. The AI assistant potentially converts the Windows path to a WSL path (if running in WSL).
6. The AI assistant passes the file path to another MCP server specialized in image analysis.
7. The image analysis server reads the file from the given path and returns the analysis results.

## Usage

1.  Ensure Python and the required dependencies are installed on the machine where this server will run (typically the Windows host if taking Windows screenshots).
    ```
    $ uv sync
    ```
2.  Configure your MCP Host (e.g., AI assistant client) to connect to this server. See the "WSL2 Setup" and "MCP Configuration Example" sections for guidance.
3.  Use the MCP Host to call the available tools (see below).

## Available Tools

This server provides the following tools via the MCP protocol:

*   **`take_screenshot_path(path: str = "./", name: str = "screenshot.jpg")`**
    *   Description: Takes a screenshot and saves it as a JPEG file to the specified path and filename on the machine where the *server* is running.
    *   Parameters:
        *   `path` (string, optional): The directory path where the screenshot file should be saved. Defaults to the server's current working directory (`./`).
        *   `name` (string, optional): The desired filename for the screenshot. Defaults to `screenshot.jpg`.
    *   Returns: A string indicating the result: `"success"` or `"failed: [error message]"`.
    *   Usage: Allows saving screenshots with custom names and locations.

*   **`take_screenshot_and_return_path()`**
    *   Description: Takes a screenshot, saves it to a predefined location (`images/latest_screenshot.jpg` relative to the server's execution directory), and returns the absolute path of the saved file (e.g., a Windows path like `C:\...`).
    *   Returns: A string containing the absolute path to the saved screenshot file, or `"failed: [error message]"` if an error occurs.
    *   Usage: The primary tool for the intended workflow where another service will access the saved file using the returned path.

## Dependencies

- Python 3.x
- pyautogui
- Pillow (implicitly used by pyautogui, but good to note)
- mcp library (`mcp[cli]>=1.4.1`)

## WSL2 Setup for Windows Screenshots

If you are running the MCP Host (e.g., the AI assistant client) within WSL2 (like Ubuntu) but want to take screenshots of the Windows host machine using this server, the following setup is required:

1.  **Place Project on Windows:**
    Ensure the `screenshot-server` project directory resides on your Windows filesystem (e.g., `C:\Users\YourUser\projects\screenshot-server`), not within the WSL filesystem.

2.  **Install Dependencies on Windows:**
    *   Ensure you have Python and `uv` installed on Windows.
    *   Open PowerShell or Command Prompt **on Windows**.
    *   Navigate (`cd`) to the project directory **on Windows**.
    *   Install the dependencies using `uv`, explicitly specifying your Windows Python executable path if needed:
        ```powershell
        # Example using uv, replace paths as needed
        C:\path\to\your\windows\uv.exe sync -p C:\path\to\your\windows\python.exe
        ```

3.  **Configure MCP Host (on WSL):**
    Modify your MCP client's settings (e.g., `mcp_settings.json`) to launch the screenshot server **on Windows** via PowerShell.

    ```json
    {
      "mcpServers": {
        "Screenshot-server": {
          "command": "powershell.exe", // Call PowerShell from WSL
          "args": [
            "-Command",
            // Use Invoke-Command for robustness
            "Invoke-Command -ScriptBlock { cd '<YOUR_WINDOWS_PROJECT_PATH>'; & '<YOUR_WINDOWS_UV_PATH>' run screenshot.py }"
            // Example: "Invoke-Command -ScriptBlock { cd 'C:\\Users\\YourUser\\projects\\screenshot-server'; & 'C:\\Users\\YourUser\\.local\\bin\\uv.exe' run screenshot.py }"
          ]
        }
        // ... other servers
      }
    }
    ```
    *   Replace `<YOUR_WINDOWS_PROJECT_PATH>` and `<YOUR_WINDOWS_UV_PATH>` with the actual paths on your Windows system.

This setup allows the WSL-based MCP Host to trigger the screenshot server on the Windows host.

## MCP Configuration Example (Generic)

This shows a generic client configuration. Adapt paths based on your environment (see WSL2 setup if applicable).

```json
{
  "mcpServers": {
    "screenshot-server": { // Use a descriptive name
      "command": "/path/to/python_or_uv", // e.g., /usr/bin/python3 or C:\Python310\python.exe
      "args": [
        // Arguments depend on how you run it
        // Example 1: Using uv
        // "/path/to/uv", "run", "screenshot.py"
        // Example 2: Running directly with python
         "screenshot.py"
      ],
      // Add 'cwd' if the command needs to be run from the project directory
      "cwd": "/path/to/screenshot-server"
    }
  }
}
```

## File Structure

- `screenshot.py`: The MCP server providing the screenshot functionality.
- `README.md`: Project documentation.
- `pyproject.toml`: Project metadata and dependencies.
- `uv.lock`: Lock file for dependencies.
- `.gitignore`: Specifies intentionally untracked files that Git should ignore.
- `.python-version`: Specifies the Python version (if using tools like pyenv).
- `server.log`: Log file generated by the server (if logging is enabled).
- `images/`: Directory where screenshots are saved by default by some tools.