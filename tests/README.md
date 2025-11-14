# Test Suite Documentation

## Quick Reference

**Run tests:**
```bash
pytest                                              # All tests, no coverage
pytest --cov=vtkapi_mcp --cov-report=term -q        # With coverage summary
pytest --cov=vtkapi_mcp --cov-report=term-missing   # Shows uncovered lines
pytest tests/unit                                   # Unit tests only
pytest tests/integration                            # Integration tests only
```

## Overview

Clean, maintainable test suite for VTK API MCP. Test files mirror source code structure for easy navigation and maintenance.

## Test Organization

### Principle
**Test files mirror source code structure.** When you add code to `vtkapi_mcp/X/Y.py`, add tests to `tests/unit/test_X_Y.py`.

### Directory Structure

```
tests/
├── conftest.py                      # Test setup: reusable test data & objects (pytest convention)
├── README.md                        # This file - complete test documentation
├── unit/                            # Unit tests
│   ├── test_core_api_index.py           # vtkapi_mcp/core/api_index.py
│   ├── test_package_init.py             # vtkapi_mcp/__init__.py
│   ├── test_package_main.py             # vtkapi_mcp/__main__.py
│   ├── test_server_mcp.py               # vtkapi_mcp/server/mcp_server.py
│   ├── test_utils_extraction.py         # vtkapi_mcp/utils/extraction.py
│   ├── test_utils_search.py             # vtkapi_mcp/utils/search.py
│   └── test_validation.py               # vtkapi_mcp/validation/* (all validators)
└── integration/                     # Integration tests
    ├── test_end_to_end.py               # Complete workflows
    ├── test_async_server.py             # Async server integration (mocked)
    └── test_mcp_protocol.py             # Real MCP protocol tests (no mocks)
```

### Source-to-Test Mapping

| Source File | Test File | What It Tests |
|-------------|-----------|---------------|
| `vtkapi_mcp/__init__.py` | `test_package_init.py` | Package initialization, imports, exports |
| `vtkapi_mcp/__main__.py` | `test_package_main.py` | Entry point, CLI argument parsing |
| `vtkapi_mcp/core/api_index.py` | `test_core_api_index.py` | API indexing, search, class/method lookup |
| `vtkapi_mcp/server/mcp_server.py` | `test_server_mcp.py` | MCP server, tool handlers |
| `vtkapi_mcp/server/tools.py` | `test_server_mcp.py` | Tool definitions (tested with server) |
| `vtkapi_mcp/utils/extraction.py` | `test_utils_extraction.py` | Code parsing, AST extraction |
| `vtkapi_mcp/utils/search.py` | `test_utils_search.py` | Text search, description extraction |
| `vtkapi_mcp/validation/*.py` | `test_validation.py` | All validators (import, class, method) |

### Adding New Tests - The Right Way

**Example: Adding a new feature to import validation**

1. **Identify the source file:**
   ```
   vtkapi_mcp/validation/import_validator.py
   ```

2. **Open the corresponding test file:**
   ```
   tests/unit/test_validation.py
   ```

3. **Add your test to the existing test class:**
   ```python
   class TestImportValidator:
       def test_your_new_feature(self, api_index):
           """Test description"""
           # Your test code
   ```

4. **Run tests to verify:**
   ```bash
   pytest tests/unit/test_validation.py::TestImportValidator::test_your_new_feature -v
   ```

### File Naming Rules

**Test file naming:**
- Name files after the source module: `test_core_api_index.py`
- Use clear, descriptive class names: `TestImportValidator`
- Mirror the source structure

## Test Setup (`conftest.py`)

**What is conftest.py?** Pytest's standard file for shared test setup. It defines reusable test data and pre-configured objects so you don't repeat setup code in every test.

**Available test fixtures** (add them as function parameters to use):

| Fixture | What It Provides | Use When |
|---------|------------------|----------|
| `sample_api_data` | Sample VTK API docs (list) | Creating custom test scenarios |
| `temp_api_docs_file` | Temporary test data file (Path) | Testing file loading |
| `api_index` | Pre-loaded VTKAPIIndex | Testing API search/lookup |
| `validator` | Ready-to-use VTKCodeValidator | Testing code validation |
| `valid_vtk_code` | Example valid VTK code (str) | Testing success cases |
| `invalid_import_code` | Code with bad import (str) | Testing import errors |
| `invalid_class_code` | Code with fake class (str) | Testing class errors |
| `invalid_method_code` | Code with fake method (str) | Testing method errors |

## Running Tests

See **Quick Reference** at the top for all commands.

## What Each Test File Contains

### Unit Tests

**`test_core_api_index.py`**
- Loading API docs from JSONL
- Searching for classes
- Getting class and method information
- Module class listings
- Edge cases (missing files, empty queries)

**`test_package_init.py`**
- Package initialization
- Import availability
- Version information
- `__all__` exports

**`test_package_main.py`**
- Entry point execution
- Argument parsing
- Default argument handling
- Async main function

**`test_server_mcp.py`**
- MCP server initialization
- Tool handler methods
- Tool registration
- Response formatting
- All 5 MCP tools (get_class_info, search_classes, etc.)

**`test_utils_extraction.py`**
- Import statement extraction
- Class instantiation detection
- Variable type tracking
- Method call extraction with objects

**`test_utils_search.py`**
- Description extraction from content
- Module path extraction
- Fallback handling

**`test_validation.py`**
- Validation data models (ValidationError, ValidationResult)
- Import validator (monolithic, modular, from-imports)
- Class validator (existence, typo suggestions)
- Method validator (type tracking, fuzzy matching)
- Main validator (complete code validation)
- Edge cases for all validators

### Integration Tests

**`test_end_to_end.py`**
- Complete validation workflows
- Multi-error detection
- Search + validate patterns
- Realistic VTK rendering pipelines

**`test_async_server.py`**
- Server initialization (mocked)
- Async tool handlers (mocked)
- MCP framework integration tests

**`test_mcp_protocol.py`** ← Real MCP integration (no mocks)
- Server startup via MCP protocol
- All 5 MCP tools tested through real protocol
- Valid and invalid cases for each tool
- JSON response validation
- Error detection and handling

