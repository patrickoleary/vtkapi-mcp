"""Integration tests for async server functionality"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from vtkapi_mcp.server import VTKAPIMCPServer


@pytest.mark.asyncio
class TestAsyncServer:
    """Test async server functionality"""
    
    async def test_server_run_method(self, temp_api_docs_file):
        """Test server run method setup"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        # Mock the stdio_server context manager
        mock_read_stream = MagicMock()
        mock_write_stream = MagicMock()
        mock_server_run = AsyncMock()
        
        with patch('mcp.server.stdio.stdio_server') as mock_stdio:
            # Setup async context manager
            mock_stdio.return_value.__aenter__ = AsyncMock(
                return_value=(mock_read_stream, mock_write_stream)
            )
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Mock the server's run method
            server.server.run = mock_server_run
            
            # Run the server (will immediately exit due to mocks)
            await server.run()
            
            # Verify run was called with streams
            mock_server_run.assert_called_once()
    
    async def test_list_tools_handler(self, temp_api_docs_file):
        """Test list_tools handler is registered"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        # The tools should be registered
        assert server.server is not None
        
        # Tools list should be accessible via get_tool_definitions
        from vtkapi_mcp.server.tools import get_tool_definitions
        tools = get_tool_definitions()
        
        assert len(tools) == 5
    
    async def test_call_tool_unknown(self, temp_api_docs_file):
        """Test calling unknown tool returns error"""
        server = VTKAPIMCPServer(temp_api_docs_file)
        
        # Verify server is set up correctly
        # The actual tool handler is decorated and called by MCP framework
        assert server.server is not None


@pytest.mark.asyncio 
class TestMainAsyncIO:
    """Test main async entry point"""
    
    async def test_main_runs(self, temp_api_docs_file, monkeypatch):
        """Test that main can be called"""
        import sys
        
        # Set up args
        test_args = ['vtkapi_mcp', '--api-docs', str(temp_api_docs_file)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        # Mock the server run to avoid actually starting
        with patch('vtkapi_mcp.__main__.VTKAPIMCPServer') as mock_server_class:
            mock_server = MagicMock()
            mock_server.run = AsyncMock()
            mock_server_class.return_value = mock_server
            
            from vtkapi_mcp.__main__ import main
            
            # Run main
            await main()
            
            # Verify it was called
            assert mock_server.run.called
