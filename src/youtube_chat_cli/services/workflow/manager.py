"""
Workflow management system for n8n conversation workflows.
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""
    name: str
    url: str
    description: str
    created_at: datetime
    last_tested: Optional[datetime] = None
    status: WorkflowStatus = WorkflowStatus.UNKNOWN
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class WorkflowManager:
    """Manager for n8n conversation workflows."""
    
    def __init__(self):
        """Initialize the workflow manager."""
        self.config_dir = Path.home() / ".youtube-chat-cli" / "workflows"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "workflows.json"
        self.workflows: Dict[str, WorkflowConfig] = {}
        self.default_workflow: Optional[str] = None
        
        self._load_workflows()
    
    def _load_workflows(self):
        """Load workflow configurations from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    self.default_workflow = data.get('default_workflow')
                    
                    for name, workflow_data in data.get('workflows', {}).items():
                        # Convert datetime strings back to datetime objects
                        workflow_data['created_at'] = datetime.fromisoformat(workflow_data['created_at'])
                        if workflow_data.get('last_tested'):
                            workflow_data['last_tested'] = datetime.fromisoformat(workflow_data['last_tested'])
                        
                        # Convert status enum
                        workflow_data['status'] = WorkflowStatus(workflow_data['status'])
                        
                        self.workflows[name] = WorkflowConfig(**workflow_data)
                        
                logger.info(f"Loaded {len(self.workflows)} workflows")
                
            except Exception as e:
                logger.warning(f"Failed to load workflow configurations: {e}")
                self._create_default_workflow()
        else:
            self._create_default_workflow()
    
    def _create_default_workflow(self):
        """Create default workflow configuration."""
        default_url = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678/workflow/vTN9y2dLXqTiDfPT')
        
        default_workflow = WorkflowConfig(
            name="default",
            url=default_url,
            description="Default n8n RAG workflow",
            created_at=datetime.now(),
            status=WorkflowStatus.UNKNOWN
        )
        
        self.workflows["default"] = default_workflow
        self.default_workflow = "default"
        self._save_workflows()
        
        logger.info("Created default workflow configuration")
    
    def _save_workflows(self):
        """Save workflow configurations to file."""
        try:
            data = {
                'default_workflow': self.default_workflow,
                'workflows': {}
            }
            
            for name, workflow in self.workflows.items():
                workflow_dict = asdict(workflow)
                # Convert datetime objects to strings
                workflow_dict['created_at'] = workflow.created_at.isoformat()
                if workflow.last_tested:
                    workflow_dict['last_tested'] = workflow.last_tested.isoformat()
                else:
                    workflow_dict['last_tested'] = None
                
                # Convert status enum to string
                workflow_dict['status'] = workflow.status.value
                
                data['workflows'][name] = workflow_dict
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save workflow configurations: {e}")
    
    def add_workflow(self, name: str, url: str, description: str = "") -> bool:
        """Add a new workflow configuration."""
        if name in self.workflows:
            logger.warning(f"Workflow '{name}' already exists")
            return False
        
        workflow = WorkflowConfig(
            name=name,
            url=url,
            description=description,
            created_at=datetime.now(),
            status=WorkflowStatus.UNKNOWN
        )
        
        self.workflows[name] = workflow
        
        # Set as default if it's the first workflow
        if not self.default_workflow:
            self.default_workflow = name
        
        self._save_workflows()
        logger.info(f"Added workflow: {name}")
        return True
    
    def remove_workflow(self, name: str) -> bool:
        """Remove a workflow configuration."""
        if name not in self.workflows:
            logger.warning(f"Workflow '{name}' not found")
            return False
        
        del self.workflows[name]
        
        # Update default if necessary
        if self.default_workflow == name:
            self.default_workflow = next(iter(self.workflows.keys())) if self.workflows else None
        
        self._save_workflows()
        logger.info(f"Removed workflow: {name}")
        return True
    
    def set_default_workflow(self, name: str) -> bool:
        """Set the default workflow."""
        if name not in self.workflows:
            logger.warning(f"Workflow '{name}' not found")
            return False
        
        self.default_workflow = name
        self._save_workflows()
        logger.info(f"Set default workflow: {name}")
        return True
    
    def get_workflow(self, name: Optional[str] = None) -> Optional[WorkflowConfig]:
        """Get a workflow configuration."""
        if name is None:
            name = self.default_workflow
        
        if name is None:
            logger.warning("No default workflow set")
            return None
        
        return self.workflows.get(name)
    
    def list_workflows(self) -> List[WorkflowConfig]:
        """List all workflow configurations."""
        return list(self.workflows.values())
    
    def test_workflow(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Test a workflow connection."""
        workflow = self.get_workflow(name)
        if not workflow:
            return {
                "status": "error",
                "error": f"Workflow '{name}' not found"
            }
        
        logger.info(f"Testing workflow: {workflow.name}")
        
        try:
            # Send a test message
            test_payload = {
                "chatInput": "Test connection",
                "sessionId": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                workflow.url,
                json=test_payload,
                headers=headers,
                timeout=30
            )
            
            workflow.last_tested = datetime.now()
            
            if response.status_code == 200:
                workflow.status = WorkflowStatus.ACTIVE
                self._save_workflows()
                
                return {
                    "status": "success",
                    "workflow": workflow.name,
                    "response_time": response.elapsed.total_seconds(),
                    "response_size": len(response.content)
                }
            else:
                workflow.status = WorkflowStatus.ERROR
                self._save_workflows()
                
                return {
                    "status": "error",
                    "workflow": workflow.name,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
                
        except requests.RequestException as e:
            workflow.status = WorkflowStatus.ERROR
            self._save_workflows()
            
            return {
                "status": "error",
                "workflow": workflow.name,
                "error": f"Connection failed: {str(e)}"
            }
        except Exception as e:
            workflow.status = WorkflowStatus.ERROR
            self._save_workflows()
            
            return {
                "status": "error",
                "workflow": workflow.name,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def test_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Test all workflow connections."""
        results = {}
        
        for name in self.workflows.keys():
            results[name] = self.test_workflow(name)
        
        return results
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        total_workflows = len(self.workflows)
        active_workflows = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE)
        error_workflows = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.ERROR)
        untested_workflows = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.UNKNOWN)
        
        return {
            "total": total_workflows,
            "active": active_workflows,
            "error": error_workflows,
            "untested": untested_workflows,
            "default": self.default_workflow
        }
    
    def update_workflow(self, name: str, **kwargs) -> bool:
        """Update workflow configuration."""
        if name not in self.workflows:
            logger.warning(f"Workflow '{name}' not found")
            return False
        
        workflow = self.workflows[name]
        
        # Update allowed fields
        if 'url' in kwargs:
            workflow.url = kwargs['url']
            workflow.status = WorkflowStatus.UNKNOWN  # Reset status after URL change
        
        if 'description' in kwargs:
            workflow.description = kwargs['description']
        
        if 'metadata' in kwargs:
            workflow.metadata.update(kwargs['metadata'])
        
        self._save_workflows()
        logger.info(f"Updated workflow: {name}")
        return True
    
    def export_workflows(self, export_path: Optional[Path] = None) -> Path:
        """Export workflow configurations to a file."""
        if export_path is None:
            export_path = self.config_dir / f"workflows_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "default_workflow": self.default_workflow,
            "workflows": {}
        }
        
        for name, workflow in self.workflows.items():
            workflow_dict = asdict(workflow)
            workflow_dict['created_at'] = workflow.created_at.isoformat()
            if workflow.last_tested:
                workflow_dict['last_tested'] = workflow.last_tested.isoformat()
            workflow_dict['status'] = workflow.status.value
            
            export_data['workflows'][name] = workflow_dict
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported workflows to: {export_path}")
        return export_path
    
    def import_workflows(self, import_path: Path, overwrite: bool = False) -> Dict[str, Any]:
        """Import workflow configurations from a file."""
        if not import_path.exists():
            return {"status": "error", "error": "Import file not found"}
        
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for name, workflow_data in data.get('workflows', {}).items():
                if name in self.workflows and not overwrite:
                    skipped_count += 1
                    continue
                
                try:
                    # Convert datetime strings
                    workflow_data['created_at'] = datetime.fromisoformat(workflow_data['created_at'])
                    if workflow_data.get('last_tested'):
                        workflow_data['last_tested'] = datetime.fromisoformat(workflow_data['last_tested'])
                    
                    # Convert status enum
                    workflow_data['status'] = WorkflowStatus(workflow_data['status'])
                    
                    self.workflows[name] = WorkflowConfig(**workflow_data)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Failed to import workflow '{name}': {str(e)}")
            
            # Set default workflow if not set
            if not self.default_workflow and data.get('default_workflow') in self.workflows:
                self.default_workflow = data['default_workflow']
            
            self._save_workflows()
            
            return {
                "status": "success",
                "imported": imported_count,
                "skipped": skipped_count,
                "errors": errors
            }
            
        except Exception as e:
            return {"status": "error", "error": f"Failed to import workflows: {str(e)}"}


# Global workflow manager instance
_workflow_manager = None

def get_workflow_manager() -> WorkflowManager:
    """Get or create the global workflow manager instance."""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager
