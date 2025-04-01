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

## Dependencies

- Python 3.x
- Pillow library
- MCP protocol related libraries

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