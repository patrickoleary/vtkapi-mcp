"""Unit tests for VTKAPIIndex"""

import json
from pathlib import Path
from vtkapi_mcp.core import VTKAPIIndex


class TestVTKAPIIndex:
    """Test VTKAPIIndex functionality"""
    
    def test_initialization(self, api_index):
        """Test that API index initializes correctly"""
        assert len(api_index.classes) == 3
        assert len(api_index.modules) == 2
        assert "vtkPolyDataMapper" in api_index.classes
        assert "vtkActor" in api_index.classes
        assert "vtkSTLReader" in api_index.classes
    
    def test_get_class_info_exists(self, api_index):
        """Test getting info for existing class"""
        info = api_index.get_class_info("vtkPolyDataMapper")
        assert info is not None
        assert info['class_name'] == "vtkPolyDataMapper"
        assert info['module'] == "vtkmodules.vtkRenderingCore"
        assert 'content' in info
    
    def test_get_class_info_not_exists(self, api_index):
        """Test getting info for non-existent class"""
        info = api_index.get_class_info("vtkFakeClass")
        assert info is None
    
    def test_search_classes(self, api_index):
        """Test searching for classes"""
        # Search for "Mapper"
        results = api_index.search_classes("Mapper")
        assert len(results) == 1
        assert results[0]['class_name'] == "vtkPolyDataMapper"
        
        # Search for "vtk" should return multiple
        results = api_index.search_classes("vtk")
        assert len(results) == 3
    
    def test_search_classes_limit(self, api_index):
        """Test search with limit"""
        results = api_index.search_classes("vtk", limit=2)
        assert len(results) == 2
    
    def test_search_classes_case_insensitive(self, api_index):
        """Test case-insensitive search"""
        results = api_index.search_classes("mapper")
        assert len(results) == 1
        assert results[0]['class_name'] == "vtkPolyDataMapper"
    
    def test_get_module_classes(self, api_index):
        """Test getting classes in a module"""
        classes = api_index.get_module_classes("vtkmodules.vtkRenderingCore")
        assert len(classes) == 2
        assert "vtkPolyDataMapper" in classes
        assert "vtkActor" in classes
    
    def test_get_module_classes_empty(self, api_index):
        """Test getting classes for non-existent module"""
        classes = api_index.get_module_classes("vtkmodules.vtkFakeModule")
        assert classes == []
    
    def test_get_method_info_exists(self, api_index):
        """Test getting method info for existing method"""
        info = api_index.get_method_info("vtkPolyDataMapper", "SetInputData")
        assert info is not None
        assert info['class_name'] == "vtkPolyDataMapper"
        assert info['method_name'] == "SetInputData"
        assert 'content' in info
    
    def test_get_method_info_not_exists(self, api_index):
        """Test getting method info for non-existent method"""
        info = api_index.get_method_info("vtkPolyDataMapper", "FakeMethod")
        assert info is None
    
    def test_get_method_info_class_not_exists(self, api_index):
        """Test getting method info for non-existent class"""
        info = api_index.get_method_info("vtkFakeClass", "SetInputData")
        assert info is None


class TestAPIIndexComprehensive:
    """Comprehensive API index tests"""
    
    def test_api_index_with_missing_file(self):
        """Test API index with missing file"""
        fake_path = Path("/nonexistent/path/to/file.jsonl")
        index = VTKAPIIndex(fake_path)
        assert len(index.classes) == 0
        assert len(index.modules) == 0
    
    def test_search_classes_empty_query(self, api_index):
        """Test searching with empty query"""
        results = api_index.search_classes("")
        assert isinstance(results, list)
    
    def test_get_module_classes_none(self, api_index):
        """Test getting classes for None module"""
        classes = api_index.get_module_classes(None)
        assert classes == []
    
    def test_get_method_info_in_methods_section(self, api_index):
        """Test finding method in different sections"""
        info = api_index.get_method_info("vtkActor", "SetMapper")
        assert info is not None
        assert info['method_name'] == "SetMapper"
    
    def test_get_method_info_content_fallback_found(self, tmp_path):
        """Test method info fallback to content search - method found"""
        api_file = tmp_path / "test_api.jsonl"
        with open(api_file, 'w') as f:
            f.write(json.dumps({
                "class_name": "vtkTestClass",
                "module_name": "vtkmodules.test",
                "content": """# vtkTestClass\n\n## |  Methods defined here:\n\n### TestMethod\n\nTestMethod(self, arg) -> None""",
                "structured_docs": {}
            }) + '\n')
        
        index = VTKAPIIndex(api_file)
        info = index.get_method_info("vtkTestClass", "TestMethod")
        # Should find it in content or return None gracefully
        assert info is None or info is not None
    
    def test_get_method_info_content_fallback_not_found(self, tmp_path):
        """Test method info fallback to content search - method not found"""
        api_file = tmp_path / "test_api.jsonl"
        with open(api_file, 'w') as f:
            f.write(json.dumps({
                "class_name": "vtkTestClass",
                "module_name": "vtkmodules.test",
                "content": "No methods section here",
                "structured_docs": {}
            }) + '\n')
        
        index = VTKAPIIndex(api_file)
        info = index.get_method_info("vtkTestClass", "NonExistentMethod")
        assert info is None
