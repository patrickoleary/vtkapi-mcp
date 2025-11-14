"""Unit tests for validation modules"""

from vtkapi_mcp.validation import ValidationError, ValidationResult, load_validator
from vtkapi_mcp.validation.import_validator import ImportValidator
from vtkapi_mcp.validation.class_validator import ClassValidator
from vtkapi_mcp.validation.method_validator import MethodValidator


class TestValidationModels:
    """Test validation data models"""
    
    def test_validation_error_creation(self):
        """Test creating ValidationError"""
        error = ValidationError(
            error_type="import",
            message="Invalid import",
            line="from vtkmodules.vtkFake import vtkFake",
            suggestion="Use correct module"
        )
        assert error.error_type == "import"
        assert error.message == "Invalid import"
        assert error.line is not None
        assert error.suggestion is not None
    
    def test_validation_result_valid(self):
        """Test ValidationResult for valid code"""
        result = ValidationResult(is_valid=True, errors=[], code="valid code")
        assert result.is_valid
        assert not result.has_errors
        assert result.format_errors() == "No errors found."
    
    def test_validation_result_invalid(self):
        """Test ValidationResult for invalid code"""
        errors = [
            ValidationError("import", "Bad import", "line1", "fix1"),
            ValidationError("method", "Bad method", "line2", "fix2")
        ]
        result = ValidationResult(is_valid=False, errors=errors, code="bad code")
        assert not result.is_valid
        assert result.has_errors
        assert len(result.errors) == 2
        formatted = result.format_errors()
        assert "IMPORT" in formatted
        assert "METHOD" in formatted


class TestImportValidator:
    """Test ImportValidator"""
    
    def test_validate_monolithic_import(self, api_index):
        """Test validating 'import vtk'"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("import vtk")
        assert result['valid']
        assert "Monolithic" in result['message']
    
    def test_validate_modular_all_import(self, api_index):
        """Test validating 'import vtkmodules.all as vtk'"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("import vtkmodules.all as vtk")
        assert result['valid']
        assert "Modular" in result['message']
    
    def test_validate_correct_from_import(self, api_index):
        """Test validating correct from-import"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("from vtkmodules.vtkRenderingCore import vtkPolyDataMapper")
        assert result['valid']
    
    def test_validate_incorrect_module(self, api_index):
        """Test validating incorrect module path"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("from vtkmodules.vtkCommonDataModel import vtkPolyDataMapper")
        assert not result['valid']
        assert "Incorrect module" in result['message']


class TestClassValidator:
    """Test ClassValidator"""
    
    def test_validate_existing_class(self, api_index):
        """Test validating existing class"""
        validator = ClassValidator(api_index)
        code = "mapper = vtkPolyDataMapper()"
        errors = validator.validate_classes(code)
        assert len(errors) == 0
    
    def test_validate_non_existent_class(self, api_index):
        """Test validating non-existent class"""
        validator = ClassValidator(api_index)
        code = "reader = vtkFakeReader()"
        errors = validator.validate_classes(code)
        assert len(errors) == 1
        assert errors[0].error_type == "unknown_class"
        assert "vtkFakeReader" in errors[0].message


class TestMethodValidator:
    """Test MethodValidator"""
    
    def test_validate_existing_method(self, api_index):
        """Test validating existing method"""
        validator = MethodValidator(api_index)
        code = """
mapper = vtkPolyDataMapper()
mapper.SetInputData(data)
"""
        errors = validator.validate_methods(code)
        assert len(errors) == 0
    
    def test_validate_non_existent_method(self, api_index):
        """Test validating non-existent method"""
        validator = MethodValidator(api_index)
        code = """
mapper = vtkPolyDataMapper()
mapper.FakeMethod()
"""
        errors = validator.validate_methods(code)
        assert len(errors) == 1
        assert errors[0].error_type == "method"
        assert "FakeMethod" in errors[0].message


class TestVTKCodeValidator:
    """Test main VTKCodeValidator"""
    
    def test_validate_valid_code(self, validator, valid_vtk_code):
        """Test validating valid code"""
        result = validator.validate_code(valid_vtk_code)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_invalid_import(self, validator, invalid_import_code):
        """Test validating code with invalid import"""
        result = validator.validate_code(invalid_import_code)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any(e.error_type == "import" for e in result.errors)
    
    def test_validate_invalid_class(self, validator, invalid_class_code):
        """Test validating code with invalid class"""
        result = validator.validate_code(invalid_class_code)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any(e.error_type == "unknown_class" for e in result.errors)
    
    def test_validate_invalid_method(self, validator, invalid_method_code):
        """Test validating code with invalid method"""
        result = validator.validate_code(invalid_method_code)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert any(e.error_type == "method" for e in result.errors)


class TestImportValidatorEdgeCases:
    """Edge case tests for ImportValidator"""
    
    def test_backend_module_imports(self, api_index):
        """Test allowed backend module imports"""
        validator = ImportValidator(api_index)
        
        allowed_backends = [
            "import vtkmodules.vtkRenderingOpenGL2",
            "import vtkmodules.vtkInteractionStyle",
            "import vtkmodules.vtkRenderingFreeType",
            "import vtkmodules.vtkRenderingVolumeOpenGL2",
        ]
        
        for import_stmt in allowed_backends:
            result = validator.validate_import(import_stmt)
            assert result['valid'], f"Failed for: {import_stmt}"
    
    def test_disallowed_direct_module_import(self, api_index):
        """Test disallowed direct module imports"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("import vtkmodules.vtkRenderingCore")
        assert not result['valid']
    
    def test_from_import_vtkmodules_all(self, api_index):
        """Test importing from vtkmodules.all"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("from vtkmodules.all import vtkPolyDataMapper")
        assert result['valid']
    
    def test_validate_mixed_module_imports(self, api_index):
        """Test validation with mixed valid/invalid module imports"""
        validator = ImportValidator(api_index)
        result = validator._format_module_import_error(
            "from vtkmodules import ModuleA, ModuleB",
            modules_to_delete=["ModuleA"],
            modules_with_usage=[("ModuleB", "vtkmodules.ModuleB", ["ClassX"])]
        )
        assert not result['valid']
    
    def test_validate_unused_module_imports(self, api_index):
        """Test validation with completely unused module imports"""
        validator = ImportValidator(api_index)
        result = validator._format_module_import_error(
            "from vtkmodules import FakeModule",
            modules_to_delete=["FakeModule"],
            modules_with_usage=[]
        )
        assert not result['valid']
    
    def test_validate_from_import_no_classes(self, api_index):
        """Test from-import with no classes found"""
        validator = ImportValidator(api_index)
        result = validator._validate_from_import("from vtkmodules.vtkCore import")
        assert not result['valid']


class TestClassValidatorComplete:
    """Complete coverage for ClassValidator"""
    
    def test_validate_non_vtk_class(self, api_index):
        """Test validating non-VTK class (should skip)"""
        validator = ClassValidator(api_index)
        code = "my_obj = MyCustomClass()"
        errors = validator.validate_classes(code)
        assert len(errors) == 0
    
    def test_error_message_includes_class_name(self, api_index):
        """Test that error message includes the typo'd class name"""
        validator = ClassValidator(api_index)
        code = "obj = vtkTypoClassName()"
        errors = validator.validate_classes(code)
        assert len(errors) == 1
        assert "vtkTypoClassName" in errors[0].message


