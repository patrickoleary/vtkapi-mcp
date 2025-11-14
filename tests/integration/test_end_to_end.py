"""Integration tests for end-to-end workflows"""


class TestEndToEndValidation:
    """Test complete validation workflows"""
    
    def test_full_validation_workflow_valid(self, api_index, validator):
        """Test complete validation workflow with valid code"""
        code = """
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor

# Create reader
reader = vtkSTLReader()
reader.SetFileName('model.stl')
reader.Update()

# Create mapper
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(reader.GetOutputPort())

# Create actor
actor = vtkActor()
actor.SetMapper(mapper)
"""
        result = validator.validate_code(code)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_full_validation_workflow_multiple_errors(self, api_index, validator):
        """Test validation with multiple types of errors"""
        code = """
from vtkmodules.vtkCommonDataModel import vtkPolyDataMapper  # Wrong module
from vtkmodules.vtkIOGeometry import vtkFakeReader  # Non-existent class

reader = vtkFakeReader()  # Non-existent class
reader.SetFileName('test.stl')

mapper = vtkPolyDataMapper()
mapper.FakeMethod()  # Non-existent method
"""
        result = validator.validate_code(code)
        assert not result.is_valid
        assert len(result.errors) >= 2
        
        # Should have import error and class error at minimum
        error_types = {e.error_type for e in result.errors}
        assert 'import' in error_types or 'unknown_class' in error_types
    
    def test_search_and_validate_workflow(self, api_index, validator):
        """Test workflow of searching for class then validating its usage"""
        # Search for mapper classes
        results = api_index.search_classes("Mapper")
        assert len(results) > 0
        
        # Get the first result
        class_name = results[0]['class_name']
        module = results[0]['module']
        
        # Create code using the found class
        code = f"""
from {module} import {class_name}

mapper = {class_name}()
mapper.Update()
"""
        # Validate the code
        result = validator.validate_code(code)
        assert result.is_valid
    
    def test_method_lookup_and_validation(self, api_index, validator):
        """Test looking up method info and validating its usage"""
        # Get method info
        method_info = api_index.get_method_info("vtkPolyDataMapper", "SetInputData")
        assert method_info is not None
        
        # Use the method in code
        code = """
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper

mapper = vtkPolyDataMapper()
mapper.SetInputData(data)
"""
        result = validator.validate_code(code)
        assert result.is_valid


class TestAPIIndexIntegration:
    """Test VTKAPIIndex integration scenarios"""
    
    def test_cross_module_class_lookup(self, api_index):
        """Test looking up classes across different modules"""
        # Get classes from different modules
        rendering_classes = api_index.get_module_classes("vtkmodules.vtkRenderingCore")
        io_classes = api_index.get_module_classes("vtkmodules.vtkIOGeometry")
        
        assert len(rendering_classes) > 0
        assert len(io_classes) > 0
        
        # Verify they're in different modules
        assert "vtkPolyDataMapper" in rendering_classes
        assert "vtkSTLReader" in io_classes
    
    def test_class_info_completeness(self, api_index):
        """Test that class info contains all expected fields"""
        info = api_index.get_class_info("vtkPolyDataMapper")
        
        assert info is not None
        assert 'class_name' in info
        assert 'module' in info
        assert 'content' in info
        assert 'metadata' in info
        
        # Check nested structure
        assert 'structured_docs' in info['metadata']


class TestValidatorIntegration:
    """Test validator integration with various code patterns"""
    
    def test_complex_import_patterns(self, validator):
        """Test validation with various import patterns"""
        test_cases = [
            # Valid patterns
            ("import vtk", True),
            ("import vtkmodules.all as vtk", True),
            ("from vtkmodules.vtkRenderingCore import vtkActor", True),
            ("from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor", True),
        ]
        
        for code, should_be_valid in test_cases:
            result = validator.validate_code(code)
            assert result.is_valid == should_be_valid, f"Failed for: {code}"
    
    def test_realistic_rendering_pipeline(self, validator):
        """Test validation of realistic VTK rendering pipeline"""
        code = """
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor

# Read geometry
reader = vtkSTLReader()
reader.SetFileName('input.stl')

# Create mapper
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(reader.GetOutputPort())

# Create actor
actor = vtkActor()
actor.SetMapper(mapper)
actor.SetPosition(0, 0, 0)
"""
        result = validator.validate_code(code)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_error_message_quality(self, validator):
        """Test that error messages are informative"""
        code = """
from vtkmodules.vtkCommonDataModel import vtkPolyDataMapper

mapper = vtkPolyDataMapper()
"""
        result = validator.validate_code(code)
        assert not result.is_valid
        
        error_message = result.format_errors()
        assert "vtkPolyDataMapper" in error_message
        assert "module" in error_message.lower()
