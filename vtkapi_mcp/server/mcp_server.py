"""MCP Server implementation for VTK API"""

import json
import logging
from pathlib import Path
from typing import List

from mcp.server import Server
from mcp.types import TextContent

from ..core.api_index import VTKAPIIndex
from ..validation.import_validator import ImportValidator
from .tools import get_tool_definitions

logger = logging.getLogger(__name__)


class VTKAPIMCPServer:
    """MCP Server for VTK API access"""
    
    def __init__(self, api_docs_path: Path):
        self.api_index = VTKAPIIndex(api_docs_path)
        self.import_validator = ImportValidator(self.api_index)
        self.server = Server("vtk-api")
        self._setup_tools()
    
    def _setup_tools(self):
        """Register all MCP tools"""
        
        @self.server.list_tools()
        async def list_tools():
            return get_tool_definitions()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls"""
            
            if name == "vtk_get_class_info":
                return self._handle_get_class_info(arguments)
            
            elif name == "vtk_search_classes":
                return self._handle_search_classes(arguments)
            
            elif name == "vtk_get_module_classes":
                return self._handle_get_module_classes(arguments)
            
            elif name == "vtk_validate_import":
                return self._handle_validate_import(arguments)
            
            elif name == "vtk_get_method_info":
                return self._handle_get_method_info(arguments)
            
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    def _handle_get_class_info(self, arguments: dict) -> List[TextContent]:
        """Handle vtk_get_class_info tool call"""
        class_name = arguments["class_name"]
        info = self.api_index.get_class_info(class_name)
        
        if info:
            result = {
                "class_name": info['class_name'],
                "module": info['module'],
                "content_preview": info['content'][:500] + "...",
                "methods": info.get('methods', [])
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        else:
            result = {
                "error": f"Class '{class_name}' not found in VTK API",
                "class_name": class_name,
                "found": False
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    def _handle_search_classes(self, arguments: dict) -> List[TextContent]:
        """Handle vtk_search_classes tool call"""
        query = arguments["query"]
        limit = arguments.get("limit", 10)
        results = self.api_index.search_classes(query, limit)
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
    
    def _handle_get_module_classes(self, arguments: dict) -> List[TextContent]:
        """Handle vtk_get_module_classes tool call"""
        module = arguments["module"]
        classes = self.api_index.get_module_classes(module)
        result = {
            "module": module,
            "classes": classes,
            "count": len(classes)
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    def _handle_validate_import(self, arguments: dict) -> List[TextContent]:
        """Handle vtk_validate_import tool call"""
        import_statement = arguments["import_statement"]
        result = self.import_validator.validate_import(import_statement)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    def _handle_get_method_info(self, arguments: dict) -> List[TextContent]:
        """Handle vtk_get_method_info tool call"""
        class_name = arguments["class_name"]
        method_name = arguments["method_name"]
        info = self.api_index.get_method_info(class_name, method_name)
        
        if info:
            return [TextContent(type="text", text=json.dumps(info, indent=2))]
        else:
            result = {
                "error": f"Method '{method_name}' not found in class '{class_name}'",
                "class_name": class_name,
                "method_name": method_name,
                "found": False
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("VTK API MCP Server starting...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
