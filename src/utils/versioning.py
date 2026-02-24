import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class ModelRegistry:
    """
    Simple file-based model registry for versioning.
    """
    
    def __init__(self, registry_path: Path = Path("models/registry.json")):
        self.registry_path = registry_path
        self._load()
        
    def _load(self):
        if self.registry_path.exists():
            with open(self.registry_path, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {"models": [], "current_version": "0.0.0"}
            
    def register_model(self, version: str, path: str, metadata: Dict[str, Any]):
        """Register a new model version."""
        entry = {
            "version": version,
            "path": str(path),
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
        self.registry["models"].append(entry)
        self.registry["current_version"] = version
        self._save()
        
    def get_current_model(self) -> Dict[str, Any]:
        """Get the latest registered model."""
        return self.registry["models"][-1] if self.registry["models"] else {}
        
    def _save(self):
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=2)

if __name__ == "__main__":
    reg = ModelRegistry()
    reg.register_model("1.0.0", "models/trained/model_v1.pkl", {"accuracy": 0.85})
