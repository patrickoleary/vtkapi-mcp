#!/usr/bin/env python3
"""
VTK API MCP Server - Integration Demo

Demonstrates using vtkapi-mcp as an actual MCP server (not standalone).
This shows the proper integration pattern that vtk-rag should use.
"""

import asyncio
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demo_mcp_tools():
    """Demonstrate MCP server integration"""
    
    # Server parameters
    api_docs_path = Path(__file__).parent / "data" / "vtk-python-docs.jsonl"
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "vtkapi_mcp", "--api-docs", str(api_docs_path)],
    )
    
    print("=" * 80)
    print("VTK API MCP Server Integration Demo")
    print("=" * 80)
    print(f"\nConnecting to MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✅ Connected to MCP server\n")
            
            # List available tools
            print("-" * 80)
            print("Available MCP Tools:")
            print("-" * 80)
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description}")
            print()
            
            # Demo 1: Get class info (valid class)
            print("=" * 80)
            print("Demo 1: Get Class Info - Valid Class")
            print("=" * 80)
            result = await session.call_tool("vtk_get_class_info", {
                "class_name": "vtkPolyDataMapper"
            })
            data = json.loads(result.content[0].text)
            print(f"✅ Class: {data['class_name']}")
            print(f"   Module: {data['module']}")
            print(f"   Methods: {len(data.get('methods', []))} methods")
            print()
            
            # Demo 2: Get class info (invalid class - catches hallucination)
            print("=" * 80)
            print("Demo 2: Get Class Info - Invalid Class (Hallucination)")
            print("=" * 80)
            print("Checking: 'vtkSuperAwesomeMapper' (doesn't exist)")
            result = await session.call_tool("vtk_get_class_info", {
                "class_name": "vtkSuperAwesomeMapper"
            })
            data = json.loads(result.content[0].text)
            print(f"❌ Error: {data['error']}")
            print(f"   Found: {data['found']}")
            print()
            
            # Demo 3: Search classes
            print("=" * 80)
            print("Demo 3: Search Classes")
            print("=" * 80)
            print("Query: 'Mapper'")
            result = await session.call_tool("vtk_search_classes", {
                "query": "Mapper",
                "limit": 5
            })
            classes = json.loads(result.content[0].text)
            print(f"Found {len(classes)} matching classes:")
            for cls in classes[:5]:
                print(f"  • {cls}")
            print()
            
            # Demo 4: Validate import (correct)
            print("=" * 80)
            print("Demo 4: Validate Import - Correct")
            print("=" * 80)
            import_stmt = "from vtkmodules.vtkRenderingCore import vtkPolyDataMapper"
            print(f"Code: {import_stmt}")
            result = await session.call_tool("vtk_validate_import", {
                "import_statement": import_stmt
            })
            data = json.loads(result.content[0].text)
            print(f"✅ Valid: {data['valid']}")
            print(f"   {data['message']}")
            print()
            
            # Demo 5: Validate import (wrong module - catches error)
            print("=" * 80)
            print("Demo 5: Validate Import - Wrong Module (Error Detection)")
            print("=" * 80)
            wrong_import = "from vtkmodules.vtkCommonDataModel import vtkPolyDataMapper"
            print(f"Code: {wrong_import}")
            result = await session.call_tool("vtk_validate_import", {
                "import_statement": wrong_import
            })
            data = json.loads(result.content[0].text)
            print(f"❌ Valid: {data['valid']}")
            print(f"   Error: {data['message']}")
            if 'suggested' in data:
                print(f"   💡 Correct: {data['suggested']}")
            print()
            
            # Demo 6: Get method info (valid method)
            print("=" * 80)
            print("Demo 6: Get Method Info - Valid Method")
            print("=" * 80)
            result = await session.call_tool("vtk_get_method_info", {
                "class_name": "vtkPolyDataMapper",
                "method_name": "SetInputData"
            })
            data = json.loads(result.content[0].text)
            if 'method_name' in data:
                print(f"✅ Method: {data['class_name']}.{data['method_name']}")
                print(f"   Exists: Yes")
            print()
            
            # Demo 7: Get method info (invalid method - catches hallucination)
            print("=" * 80)
            print("Demo 7: Get Method Info - Invalid Method (Hallucination)")
            print("=" * 80)
            print("Checking: vtkPolyDataMapper.SetAwesomeMode() (doesn't exist)")
            result = await session.call_tool("vtk_get_method_info", {
                "class_name": "vtkPolyDataMapper",
                "method_name": "SetAwesomeMode"
            })
            data = json.loads(result.content[0].text)
            print(f"❌ Error: {data['error']}")
            print(f"   Found: {data['found']}")
            print()
            
            # Demo 8: Get module classes
            print("=" * 80)
            print("Demo 8: Get Module Classes")
            print("=" * 80)
            result = await session.call_tool("vtk_get_module_classes", {
                "module": "vtkmodules.vtkRenderingCore"
            })
            data = json.loads(result.content[0].text)
            classes = data.get('classes', [])
            print(f"Module: vtkmodules.vtkRenderingCore")
            print(f"Classes: {len(classes)} classes")
            print(f"Sample: {', '.join(classes[:5])}")
            print()
            
            print("=" * 80)
            print("✅ MCP Integration Demo Complete")
            print("=" * 80)
            print("\nThis demonstrates the CORRECT way to use vtkapi-mcp:")
            print("  • As an MCP server (not direct Python imports)")
            print("  • Through MCP tools (not calling classes directly)")
            print("  • Proper error detection through MCP protocol")
            print("\nUse this pattern in vtk-rag to replace api-mcp module!")


if __name__ == "__main__":
    asyncio.run(demo_mcp_tools())
