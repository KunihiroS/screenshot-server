# Screenshot Server (File Path Focused)

This project provides an MCP (Modular Communication Protocol) server designed to capture screenshots and facilitate their use by other processes or AI assistants, primarily by **saving the screenshot to a file and returning its absolute path**.

## Core Problem & Solution

Directly interpreting screenshot image data sent via MCP by AI assistants proved unreliable in testing. This server adopts a more robust workflow:

1.  An MCP Host (like an AI assistant) calls the `take_screenshot_and_return_path` tool.
2.  This server captures the screen, saves it as `images/latest_screenshot.jpg` on the machine where the server is running.
3.  The server returns the **absolute file path** (e.g., `C:\Users\YourUser\...\latest_screenshot.jpg`) to the saved image.
4.  The MCP Host receives this path.
5.  The MCP Host can then pass this file path (potentially converting it if needed, e.g., Windows path to WSL path) to another specialized MCP server (or tool) responsible for image analysis or processing. That server reads the file directly from the shared filesystem.

## Available Tools

This server currently offers the following tools:

*   **`take_screenshot_and_return_path()`**
    *   **Primary Use:** The recommended tool for the workflow described above.
    *   **Action:** Takes a screenshot, saves it to a fixed location (`images/latest_screenshot.jpg` relative to where the server script is running), and returns the absolute path to the saved file.
    *   **Returns:** `str` - The absolute path (e.g., a Windows path) or a string starting with `"failed: "` on error.
    *   **Example Return:** `"C:\\Users\\YourUser\\projects\\screenshot-server\\images\\latest_screenshot.jpg"`

*   **`take_screenshot_path(path: str = "./", name: str = "screenshot.jpg")`**
    *   **Primary Use:** When you need to specify the exact save location and filename.
    *   **Action:** Takes a screenshot and saves it to the location specified by the `path` and `name` arguments on the server machine.
    *   **Parameters:**
        *   `path` (str, optional): Directory to save the file. Defaults to the server's working directory.
        *   `name` (str, optional): Filename for the screenshot. Defaults to `screenshot.jpg`.
    *   **Returns:** `str` - `"success"` or `"failed: [error message]"`.
    *   **Example Call:** Requesting to save to `C:\temp\myscreen.jpg` would involve calling the tool with `path="C:\\temp"` and `name="myscreen.jpg"`.

## Setup and Usage

### 1. Prerequisites
*   **Python 3.x:** Required on the machine where the server will run.
*   **Dependencies:** Install using `uv`:
    ```bash
    uv sync
    ```
    Required libraries include `mcp[cli]>=1.4.1`, `pyautogui`, and `Pillow`.

### 2. Running the Server
This server is typically launched *by* an MCP Host (like an AI assistant client) based on its configuration. Manual execution is usually only for direct testing.

### 3. Environment Considerations (Especially WSL2)

**Crucial Point:** `pyautogui` needs access to the graphical environment of the screen it's capturing. If you want to capture the **Windows screen** but run your MCP Host (AI Assistant) in **WSL2**, you **must** run this `screenshot.py` server directly on **Windows**, not inside WSL2.

**Recommended WSL2 Host -> Windows Server Setup:**

1.  **Project Location:** Place this `screenshot-server` project folder on your **Windows filesystem** (e.g., `C:\Users\YourUser\projects\screenshot-server`).
2.  **Windows Dependencies:** Install Python, `uv`, and the project dependencies (using `uv sync -p C:\path\to\python.exe`) directly on **Windows** within the project folder.
3.  **MCP Host Configuration (in WSL):** Configure your MCP Host (running in WSL) to launch the server on Windows using PowerShell. Update your `mcp_settings.json` (or equivalent):

    ```json
    {
      "mcpServers": {
        "Screenshot-server": { // Or your preferred server name
          "command": "powershell.exe", // Execute PowerShell from WSL
          "args": [
            "-Command",
            // Command executed by PowerShell: Change dir, then run server with uv
            "Invoke-Command -ScriptBlock { cd '<YOUR_WINDOWS_PROJECT_PATH>'; & '<YOUR_WINDOWS_UV_PATH>' run screenshot.py }"
          ]
        }
      }
    }
    ```
    *   **Replace `<YOUR_WINDOWS_PROJECT_PATH>`:** The full path to the project folder on Windows.
    *   **Replace `<YOUR_WINDOWS_UV_PATH>`:** The full path to `uv.exe` on Windows.

### 4. Workflow Example (AI Assistant)
1.  AI Assistant uses `use_mcp_tool` to call `take_screenshot_and_return_path` on the `Screenshot-server`.
2.  Receives the Windows path: `"C:\\Users\\...\\images\\latest_screenshot.jpg"`
3.  Converts path if necessary (e.g., to `/mnt/c/Users/.../images/latest_screenshot.jpg` if the AI Host is in WSL).
4.  AI Assistant uses `use_mcp_tool` to call an *image analysis* server/tool, passing the (converted) file path as an argument.
5.  The image analysis server reads the file and performs its task.

## File Structure

*   `screenshot.py`: The core MCP server script.
*   `README.md`: This documentation file.
*   `pyproject.toml`: Project definition and dependencies for `uv`.
*   `uv.lock`: Dependency lock file.
*   `.gitignore`: Git ignore configuration.
*   `.python-version`: (Optional) Python version specifier for tools like `pyenv`.
*   `server.log`: Log file generated by the server.
*   `images/`: Default directory created to store screenshots (e.g., `latest_screenshot.jpg`).