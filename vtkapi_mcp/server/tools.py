"""MCP Tool definitions for VTK API"""

from mcp.types import Tool


def get_tool_definitions():
    """Get all MCP tool definitions"""
    return [
        Tool(
            name="vtk_get_class_info",
            description="Get complete information about a VTK class including module path, description, and methods",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "VTK class name (e.g., 'vtkPolyDataMapper')"
                    }
                },
                "required": ["class_name"]
            }
        ),
        Tool(
            name="vtk_search_classes",
            description="Search for VTK classes by name or keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (e.g., 'reader', 'mapper', 'actor')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="vtk_get_module_classes",
            description="List all VTK classes in a specific module",
            inputSchema={
                "type": "object",
                "properties": {
                    "module": {
                        "type": "string",
                        "description": "Module name (e.g., 'vtkmodules.vtkRenderingCore')"
                    }
                },
                "required": ["module"]
            }
        ),
        Tool(
            name="vtk_validate_import",
            description="Validate if a VTK import statement is correct and suggest corrections",
            inputSchema={
                "type": "object",
                "properties": {
                    "import_statement": {
                        "type": "string",
                        "description": "Python import statement to validate"
                    }
                },
                "required": ["import_statement"]
            }
        ),
        Tool(
            name="vtk_get_method_info",
            description="Get documentation for a specific method of a VTK class",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "VTK class name"
                    },
                    "method_name": {
                        "type": "string",
                        "description": "Method name"
                    }
                },
                "required": ["class_name", "method_name"]
            }
        )
    ]
