"""VTK API Index - Fast in-memory index of VTK API documentation"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..utils.search import extract_description

logger = logging.getLogger(__name__)


class VTKAPIIndex:
    """Fast in-memory index of VTK API documentation"""
    
    def __init__(self, api_docs_path: Path):
        """
        Initialize the API index
        
        Args:
            api_docs_path: Path to vtk-python-docs.jsonl (raw, not chunked)
        """
        self.api_docs_path = api_docs_path
        self.classes: Dict[str, Dict[str, Any]] = {}
        self.modules: Dict[str, List[str]] = {}  # module -> [class names]
        self._load_api_docs()
    
    def _load_api_docs(self):
        """Load all API documentation from raw vtk-python-docs.jsonl"""
        logger.info(f"Loading VTK API docs from {self.api_docs_path}")
        
        if not self.api_docs_path.exists():
            logger.error(f"API docs not found at {self.api_docs_path}")
            return
        
        with open(self.api_docs_path) as f:
            for line in f:
                doc = json.loads(line)
                
                # Raw format: each line is a complete class documentation
                class_name = doc.get('class_name')
                
                if not class_name:
                    continue
                
                # Get content (full documentation with all methods)
                content = doc.get('content', '')
                module = doc.get('module_name', '')  # Raw format uses 'module_name' not 'module'
                
                # Store class info
                self.classes[class_name] = {
                    'class_name': class_name,
                    'module': module,
                    'content': content,
                    'metadata': doc
                }
                
                # Index by module
                if module:
                    if module not in self.modules:
                        self.modules[module] = []
                    self.modules[module].append(class_name)
        
        logger.info(f"Loaded {len(self.classes)} VTK classes from {len(self.modules)} modules")
    
    def get_class_info(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get complete information about a VTK class"""
        return self.classes.get(class_name)
    
    def search_classes(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for classes by name or keyword
        
        Returns list of {class_name, module, description}
        """
        query_lower = query.lower()
        results = []
        
        for class_name, info in self.classes.items():
            # Match by class name
            if query_lower in class_name.lower():
                content = info['content']
                # Extract first line of description
                description = extract_description(content)
                
                results.append({
                    'class_name': class_name,
                    'module': info['module'] or 'Unknown',
                    'description': description
                })
        
        return results[:limit]
    
    def get_module_classes(self, module: str) -> List[str]:
        """Get all classes in a module"""
        return self.modules.get(module, [])
    
    def get_method_info(self, class_name: str, method_name: str) -> Optional[Dict[str, str]]:
        """Get information about a specific method of a class"""
        info = self.get_class_info(class_name)
        if not info:
            return None
        
        # Check if structured_docs exists (raw format)
        metadata = info.get('metadata', {})
        structured_docs = metadata.get('structured_docs', {})
        
        if structured_docs:
            # Raw format: use structured_docs
            sections = structured_docs.get('sections', {})
            
            # Check all method sections
            for section_name, section_data in sections.items():
                if 'methods' in section_data:
                    methods = section_data['methods']
                    if method_name in methods:
                        return {
                            'class_name': class_name,
                            'method_name': method_name,
                            'content': methods[method_name],
                            'section': section_name
                        }
        
        # Fallback: search in content (for chunked format or if structured_docs missing)
        content = info.get('content', '')
        lines = content.split('\n')
        in_methods = False
        method_lines = []
        
        for line in lines:
            if '## |  Methods defined here:' in line:
                in_methods = True
                continue
            
            if in_methods:
                if line.startswith('###') and method_name not in line:
                    # Next method, stop
                    break
                method_lines.append(line)
        
        if method_lines:
            return {
                'class_name': class_name,
                'method_name': method_name,
                'content': '\n'.join(method_lines)
            }
        
        return None
