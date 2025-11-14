"""Unit tests for utils/extraction.py"""

from vtkapi_mcp.utils.extraction import (
    extract_imports,
    extract_class_instantiations,
    extract_used_classes,
    track_variable_types,
    extract_method_calls_with_objects,
)


class TestExtraction:
    """Test extraction utilities"""
    
    def test_extract_imports_simple(self):
        """Test extracting simple imports"""
        code = """
import vtk
from vtkmodules.vtkRenderingCore import vtkActor
from vtkmodules.vtkIOGeometry import vtkSTLReader
"""
        imports = extract_imports(code)
        assert len(imports) == 3
        assert any("import vtk" in imp for imp in imports)
        assert any("vtkActor" in imp for imp in imports)
    
    def test_extract_imports_multiline(self):
        """Test extracting multiline imports"""
        code = """
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper
)
"""
        imports = extract_imports(code)
        assert len(imports) == 1
        assert "vtkActor" in imports[0]
        assert "vtkPolyDataMapper" in imports[0]
    
    def test_extract_class_instantiations(self):
        """Test extracting class instantiations"""
        code = """
mapper = vtkPolyDataMapper()
actor = vtkActor()
reader = vtkSTLReader()
"""
        classes = extract_class_instantiations(code)
        assert "vtkPolyDataMapper" in classes
        assert "vtkActor" in classes
        assert "vtkSTLReader" in classes
    
    def test_extract_used_classes(self):
        """Test extracting used classes"""
        code = """
mapper = vtkPolyDataMapper()
actor = vtkActor()
"""
        available = {"vtkPolyDataMapper", "vtkActor", "vtkFakeClass"}
        used = extract_used_classes(code, available)
        assert "vtkPolyDataMapper" in used
        assert "vtkActor" in used
        assert "vtkFakeClass" not in used
    
    def test_track_variable_types(self):
        """Test tracking variable types"""
        code = """
mapper = vtkPolyDataMapper()
actor = vtkActor()
reader = vtk.vtkSTLReader()
"""
        var_types = track_variable_types(code)
        assert var_types['mapper'] == "vtkPolyDataMapper"
        assert var_types['actor'] == "vtkActor"
        assert var_types['reader'] == "vtkSTLReader"
    
    def test_extract_method_calls_with_objects(self):
        """Test extracting method calls with objects"""
        code = """
mapper = vtkPolyDataMapper()
mapper.SetInputData(data)
mapper.Update()
actor = vtkActor()
actor.SetMapper(mapper)
"""
        calls = extract_method_calls_with_objects(code)
        assert len(calls) >= 3
        
        # Check specific calls
        obj_names = [call[0] for call in calls]
        method_names = [call[1] for call in calls]
        
        assert "mapper" in obj_names
        assert "SetInputData" in method_names
        assert "Update" in method_names
        assert "SetMapper" in method_names
