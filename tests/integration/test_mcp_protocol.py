"""Integration tests for actual MCP protocol communication"""

import asyncio
import json
import pytest
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
class TestMCPProtocolIntegration:
    """Test vtkapi-mcp through actual MCP protocol (not mocked)"""
    
    async def test_mcp_server_startup_and_tools(self, temp_api_docs_file):
        """Test server starts and lists tools via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List tools via MCP protocol
                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                
                assert len(tool_names) == 5
                assert "vtk_get_class_info" in tool_names
                assert "vtk_search_classes" in tool_names
                assert "vtk_get_module_classes" in tool_names
                assert "vtk_validate_import" in tool_names
                assert "vtk_get_method_info" in tool_names
    
    async def test_mcp_get_class_info_valid(self, temp_api_docs_file):
        """Test getting valid class info via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Call tool via MCP protocol
                result = await session.call_tool("vtk_get_class_info", {
                    "class_name": "vtkPolyDataMapper"
                })
                
                # Parse JSON response
                data = json.loads(result.content[0].text)
                
                assert data["class_name"] == "vtkPolyDataMapper"
                assert "module" in data
                assert "content_preview" in data
    
    async def test_mcp_get_class_info_invalid(self, temp_api_docs_file):
        """Test getting invalid class via MCP protocol returns proper error"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Call tool with non-existent class
                result = await session.call_tool("vtk_get_class_info", {
                    "class_name": "vtkFakeClass"
                })
                
                # Parse JSON error response
                data = json.loads(result.content[0].text)
                
                assert data["found"] == False
                assert "error" in data
                assert "vtkFakeClass" in data["error"]
    
    async def test_mcp_validate_import_correct(self, temp_api_docs_file):
        """Test validating correct import via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Validate correct import
                result = await session.call_tool("vtk_validate_import", {
                    "import_statement": "from vtkmodules.vtkRenderingCore import vtkPolyDataMapper"
                })
                
                data = json.loads(result.content[0].text)
                
                assert data["valid"] == True
    
    async def test_mcp_validate_import_wrong_module(self, temp_api_docs_file):
        """Test detecting wrong module import via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Validate import with wrong module
                result = await session.call_tool("vtk_validate_import", {
                    "import_statement": "from vtkmodules.vtkCommonDataModel import vtkPolyDataMapper"
                })
                
                data = json.loads(result.content[0].text)
                
                assert data["valid"] == False
                assert "suggested" in data
                assert "vtkRenderingCore" in data["suggested"]
    
    async def test_mcp_search_classes(self, temp_api_docs_file):
        """Test searching classes via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Search for classes
                result = await session.call_tool("vtk_search_classes", {
                    "query": "Mapper",
                    "limit": 5
                })
                
                classes = json.loads(result.content[0].text)
                
                assert isinstance(classes, list)
                assert len(classes) <= 5
                assert len(classes) > 0
    
    async def test_mcp_get_method_info_valid(self, temp_api_docs_file):
        """Test getting valid method via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get valid method
                result = await session.call_tool("vtk_get_method_info", {
                    "class_name": "vtkPolyDataMapper",
                    "method_name": "SetInputData"
                })
                
                data = json.loads(result.content[0].text)
                
                assert "method_name" in data
                assert data["method_name"] == "SetInputData"
                assert data["class_name"] == "vtkPolyDataMapper"
    
    async def test_mcp_get_method_info_invalid(self, temp_api_docs_file):
        """Test getting invalid method via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get non-existent method
                result = await session.call_tool("vtk_get_method_info", {
                    "class_name": "vtkPolyDataMapper",
                    "method_name": "FakeMethod"
                })
                
                data = json.loads(result.content[0].text)
                
                assert data["found"] == False
                assert "error" in data
                assert "FakeMethod" in data["error"]
    
    async def test_mcp_get_module_classes_valid(self, temp_api_docs_file):
        """Test getting classes from valid module via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get classes from valid module
                result = await session.call_tool("vtk_get_module_classes", {
                    "module": "vtkmodules.vtkRenderingCore"
                })
                
                data = json.loads(result.content[0].text)
                
                assert "module" in data
                assert data["module"] == "vtkmodules.vtkRenderingCore"
                assert "classes" in data
                assert isinstance(data["classes"], list)
                assert len(data["classes"]) > 0
                # Should contain at least vtkPolyDataMapper
                assert "vtkPolyDataMapper" in data["classes"]
    
    async def test_mcp_get_module_classes_invalid(self, temp_api_docs_file):
        """Test getting classes from non-existent module via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get classes from non-existent module
                result = await session.call_tool("vtk_get_module_classes", {
                    "module": "vtkmodules.vtkFakeModule"
                })
                
                data = json.loads(result.content[0].text)
                
                assert "module" in data
                assert "classes" in data
                # Empty list for non-existent module
                assert isinstance(data["classes"], list)
                assert len(data["classes"]) == 0
    
    async def test_mcp_validate_import_monolithic(self, temp_api_docs_file):
        """Test validating monolithic import via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Validate monolithic import (always valid)
                result = await session.call_tool("vtk_validate_import", {
                    "import_statement": "import vtk"
                })
                
                data = json.loads(result.content[0].text)
                
                assert data["valid"] == True
                assert "vtk" in data["message"].lower()
    
    async def test_mcp_search_classes_empty(self, temp_api_docs_file):
        """Test searching with no matches via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Search with query that won't match anything
                result = await session.call_tool("vtk_search_classes", {
                    "query": "xyzabc123notfound",
                    "limit": 10
                })
                
                classes = json.loads(result.content[0].text)
                
                assert isinstance(classes, list)
                assert len(classes) == 0
    
    async def test_mcp_validate_import_invalid_class(self, temp_api_docs_file):
        """Test validating import with non-existent class via MCP protocol"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "vtkapi_mcp", "--api-docs", str(temp_api_docs_file)],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Validate import with fake class
                result = await session.call_tool("vtk_validate_import", {
                    "import_statement": "from vtkmodules.vtkRenderingCore import vtkFakeClass"
                })
                
                data = json.loads(result.content[0].text)
                
                assert data["valid"] == False
                assert "vtkFakeClass" in data["message"]