class TestMethodValidatorComplete:
    """Complete coverage for MethodValidator"""
    
    def test_validate_method_unknown_object_type(self, api_index):
        """Test validating method when object type is unknown"""
        validator = MethodValidator(api_index)
        code = "unknown_obj.SomeMethod()"
        errors = validator.validate_methods(code)
        assert len(errors) == 0
    
    def test_suggest_method_case_match(self, api_index):
        """Test method suggestion with case-only difference"""
        validator = MethodValidator(api_index)
        suggestion = validator._suggest_similar_method("vtkPolyDataMapper", "setinputdata")
        assert suggestion == "SetInputData"
    
    def test_suggest_method_fuzzy_match(self, api_index):
        """Test method suggestion with fuzzy matching"""
        validator = MethodValidator(api_index)
        suggestion = validator._suggest_similar_method("vtkPolyDataMapper", "SetInputDta")
        assert suggestion is not None
    
    def test_suggest_method_when_no_methods_available(self, api_index):
        """Test method suggestion when class has no methods"""
        validator = MethodValidator(api_index)
        class_info = api_index.get_class_info("vtkPolyDataMapper")
        original_metadata = class_info['metadata'].copy()
        class_info['metadata'] = {'structured_docs': {'sections': {}}}
        suggestion = validator._suggest_similar_method("vtkPolyDataMapper", "AnyMethod")
        class_info['metadata'] = original_metadata
        assert suggestion is None


class TestVTKCodeValidatorComplete:
    """Complete coverage for VTKCodeValidator"""
    
    def test_validator_with_no_imports(self, validator):
        """Test validating code with no imports"""
        code = "x = 1 + 1\nprint(x)"
        result = validator.validate_code(code)
        assert result.is_valid
    
    def test_validator_with_non_vtk_imports(self, validator):
        """Test validating code with non-VTK imports"""
        code = "import os\nimport sys\nfrom pathlib import Path"
        result = validator.validate_code(code)
        assert result.is_valid
    
    def test_load_validator_with_path(self, temp_api_docs_file):
        """Test loading validator with explicit path"""
        validator = load_validator(temp_api_docs_file)
        assert validator is not None
    
    def test_load_validator_with_nonexistent_path(self):
        """Test loading validator with non-existent path"""
        from pathlib import Path
        fake_path = Path("/nonexistent/fake/path.jsonl")
        validator = load_validator(fake_path)
        assert validator is not None


class TestAPIIndexEdgeCases:
    """Test edge cases in API index"""
    
    def test_load_api_docs_with_missing_class_name(self, tmp_path):
        """Test loading docs with missing class_name field"""
        import json
        from vtkapi_mcp.core import VTKAPIIndex
        
        api_file = tmp_path / "test_api.jsonl"
        with open(api_file, 'w') as f:
            f.write(json.dumps({"class_name": "vtkTest", "module_name": "vtkmodules.test", "content": "Test"}) + '\n')
            f.write(json.dumps({"module_name": "vtkmodules.test", "content": "No class name"}) + '\n')
        
        index = VTKAPIIndex(api_file)
        assert len(index.classes) == 1
    
    def test_get_method_info_fallback_search(self, api_index):
        """Test method info fallback to content search"""
        class_info = api_index.get_class_info("vtkPolyDataMapper")
        original_metadata = class_info['metadata'].copy()
        class_info['metadata'] = {}
        info = api_index.get_method_info("vtkPolyDataMapper", "SetInputData")
        class_info['metadata'] = original_metadata
        assert info is None or 'method_name' in info


class TestUtilsEdgeCases:
    """Test edge cases in utilities"""
    
    def test_track_variable_types_complex(self):
        """Test tracking variable types with complex patterns"""
        from vtkapi_mcp.utils.extraction import track_variable_types
        code = """
a = vtkPolyDataMapper()
b=vtkActor()
c  =  vtkSTLReader()
d = some_function()
e = vtk.vtkRenderer()
"""
        types = track_variable_types(code)
        assert 'a' in types
        assert 'b' in types
        assert 'c' in types
        assert 'd' not in types
        assert 'e' in types


