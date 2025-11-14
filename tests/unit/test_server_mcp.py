"""Unit tests for MCP server"""

import json
from vtkapi_mcp.server import VTKAPIMCPServer
from vtkapi_mcp.server.tools import get_tool_definitions


class TestVTKAPIMCPServer:
    """Test VTKAPIMCPServer"""
    
    def test_server_initialization(self, temp_api_docs_file):
        """Test server initializes correctly"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        assert server.api_index is not None
        assert server.import_validator is not None
        assert server.server is not None
    
    def test_handle_get_class_info_exists(self, temp_api_docs_file):
        """Test getting existing class info"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        result = server._handle_get_class_info({"class_name": "vtkPolyDataMapper"})
        
        assert len(result) == 1
        content = json.loads(result[0].text)
        assert content["class_name"] == "vtkPolyDataMapper"
        assert "module" in content
    
    def test_handle_get_class_info_not_exists(self, temp_api_docs_file):
        """Test getting non-existent class info"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        result = server._handle_get_class_info({"class_name": "vtkFakeClass"})
        
        assert len(result) == 1
        assert "not found" in result[0].text
    
    def test_handle_search_classes(self, temp_api_docs_file):
        """Test searching classes"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        result = server._handle_search_classes({"query": "Mapper", "limit": 10})
        
        assert len(result) == 1
        classes = json.loads(result[0].text)
        assert isinstance(classes, list)
        assert len(classes) > 0
    
    def test_handle_get_module_classes(self, temp_api_docs_file):
        """Test getting module classes"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        result = server._handle_get_module_classes({"module": "vtkmodules.vtkRenderingCore"})
        
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "classes" in data
        assert len(data["classes"]) > 0
    
    def test_handle_validate_import(self, temp_api_docs_file):
        """Test validating import"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        result = server._handle_validate_import({"import_statement": "import vtk"})
        
        assert len(result) == 1
        validation = json.loads(result[0].text)
        assert "valid" in validation
    
    def test_handle_get_method_info_exists(self, temp_api_docs_file):
        """Test getting existing method info"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        result = server._handle_get_method_info({
            "class_name": "vtkPolyDataMapper",
            "method_name": "SetInputData"
        })
        
        assert len(result) == 1
        info = json.loads(result[0].text)
        assert "method_name" in info
    
    def test_handle_get_method_info_not_exists(self, temp_api_docs_file):
        """Test getting non-existent method info"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        result = server._handle_get_method_info({
            "class_name": "vtkPolyDataMapper",
            "method_name": "FakeMethod"
        })
        
        assert len(result) == 1
        assert "not found" in result[0].text


class TestServerToolHandlers:
    """Test all server tool handler methods"""
    
    def test_all_tool_handlers(self, temp_api_docs_file):
        """Test all tool handler paths"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        # Test each handler method directly
        
        # 1. Get class info - exists
        result = server._handle_get_class_info({"class_name": "vtkPolyDataMapper"})
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert "class_name" in data
        
        # 2. Get class info - not exists
        result = server._handle_get_class_info({"class_name": "vtkFake"})
        assert len(result) == 1
        assert "not found" in result[0].text
        
        # 3. Search classes
        result = server._handle_search_classes({"query": "vtk", "limit": 5})
        assert len(result) == 1
        
        # 4. Get module classes
        result = server._handle_get_module_classes({"module": "vtkmodules.vtkRenderingCore"})
        assert len(result) == 1
        
        # 5. Validate import
        result = server._handle_validate_import({"import_statement": "import vtk"})
        assert len(result) == 1
        
        # 6. Get method info - exists
        result = server._handle_get_method_info({
            "class_name": "vtkPolyDataMapper",
            "method_name": "SetInputData"
        })
        assert len(result) == 1
        
        # 7. Get method info - not exists
        result = server._handle_get_method_info({
            "class_name": "vtkPolyDataMapper",
            "method_name": "FakeMethod"
        })
        assert len(result) == 1
        assert "not found" in result[0].text


class TestToolDefinitions:
    """Test tool definitions"""
    
    def test_get_tool_definitions_complete(self):
        """Test that all tools are properly defined"""
        tools = get_tool_definitions()
        
        assert len(tools) == 5
        tool_names = [t.name for t in tools]
        
        assert "vtk_get_class_info" in tool_names
        assert "vtk_search_classes" in tool_names
        assert "vtk_get_module_classes" in tool_names
        assert "vtk_validate_import" in tool_names
        assert "vtk_get_method_info" in tool_names
        
        # Verify each tool has proper schema
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')
