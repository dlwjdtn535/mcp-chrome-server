# MCP Chrome Server

[![smithery badge](https://smithery.ai/badge/@dlwjdtn535/mcp-chrome-server)](https://smithery.ai/server/@dlwjdtn535/mcp-chrome-server)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-yellow.svg)](https://buymeacoffee.com/dlwjdtn535)

A Chrome server based on MCP (Model-Controller-Prompt) for browser automation.

## Installation

### Prerequisites
- Python 3.12
- Google Chrome browser installed
- uv (Python package installer) or Docker

### Installing via Smithery

```bash
npx -y @smithery/cli install @dlwjdtn535/mcp-chrome-server --client claude
```

### Configuration Setup

Choose one of the following setup methods based on your environment:

#### 1. Using uv (Recommended)

**Windows Setup:**
```json
{
  "mcpServers": {
    "mcp-chrome-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "%LOCALAPPDATA%\\Programs\\mcp-chrome-server\\src",
        "mcp-chrome-server"
      ],
      "env": {
        "CHROME_PROFILE_PATH": "%LOCALAPPDATA%\\Google\\Chrome\\User Data"
      }
    }
  }
}
```

**macOS Setup:**
```json
{
  "mcpServers": {
    "mcp-chrome-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/usr/local/bin/mcp-chrome-server/src",
        "mcp-chrome-server"
      ],
      "env": {
        "CHROME_PROFILE_PATH": "$HOME/Library/Application Support/Google/Chrome"
      }
    }
  }
}
```

**Linux Setup:**
```json
{
  "mcpServers": {
    "mcp-chrome-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/usr/local/bin/mcp-chrome-server/src",
        "mcp-chrome-server"
      ],
      "env": {
        "CHROME_PROFILE_PATH": "$HOME/.config/google-chrome"
      }
    }
  }
}
```

#### 2. Using Docker

```bash
# Pull the latest image first
docker pull dlwjdtn535/mcp-chrome-server:latest
```

```json
{
  "mcpServers": {
    "chrome-server-docker": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--init",
        "-e", "CHROME_PROFILE_PATH=/chrome-profile",
        "-v", "${CHROME_PROFILE_PATH}:/chrome-profile",
        "dlwjdtn535/mcp-chrome-server:latest"
      ]
    }
  }
}
```

## Configuration

### Chrome Profile Paths

Default Chrome profile paths for each operating system:

| OS | Path |
|---|---|
| Windows | `%LOCALAPPDATA%\Google\Chrome\User Data` |
| macOS | `~/Library/Application Support/Google/Chrome` |
| Linux | `~/.config/google-chrome` |

### Important Notes
- Close all running Chrome instances before starting the automation server
- Ensure proper permissions for the Chrome profile directory
- For Docker setup, make sure the volume mount path matches your system's Chrome profile path

### Credential Management

Securely store and manage login information using the system keychain:

```python
# Save credentials
result = tool_save_credentials(
    site="example.com",
    username="your_username",
    password="your_password"
)

# Retrieve saved credentials
result = tool_get_credentials(
    site="example.com",
    username="your_username"
)
```

## Key Features

### Browser Control

```python
# Open browser
result = tool_open_browser()

# Navigate to URL
result = tool_navigate(url="https://example.com")

# Close browser
result = tool_close_browser()
```

### Web Login

```python
result = tool_web_login(
    url="https://example.com/login",
    credentials={
        "username": "your_username",
        "password": "your_password"
    },
    selectors={
        "username": "#id",
        "password": "#pw",
        "submit": ".login-button"
    }
)
```

Special handling:
- Waits for user to solve CAPTCHA when detected
- Automatic detection of 2-factor authentication
- Detailed analysis of login failure scenarios

### Element Manipulation

```python
# Click element
result = tool_click(selector=".button")

# Type text
result = tool_type(
    selector="#input-field",
    text="Hello, World!"
)

# Get text
result = tool_get_text(selector=".content")

# Get multiple elements
result = tool_get_elements(selector=".items")
```

## Important Considerations

1. Chrome Profile Usage
   - Verify correct profile path configuration
   - Close all other Chrome windows using the profile

2. Automation Detection Prevention
   - Simulation of natural user behavior
   - Maintain appropriate delays between login attempts

3. Security
   - Always use system keychain for important credentials
   - Never expose credentials directly in environment variables or configuration files
