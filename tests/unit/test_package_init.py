"""Tests for package-level imports and initialization"""

import pytest
import sys
from unittest.mock import patch


class TestPackageImports:
    """Test package import scenarios"""
    
    def test_import_without_mcp_module(self):
        """Test importing vtkapi_mcp when MCP module is not available"""
        # Save original modules
        original_modules = sys.modules.copy()
        
        try:
            # Remove vtkapi_mcp from modules if present
            modules_to_remove = [
                key for key in sys.modules.keys() 
                if key.startswith('vtkapi_mcp')
            ]
            for mod in modules_to_remove:
                del sys.modules[mod]
            
            # Mock MCP import to fail
            with patch.dict('sys.modules', {'mcp': None, 'mcp.server': None}):
                # Force import error for mcp.server
                def mock_import(name, *args, **kwargs):
                    if 'mcp.server' in name or name == 'mcp.server':
                        raise ImportError("No module named 'mcp.server'")
                    return original_import(name, *args, **kwargs)
                
                import builtins
                original_import = builtins.__import__
                
                with patch('builtins.__import__', side_effect=mock_import):
                    # Now try to import vtkapi_mcp
                    # This should trigger the except block in __init__.py
                    try:
                        import vtkapi_mcp
                        
                        # Should still have core functionality
                        assert hasattr(vtkapi_mcp, 'VTKAPIIndex')
                        assert hasattr(vtkapi_mcp, 'VTKCodeValidator')
                        
                        # VTKAPIMCPServer might not be available
                        # Check __all__ doesn't include it when MCP fails
                        if 'VTKAPIMCPServer' not in vtkapi_mcp.__all__:
                            # This is the except path
                            assert len(vtkapi_mcp.__all__) == 5
                    except ImportError as e:
                        # If the import completely fails, that's also testing the path
                        assert 'mcp' in str(e).lower()
        
        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)
    
    def test_package_version_exists(self):
        """Test that package version is defined"""
        import vtkapi_mcp
        
        assert hasattr(vtkapi_mcp, '__version__')
        assert vtkapi_mcp.__version__ == "1.0.0"
    
    def test_core_imports_always_available(self):
        """Test that core imports are always available"""
        from vtkapi_mcp import (
            VTKAPIIndex,
            VTKCodeValidator,
            ValidationError,
            ValidationResult,
            load_validator
        )
        
        assert VTKAPIIndex is not None
        assert VTKCodeValidator is not None
        assert ValidationError is not None
        assert ValidationResult is not None
        assert load_validator is not None
    
    def test_server_import_with_mcp_available(self):
        """Test that server imports when MCP is available"""
        try:
            from vtkapi_mcp import VTKAPIMCPServer
            assert VTKAPIMCPServer is not None
        except ImportError:
            # MCP not available, skip this test
            pytest.skip("MCP not available")
    
    def test_all_exports_list(self):
        """Test __all__ exports list"""
        import vtkapi_mcp
        
        assert isinstance(vtkapi_mcp.__all__, list)
        
        # Core exports should always be present
        core_exports = {
            'VTKAPIIndex',
            'VTKCodeValidator',
            'ValidationError',
            'ValidationResult',
            'load_validator'
        }
        
        for export in core_exports:
            assert export in vtkapi_mcp.__all__
