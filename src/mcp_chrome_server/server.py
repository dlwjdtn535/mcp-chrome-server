"""MCP Chrome Server

This module implements a FastMCP server that provides Chrome browser automation capabilities.
It exposes various tools for browser control, web navigation, and credential management through
a standardized interface.

The server uses Selenium WebDriver for browser automation and system keychain for secure
credential storage. It provides a comprehensive set of tools for web automation tasks including:
- Browser control (open/close)
- Navigation and interaction (click, type, get text)
- Form automation and login
- Credential management
"""

import os
import sys
import logging
from typing import Dict, Any
import mcp
from .service import SeleniumService

from mcp.server.fastmcp import FastMCP

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP and Service
mcp = FastMCP()
service = SeleniumService()

# Register all service tools
for name in dir(service):
    if name.startswith('tool_'):
        tool_name = name[5:]  # Remove 'tool_' prefix
        tool_func = getattr(service, name)
        mcp.tool()(tool_func)

@mcp.prompt()
def prompt() -> Dict[str, Any]:
    """MCP Tool Definitions"""
    return {
        "tools": [
            {
                "name": "open_browser",
                "description": "Opens a new Chrome browser instance.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "close_browser",
                "description": "Closes the current Chrome browser instance.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "navigate",
                "description": "Navigates to the specified URL.",
                "parameters": {
                    "url": {
                        "type": "string",
                        "description": "URL to navigate to (including protocol)"
                    }
                },
                "required": ["url"]
            },
            {
                "name": "click",
                "description": "Finds and clicks an element on the page.",
                "parameters": {
                    "selector": {
                        "type": "string",
                        "description": "Selector of the element to click"
                    },
                    "by": {
                        "type": "string",
                        "description": "Selector type (css or xpath)",
                        "default": "css"
                    }
                },
                "required": ["selector"]
            },
            {
                "name": "type",
                "description": "Types text into an input field.",
                "parameters": {
                    "selector": {
                        "type": "string",
                        "description": "Selector of the element to type into"
                    },
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    },
                    "by": {
                        "type": "string",
                        "description": "Selector type (css or xpath)",
                        "default": "css"
                    }
                },
                "required": ["selector", "text"]
            },
            {
                "name": "get_text",
                "description": "Gets the text content of an element.",
                "parameters": {
                    "selector": {
                        "type": "string",
                        "description": "Selector of the element to get text from"
                    },
                    "by": {
                        "type": "string",
                        "description": "Selector type (css or xpath)",
                        "default": "css"
                    }
                },
                "required": ["selector"]
            },
            {
                "name": "get_elements",
                "description": "Finds and returns all elements matching the selector.",
                "parameters": {
                    "selector": {
                        "type": "string",
                        "description": "Selector for the elements to find"
                    },
                    "by": {
                        "type": "string",
                        "description": "Selector type (css or xpath)",
                        "default": "css"
                    }
                },
                "required": ["selector"]
            },
            {
                "name": "get_current_url",
                "description": "Returns the URL of the current page.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "get_title",
                "description": "Returns the title of the current page.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "get_page_source",
                "description": "Returns the HTML source of the current page.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "refresh",
                "description": "Refreshes the current page.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "back",
                "description": "Navigates back in browser history.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "forward",
                "description": "Navigates forward in browser history.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "execute_script",
                "description": "Executes JavaScript code.",
                "parameters": {
                    "script": {
                        "type": "string",
                        "description": "JavaScript code to execute"
                    }
                },
                "required": ["script"]
            },
            {
                "name": "get_cookies",
                "description": "Returns all cookies from the current page.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "add_cookie",
                "description": "Adds a cookie.",
                "parameters": {
                    "cookie": {
                        "type": "object",
                        "description": "Information about the cookie to add"
                    }
                },
                "required": ["cookie"]
            },
            {
                "name": "delete_cookie",
                "description": "Deletes a cookie with the specified name.",
                "parameters": {
                    "name": {
                        "type": "string",
                        "description": "Name of the cookie to delete"
                    }
                },
                "required": ["name"]
            },
            {
                "name": "delete_all_cookies",
                "description": "Deletes all cookies.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "set_window_size",
                "description": "Sets the size of the browser window.",
                "parameters": {
                    "width": {
                        "type": "integer",
                        "description": "Width of the window (pixels)"
                    },
                    "height": {
                        "type": "integer",
                        "description": "Height of the window (pixels)"
                    }
                },
                "required": ["width", "height"]
            },
            {
                "name": "get_window_size",
                "description": "Returns the size of the current browser window.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "maximize_window",
                "description": "Maximizes the browser window.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "minimize_window",
                "description": "Minimizes the browser window.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "fullscreen_window",
                "description": "Switches the browser window to full screen.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "take_screenshot",
                "description": "Saves a screenshot of the current page.",
                "parameters": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to save the screenshot to (optional)",
                        "default": None
                    }
                },
                "required": []
            },
            {
                "name": "switch_to_frame",
                "description": "Switches to a specific frame.",
                "parameters": {
                    "frame_reference": {
                        "type": "string",
                        "description": "Frame reference (selector or index)"
                    }
                },
                "required": ["frame_reference"]
            },
            {
                "name": "switch_to_default_content",
                "description": "Switches back to the default content.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "switch_to_window",
                "description": "Switches to a specific window.",
                "parameters": {
                    "window_handle": {
                        "type": "string",
                        "description": "Handle of the window to switch to"
                    }
                },
                "required": ["window_handle"]
            },
            {
                "name": "get_window_handles",
                "description": "Returns all window handles.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "close_current_window",
                "description": "Closes the current window.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "get_log",
                "description": "Gets browser logs.",
                "parameters": {
                    "log_type": {
                        "type": "string",
                        "description": "Type of logs to get"
                    }
                },
                "required": ["log_type"]
            },
            {
                "name": "implicitly_wait",
                "description": "Sets implicitly wait time.",
                "parameters": {
                    "seconds": {
                        "type": "integer",
                        "description": "Wait time (seconds)"
                    }
                },
                "required": ["seconds"]
            },
            {
                "name": "set_page_load_timeout",
                "description": "Sets page load timeout.",
                "parameters": {
                    "seconds": {
                        "type": "integer",
                        "description": "Timeout time (seconds)"
                    }
                },
                "required": ["seconds"]
            },
            {
                "name": "set_script_timeout",
                "description": "Sets script execution timeout.",
                "parameters": {
                    "seconds": {
                        "type": "integer",
                        "description": "Timeout time (seconds)"
                    }
                },
                "required": ["seconds"]
            },
            {
                "name": "save_credentials",
                "description": "Saves credentials securely.",
                "parameters": {
                    "site": {
                        "type": "string",
                        "description": "Web site domain"
                    },
                    "username": {
                        "type": "string",
                        "description": "User name"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password"
                    }
                },
                "required": ["site", "username", "password"]
            },
            {
                "name": "get_credentials",
                "description": "Retrieves saved credentials.",
                "parameters": {
                    "site": {
                        "type": "string",
                        "description": "Web site domain"
                    },
                    "username": {
                        "type": "string",
                        "description": "User name"
                    }
                },
                "required": ["site", "username"]
            },
            {
                "name": "web_login",
                "description": "Performs web site login.",
                "parameters": {
                    "url": {
                        "type": "string",
                        "description": "Login page URL"
                    },
                    "credentials": {
                        "type": "object",
                        "description": "Login information"
                    },
                    "selectors": {
                        "type": "object",
                        "description": "Selectors of login form elements"
                    },
                    "auth_type": {
                        "type": "string",
                        "description": "Authentication method",
                        "default": "form"
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "Selector of element to wait for after login",
                        "default": None
                    }
                },
                "required": ["url", "credentials", "selectors"]
            },
            {
                "name": "open_new_tab",
                "description": "Opens a new tab.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "switch_to_tab",
                "description": "Switches to a tab with the specified index.",
                "parameters": {
                    "index": {
                        "type": "integer",
                        "description": "Index of the tab to switch to (0-based)"
                    }
                },
                "required": ["index"]
            },
            {
                "name": "close_tab",
                "description": "Closes the current tab and switches to the previous tab.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "get_current_tab_index",
                "description": "Returns the index of the current tab.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "get_tab_count",
                "description": "Returns the total number of open tabs.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "get_tab_titles",
                "description": "Returns the titles of all open tabs.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "get_tab_urls",
                "description": "Returns the URLs of all open tabs.",
                "parameters": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            },
            {
                "name": "wait_for_element",
                "description": "Waits for an element to be present on the page.",
                "parameters": {
                    "selector": {
                        "type": "string",
                        "description": "Selector of the element to wait for"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum time to wait (seconds)",
                        "default": 10
                    },
                    "by": {
                        "type": "string",
                        "description": "Selector type (css or xpath)",
                        "default": "css"
                    }
                },
                "required": ["selector"]
            },
            {
                "name": "wait_for_element_visible",
                "description": "Waits for an element to be visible on the page.",
                "parameters": {
                    "selector": {
                        "type": "string",
                        "description": "Selector of the element to wait for"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum time to wait (seconds)",
                        "default": 10
                    },
                    "by": {
                        "type": "string",
                        "description": "Selector type (css or xpath)",
                        "default": "css"
                    }
                },
                "required": ["selector"]
            },
            {
                "name": "wait_for_element_clickable",
                "description": "Waits for an element to be clickable on the page.",
                "parameters": {
                    "selector": {
                        "type": "string",
                        "description": "Selector of the element to wait for"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum time to wait (seconds)",
                        "default": 10
                    },
                    "by": {
                        "type": "string",
                        "description": "Selector type (css or xpath)",
                        "default": "css"
                    }
                },
                "required": ["selector"]
            }
        ]
    }

def main():
    """
    Main entry point for the MCP Chrome server.
    
    This function initializes and runs the MCP server with the following steps:
    1. Starts the server and logs initialization
    2. Registers and logs available tools
    3. Runs the server using stdio transport
    4. Ensures proper cleanup on exit
    
    The server will automatically close any open browser sessions on shutdown.
    
    Raises:
        Exception: If server initialization or execution fails
    """
    try:
        logger.info("MCP Chrome server starting...")
        print("MCP Chrome server starting...", file=sys.stderr)

        # Log available tools
        tools = [name for name in dir(service) if name.startswith('tool_')]
        logger.info(f"Available tools: {[name[5:] for name in tools]}")

        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(e)
        print(f"Server execution failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Ensure browser is closed on exit
        try:
            service.tool_close_browser()
        except:
            pass

if __name__ == "__main__":
    main() 