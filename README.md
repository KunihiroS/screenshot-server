# Screenshot Server (File Path Focused)

This project provides an MCP (Modular Communication Protocol) server designed to capture screenshots and facilitate their use by other processes or AI assistants, primarily by **saving the screenshot to a file path specified by the client (Host)**.

## Core Problem & Solution

Directly interpreting screenshot image data sent via MCP by AI assistants proved unreliable in testing. This server adopts more robust workflows focused on file paths:

**Recommended Workflow (WSL Host -> Windows Server):**

1.  An MCP Host (like an AI assistant running in WSL) calls the `save_screenshot_to_host_workspace` tool, providing its **WSL workspace path** as an argument.
2.  This server (running on Windows) captures the screen.
3.  The server converts the received WSL path to a Windows-accessible UNC path (e.g., `\\wsl$\Distro\path`).
4.  The server saves the screenshot to the specified location within the Host's WSL filesystem via the UNC path.
5.  The server returns `"success"` or `"failed:..."`.
6.  The MCP Host knows the file is saved in its workspace (or a sub-directory if specified in the path argument).
7.  The MCP Host can then pass the **WSL path** to another specialized MCP server (running in WSL) for image analysis.

**Alternative Workflow (General):**

1.  MCP Host calls `take_screenshot_and_return_path`, optionally specifying a filename.
2.  Server saves the screenshot to its local `images/` directory.
3.  Server returns the **absolute path** (e.g., Windows path) to the saved file.
4.  MCP Host receives the path and passes it (with potential conversion) to an analysis server.

## Available Tools

This server currently offers the following tools:

*   **`save_screenshot_to_host_workspace(host_workspace_path: str, name: str = "workspace_screenshot.jpg")`**
    *   **Primary Use:** The **recommended** tool for saving screenshots directly into the AI Assistant's (Host's) WSL workspace, simplifying workflows.
    *   **Action:** Takes a screenshot and saves it to the specified Host's WSL workspace path. The server handles the conversion from WSL path to UNC path for saving. It automatically attempts to detect the WSL distribution name.
    *   **Args:**
        *   `host_workspace_path` (str): The absolute WSL path of the Host's workspace (e.g., `/home/user/project`). **Must start with `/`**.
        *   `name` (str, optional): The desired filename for the screenshot. Defaults to `workspace_screenshot.jpg`.
    *   **Returns:** `str` - `"success"` or `"failed: [error message]"`.

*   **`take_screenshot_and_return_path(name: str = "latest_screenshot.jpg")`**
    *   **Primary Use:** When saving to a fixed location *relative to the server* is acceptable, and the Host needs the absolute path for further processing.
    *   **Action:** Takes a screenshot, saves it to the `images/` subdirectory (relative to where the server script is running) with the specified filename, and returns the absolute path of the saved file.
    *   **Args:**
        *   `name` (str, optional): The filename for the screenshot. Defaults to `latest_screenshot.jpg`.
    *   **Returns:** `str` - The absolute path (e.g., a Windows path like `C:\...`) or `"failed: [error message]"`.

*   **`take_screenshot_path(path: str = "./", name: str = "screenshot.jpg")`**
    *   **Primary Use:** When maximum flexibility in specifying the save location (on the server machine) and filename is needed. Requires careful path handling by the caller, especially in WSL scenarios.
    *   **Action:** Takes a screenshot and saves it to the location specified by the `path` and `name` arguments on the server machine.
    *   **Args:**
        *   `path` (str, optional): The **Windows path** (or UNC path to WSL, e.g., `\\\\wsl$\\Distro\\...`) where the server should save the screenshot directory. Defaults to the server's working directory.
        *   `name` (str, optional): The filename. Defaults to `screenshot.jpg`.
    *   **Returns:** `str` - `"success"` or `"failed: [error message]"`.

## Setup and Usage

### 1. Prerequisites
*   **Python 3.x:** Required on the machine where the server will run.
*   **Dependencies:** Install using `uv`:
    ```bash
    uv sync
    ```
    Required libraries include `mcp[cli]>=1.4.1`, `pyautogui`, and `Pillow`.

### 2. Running the Server
This server is typically launched *by* an MCP Host based on its configuration.

### 3. Environment Considerations (Especially WSL2)

**Crucial Point:** To capture the **Windows screen**, this `screenshot.py` server **must run directly on Windows**.

**Recommended WSL2 Host -> Windows Server Setup:**

1.  **Project Location:** Place this `screenshot-server` project folder on your **Windows filesystem** (e.g., `C:\Users\YourUser\projects\screenshot-server`).
2.  **Windows Dependencies:** Install Python, `uv`, and project dependencies (`uv sync ...`) directly on **Windows** within the project folder.
3.  **MCP Host Configuration (in WSL):** Configure your MCP Host (running in WSL) to launch the server on Windows using PowerShell. Update `mcp_settings.json` (or equivalent):

    ```json
    {
      "mcpServers": {
        "Screenshot-server": {
          "command": "powershell.exe",
          "args": [
            "-Command",
            "Invoke-Command -ScriptBlock { cd '<YOUR_WINDOWS_PROJECT_PATH>'; & '<YOUR_WINDOWS_UV_PATH>' run screenshot.py }"
            // Example: "Invoke-Command -ScriptBlock { cd 'C:\\Users\\KUNI\\dev\\mcp_servers\\screenshot-server'; & 'C:\\Users\\KUNI\\.local\\bin\\uv.exe' run screenshot.py }"
          ]
        }
        // ... other servers ...
      }
    }
    ```
    *   Replace paths with your actual Windows paths.

### 4. Workflow Example (AI Assistant in WSL)
1.  AI Assistant identifies its current workspace path (e.g., `/home/user/current_project`).
2.  AI Assistant uses `use_mcp_tool` to call `save_screenshot_to_host_workspace` on `Screenshot-server`, passing `host_workspace_path="/home/user/current_project"` and optionally a `name`.
3.  Receives `"success"`.
4.  AI Assistant knows the screenshot is now at `/home/user/current_project/workspace_screenshot.jpg` (or the specified name).
5.  AI Assistant uses `use_mcp_tool` to call an *image analysis* server/tool (also running in WSL), passing the WSL path `/home/user/current_project/workspace_screenshot.jpg`.
6.  The image analysis server reads the file and performs its task.

## File Structure

*   `screenshot.py`: The core MCP server script.
*   `README.md`: This documentation file.
*   `pyproject.toml`: Project definition and dependencies for `uv`.
*   `uv.lock`: Dependency lock file.
*   `.gitignore`: Git ignore configuration.
*   `.python-version`: (Optional) Python version specifier.
*   `server.log`: Log file generated by the server.
*   `images/`: Default directory for `take_screenshot_and_return_path`.