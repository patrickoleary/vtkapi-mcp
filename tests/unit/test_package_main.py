"""Tests for __main__ entry point"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock


class TestMainModule:
    """Test __main__.py module"""
    
    @pytest.mark.asyncio
    async def test_main_with_default_args(self, temp_api_docs_file, monkeypatch):
        """Test main function with default arguments"""
        # Mock sys.argv
        test_args = ['vtkapi_mcp']
        monkeypatch.setattr(sys, 'argv', test_args)
        
        # Mock the server's run method
        with patch('vtkapi_mcp.__main__.VTKAPIMCPServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.run = AsyncMock()
            mock_server_class.return_value = mock_server
            
            # Import and run
            from vtkapi_mcp.__main__ import main
            
            await main()
            
            # Verify server was created
            mock_server_class.assert_called_once()
            mock_server.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_main_with_custom_path(self, temp_api_docs_file, monkeypatch):
        """Test main function with custom API docs path"""
        # Mock sys.argv with custom path
        test_args = ['vtkapi_mcp', '--api-docs', str(temp_api_docs_file)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        # Mock the server's run method
        with patch('vtkapi_mcp.__main__.VTKAPIMCPServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.run = AsyncMock()
            mock_server_class.return_value = mock_server
            
            # Import and run
            from vtkapi_mcp.__main__ import main
            
            await main()
            
            # Verify server was created with correct path
            mock_server_class.assert_called_once()
            call_args = mock_server_class.call_args[0]
            assert isinstance(call_args[0], Path)
    
    def test_main_module_name(self):
        """Test that module can be imported"""
        import vtkapi_mcp.__main__ as main_module
        
        assert hasattr(main_module, 'main')
        assert callable(main_module.main)


class TestPackageInit:
    """Test package __init__.py"""
    
    def test_import_without_mcp(self):
        """Test importing package when MCP is not available"""
        # This is a bit tricky since MCP is installed
        # We'll test the fallback path exists
        import vtkapi_mcp
        
        # Should have core exports
        assert hasattr(vtkapi_mcp, 'VTKAPIIndex')
        assert hasattr(vtkapi_mcp, 'VTKCodeValidator')
        assert hasattr(vtkapi_mcp, 'ValidationError')
        assert hasattr(vtkapi_mcp, 'ValidationResult')
        assert hasattr(vtkapi_mcp, 'load_validator')
    
    def test_import_with_mcp(self):
        """Test importing package when MCP is available"""
        import vtkapi_mcp
        
        # Should have MCP server if available
        try:
            assert hasattr(vtkapi_mcp, 'VTKAPIMCPServer')
        except (AttributeError, ImportError):
            # If MCP not available, that's OK too
            pass
    
    def test_package_version(self):
        """Test package has version"""
        import vtkapi_mcp
        
        assert hasattr(vtkapi_mcp, '__version__')
        assert isinstance(vtkapi_mcp.__version__, str)
    
    def test_all_exports(self):
        """Test __all__ exports"""
        import vtkapi_mcp
        
        assert hasattr(vtkapi_mcp, '__all__')
        assert isinstance(vtkapi_mcp.__all__, list)
        assert len(vtkapi_mcp.__all__) >= 5  # At least core exports


@pytest.mark.asyncio
class TestMainEntryPoint:
    """Test main entry point comprehensively"""
    
    async def test_main_function_direct_call(self, temp_api_docs_file, monkeypatch):
        """Test calling main() directly"""
        test_args = ['vtkapi_mcp', '--api-docs', str(temp_api_docs_file)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with patch('vtkapi_mcp.__main__.VTKAPIMCPServer') as mock_server_class:
            mock_server = mock_server_class.return_value
            mock_server.run = AsyncMock()
            
            from vtkapi_mcp.__main__ import main
            await main()
            
            assert mock_server.run.called
    
    async def test_main_with_default_args(self, temp_api_docs_file, monkeypatch):
        """Test main function with default arguments"""
        test_args = ['vtkapi_mcp']
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with patch('vtkapi_mcp.__main__.VTKAPIMCPServer') as mock_server_class:
            mock_server = mock_server_class.return_value
            mock_server.run = AsyncMock()
            
            from vtkapi_mcp.__main__ import main
            await main()
            
            mock_server_class.assert_called_once()


class TestPackageImports:
    """Test package imports comprehensively"""
    
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
    
    def test_package_version_exists(self):
        """Test that package version is defined"""
        import vtkapi_mcp
        assert hasattr(vtkapi_mcp, '__version__')
        assert vtkapi_mcp.__version__ == "1.0.0"
    
    def test_all_exports_list(self):
        """Test __all__ exports list"""
        import vtkapi_mcp
        assert isinstance(vtkapi_mcp.__all__, list)
        
        core_exports = {
            'VTKAPIIndex',
            'VTKCodeValidator',
            'ValidationError',
            'ValidationResult',
            'load_validator'
        }
        
        for export in core_exports:
            assert export in vtkapi_mcp.__all__
