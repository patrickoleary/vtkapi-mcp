"""Pytest configuration and shared fixtures"""

import pytest
import json
import tempfile
from pathlib import Path
from vtkapi_mcp.core import VTKAPIIndex
from vtkapi_mcp.validation import VTKCodeValidator


@pytest.fixture
def sample_api_data():
    """Sample VTK API documentation data"""
    return [
        {
            "class_name": "vtkPolyDataMapper",
            "module_name": "vtkmodules.vtkRenderingCore",
            "content": "**Module:** `vtkmodules.vtkRenderingCore`\n\nvtkPolyDataMapper maps polygonal data to graphics primitives.",
            "structured_docs": {
                "sections": {
                    "Methods defined here": {
                        "methods": {
                            "SetInputData": "SetInputData(self, input) -> None\n\nSet the input data object.",
                            "SetInputConnection": "SetInputConnection(self, port) -> None\n\nSet input connection.",
                            "Update": "Update(self) -> None\n\nUpdate the mapper."
                        }
                    }
                }
            }
        },
        {
            "class_name": "vtkActor",
            "module_name": "vtkmodules.vtkRenderingCore",
            "content": "**Module:** `vtkmodules.vtkRenderingCore`\n\nvtkActor represents an entity in a rendering scene.",
            "structured_docs": {
                "sections": {
                    "Methods defined here": {
                        "methods": {
                            "SetMapper": "SetMapper(self, mapper) -> None\n\nSet the mapper.",
                            "GetMapper": "GetMapper(self) -> vtkMapper\n\nGet the mapper.",
                            "SetPosition": "SetPosition(self, x, y, z) -> None\n\nSet position."
                        }
                    }
                }
            }
        },
        {
            "class_name": "vtkSTLReader",
            "module_name": "vtkmodules.vtkIOGeometry",
            "content": "**Module:** `vtkmodules.vtkIOGeometry`\n\nvtkSTLReader reads STL files.",
            "structured_docs": {
                "sections": {
                    "Methods defined here": {
                        "methods": {
                            "SetFileName": "SetFileName(self, filename) -> None\n\nSet the file name.",
                            "GetFileName": "GetFileName(self) -> str\n\nGet the file name.",
                            "Update": "Update(self) -> None\n\nUpdate the reader.",
                            "GetOutputPort": "GetOutputPort(self) -> vtkAlgorithmOutput\n\nGet output port."
                        }
                    }
                }
            }
        }
    ]


@pytest.fixture
def temp_api_docs_file(sample_api_data):
    """Create a temporary API docs JSONL file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in sample_api_data:
            f.write(json.dumps(item) + '\n')
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    temp_path.unlink()


@pytest.fixture
def api_index(temp_api_docs_file):
    """Create a VTKAPIIndex instance with test data"""
    return VTKAPIIndex(temp_api_docs_file)


@pytest.fixture
def validator(api_index):
    """Create a VTKCodeValidator instance"""
    return VTKCodeValidator(api_index)


@pytest.fixture
def valid_vtk_code():
    """Sample valid VTK code"""
    return """
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor

reader = vtkSTLReader()
reader.SetFileName('model.stl')
reader.Update()

mapper = vtkPolyDataMapper()
mapper.SetInputConnection(reader.GetOutputPort())

actor = vtkActor()
actor.SetMapper(mapper)
"""


@pytest.fixture
def invalid_import_code():
    """Sample code with invalid import"""
    return """
from vtkmodules.vtkCommonDataModel import vtkPolyDataMapper

mapper = vtkPolyDataMapper()
"""


@pytest.fixture
def invalid_class_code():
    """Sample code with non-existent class"""
    return """
from vtkmodules.vtkIOGeometry import vtkFakeReader

reader = vtkFakeReader()
"""


@pytest.fixture
def invalid_method_code():
    """Sample code with non-existent method"""
    return """
from vtkmodules.vtkRenderingCore import vtkActor

actor = vtkActor()
actor.FakeMethod()
"""