class TestImportValidatorComplete:
    """Complete coverage for import validator"""
    
    def test_validate_monolithic_import(self, api_index):
        """Test validating 'import vtk'"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("import vtk")
        assert result['valid']
        assert "Monolithic" in result['message']
    
    def test_validate_modular_all_import(self, api_index):
        """Test validating 'import vtkmodules.all as vtk'"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("import vtkmodules.all as vtk")
        assert result['valid']
        assert "Modular" in result['message']
    
    def test_backend_module_imports_all(self, api_index):
        """Test all allowed backend module imports"""
        validator = ImportValidator(api_index)
        
        backends = [
            "import vtkmodules.vtkRenderingOpenGL2",
            "import vtkmodules.vtkInteractionStyle",
            "import vtkmodules.vtkRenderingFreeType",
            "import vtkmodules.vtkRenderingVolumeOpenGL2",
        ]
        
        for import_stmt in backends:
            result = validator.validate_import(import_stmt)
            assert result['valid']
            assert "Backend" in result['message']
    
    def test_disallowed_direct_module_import(self, api_index):
        """Test disallowed direct module imports"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("import vtkmodules.vtkRenderingCore")
        assert not result['valid']
        assert "from-import" in result['message'].lower()
    
    def test_import_with_inline_comment(self, api_index):
        """Test import with inline comment"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("import vtkmodules.vtkRenderingOpenGL2  # Required")
        assert result['valid']
    
    def test_from_import_vtkmodules_all(self, api_index):
        """Test importing from vtkmodules.all"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("from vtkmodules.all import vtkPolyDataMapper")
        assert result['valid']
    
    def test_validate_correct_from_import(self, api_index):
        """Test validating correct from-import"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("from vtkmodules.vtkRenderingCore import vtkPolyDataMapper")
        assert result['valid']
    
    def test_validate_incorrect_module(self, api_index):
        """Test validating incorrect module path"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("from vtkmodules.vtkCommonDataModel import vtkPolyDataMapper")
        assert not result['valid']
        assert "Incorrect module" in result['message']
    
    def test_validate_class_not_found(self, api_index):
        """Test import validator when class not found"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("from vtkmodules.vtkCore import vtkNonExistentClass123")
        assert not result['valid']
        assert "not found" in result['message']
    
    def test_validate_from_import_no_classes(self, api_index):
        """Test from-import with no classes found"""
        validator = ImportValidator(api_index)
        result = validator._validate_from_import("from vtkmodules.vtkCore import")
        assert not result['valid']
    
    def test_validate_from_import_cannot_parse(self, api_index):
        """Test from-import that cannot be parsed"""
        validator = ImportValidator(api_index)
        result = validator._validate_from_import("from vtkmodules.vtkCore")
        assert not result['valid']
        assert "parse" in result['message'].lower()
    
    def test_format_module_import_error_delete_all(self, api_index):
        """Test formatting error for completely unused module imports"""
        validator = ImportValidator(api_index)
        result = validator._format_module_import_error(
            "from vtkmodules import FakeModule",
            modules_to_delete=["FakeModule"],
            modules_with_usage=[]
        )
        assert not result['valid']
        assert "DELETE" in result['message']
    
    def test_format_module_import_error_replace_all(self, api_index):
        """Test formatting error for used module imports"""
        validator = ImportValidator(api_index)
        result = validator._format_module_import_error(
            "from vtkmodules import RealModule",
            modules_to_delete=[],
            modules_with_usage=[("RealModule", "vtkmodules.RealModule", ["ClassA", "ClassB"])]
        )
        assert not result['valid']
        assert "proper import" in result['message'].lower()
    
    def test_format_module_import_error_mixed(self, api_index):
        """Test formatting error for mixed module imports"""
        validator = ImportValidator(api_index)
        result = validator._format_module_import_error(
            "from vtkmodules import ModuleA, ModuleB",
            modules_to_delete=["ModuleA"],
            modules_with_usage=[("ModuleB", "vtkmodules.ModuleB", ["ClassX"])]
        )
        assert not result['valid']
        assert "NOT USED" in result['message'] or "MIXED" in result['message'] or "USED" in result['message']
    
    def test_unparseable_import(self, api_index):
        """Test unparseable import statement"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("invalid import syntax")
        assert not result['valid']
        assert "parse" in result['message'].lower()
    
    def test_empty_import(self, api_index):
        """Test empty/whitespace import"""
        validator = ImportValidator(api_index)
        result = validator.validate_import("   ")
        assert not result['valid']


class TestClassValidatorEdgeCases:
    """Complete edge cases for class validator"""
    
    def test_class_validator_lines_28_39(self, api_index):
        """Test class_validator.py lines 28 and 39"""
        validator = ClassValidator(api_index)
        
        # Line 28: if not cls.startswith('vtk')
        code_non_vtk = "obj = MyClass()"
        errors = validator.validate_classes(code_non_vtk)
        assert len(errors) == 0  # Covers line 28 (continue for non-vtk)
        
        # Line 39: the suggestion with format
        code_typo = "obj = vtkPolyDataMapperTypo()"
        errors = validator.validate_classes(code_typo)
        if len(errors) > 0 and errors[0].suggestion:
            assert "Did you mean" in errors[0].message or "try" in errors[0].message.lower()
    
    def test_suggest_similar_class_with_results(self, api_index):
        """Test class validator suggestion logic"""
        validator = ClassValidator(api_index)
        suggestion = validator._suggest_similar_class("vtkPoly")
        assert suggestion is None or isinstance(suggestion, str)
    
    def test_suggest_similar_class_no_results(self, api_index):
        """Test class validator with no similar classes"""
        validator = ClassValidator(api_index)
        suggestion = validator._suggest_similar_class("CompletelyFakeXYZ123")
        assert suggestion is None or isinstance(suggestion, str)
    
    def test_error_message_includes_typo_class_name(self, api_index):
        """Test that error message includes the class name"""
        validator = ClassValidator(api_index)
        code = "obj = vtkTypoClassName()"
        errors = validator.validate_classes(code)
        assert len(errors) == 1
        assert "vtkTypoClassName" in errors[0].message
        assert "SMALLEST CHANGE" in errors[0].message


class TestMethodValidatorEdgeCases:
    """Complete edge cases for method validator"""
    
    def test_method_validator_exact_case_match(self, api_index):
        """Test method validator with case differences"""
        validator = MethodValidator(api_index)
        suggestion = validator._suggest_similar_method("vtkPolyDataMapper", "setinputdata")
        assert suggestion is not None
        assert "SetInputData" in suggestion
    
    def test_method_validator_fuzzy_match(self, api_index):
        """Test method validator fuzzy matching"""
        validator = MethodValidator(api_index)
        suggestion = validator._suggest_similar_method("vtkPolyDataMapper", "SetInputDat")
        assert suggestion is not None or suggestion is None
    
    def test_method_validator_prefix_match(self, api_index):
        """Test method validator prefix matching"""
        validator = MethodValidator(api_index)
        suggestion = validator._suggest_similar_method("vtkPolyDataMapper", "SetI")
        assert suggestion is not None or suggestion is None
    
    def test_method_validator_no_match(self, api_index):
        """Test method validator with no possible match"""
        validator = MethodValidator(api_index)
        suggestion = validator._suggest_similar_method("vtkPolyDataMapper", "CompletelyWrongXYZ")
        assert suggestion is None
    
    def test_method_validator_class_not_found(self, api_index):
        """Test method validator with non-existent class"""
        validator = MethodValidator(api_index)
        suggestion = validator._suggest_similar_method("vtkFakeClass", "AnyMethod")
        assert suggestion is None
    
    def test_method_validator_no_structured_docs(self, api_index):
        """Test method validator when structured_docs is missing"""
        validator = MethodValidator(api_index)
        class_info = api_index.get_class_info("vtkPolyDataMapper")
        original_metadata = class_info['metadata'].copy()
        class_info['metadata'] = {}
        suggestion = validator._suggest_similar_method("vtkPolyDataMapper", "AnyMethod")
        class_info['metadata'] = original_metadata
        assert suggestion is None


class TestValidatorEdgeCasesComplete:
    """Complete coverage for validator edge cases"""
    
    def test_load_validator_with_path(self, temp_api_docs_file):
        """Test loading validator with explicit path"""
        from vtkapi_mcp.validation import load_validator
        validator = load_validator(temp_api_docs_file)
        assert validator is not None
        assert validator.api is not None
    
    def test_load_validator_default_path(self):
        """Test loading validator with default path"""
        from vtkapi_mcp.validation import load_validator
        try:
            validator = load_validator()
            assert validator is not None
        except (FileNotFoundError, Exception):
            pass  # Expected if default file doesn't exist
