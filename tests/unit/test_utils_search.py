"""Unit tests for utils/search.py"""

from vtkapi_mcp.utils.search import extract_description, extract_module


class TestSearch:
    """Test search utilities"""
    
    def test_extract_description(self):
        """Test extracting description from content"""
        content = """# vtkPolyDataMapper

**Module:** `vtkmodules.vtkRenderingCore`

vtkPolyDataMapper maps polygonal data to graphics primitives. This is a long description."""
        
        desc = extract_description(content)
        assert "vtkPolyDataMapper maps polygonal data to graphics primitives" in desc
    
    def test_extract_module(self):
        """Test extracting module from content"""
        content = """# vtkPolyDataMapper

**Module:** `vtkmodules.vtkRenderingCore`

Description here."""
        
        module = extract_module(content)
        assert module == "vtkmodules.vtkRenderingCore"
    
    def test_extract_module_not_found(self):
        """Test extracting module when not present"""
        content = "Some content without module info"
        module = extract_module(content)
        assert module is None
