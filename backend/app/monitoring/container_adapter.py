"""
Container & Service Adapter Layer
Provides an abstract interface with implementations for:
1. Local Process & Simulated Container Adapter (Default for portable environments)
2. Real Docker Engine Adapter (Uses docker-py when Docker daemon socket is available)
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class BaseContainerAdapter:
    def get_container_status(self, container_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def restart_container(self, container_id: str) -> bool:
        raise NotImplementedError

    def stop_container(self, container_id: str) -> bool:
        raise NotImplementedError

    def start_container(self, container_id: str) -> bool:
        raise NotImplementedError


class LocalContainerAdapter(BaseContainerAdapter):
    """
    Local robust adapter managing in-memory and simulated container state.
    Allows full testing and production simulation without requiring root Docker socket privileges.
    """
    def __init__(self):
        self._states: Dict[str, Dict[str, Any]] = {}

    def register_container(self, container_id: str, name: str):
        if container_id not in self._states:
            self._states[container_id] = {
                "name": name,
                "status": "running",
                "restarts": 0,
                "last_started": datetime.now(timezone.utc)
            }

    def get_container_status(self, container_id: str) -> Dict[str, Any]:
        state = self._states.get(container_id)
        if not state:
            return {"container_id": container_id, "status": "running", "restarts": 0}
        return {
            "container_id": container_id,
            "status": state["status"],
            "restarts": state["restarts"],
            "last_started": state["last_started"].isoformat()
        }

    def restart_container(self, container_id: str) -> bool:
        state = self._states.setdefault(container_id, {"status": "running", "restarts": 0, "last_started": datetime.now(timezone.utc)})
        state["status"] = "running"
        state["restarts"] += 1
        state["last_started"] = datetime.now(timezone.utc)
        return True

    def stop_container(self, container_id: str) -> bool:
        state = self._states.setdefault(container_id, {"status": "running", "restarts": 0, "last_started": datetime.now(timezone.utc)})
        state["status"] = "stopped"
        return True

    def start_container(self, container_id: str) -> bool:
        state = self._states.setdefault(container_id, {"status": "stopped", "restarts": 0, "last_started": datetime.now(timezone.utc)})
        state["status"] = "running"
        state["last_started"] = datetime.now(timezone.utc)
        return True


class DockerEngineAdapter(BaseContainerAdapter):
    """Real Docker Engine Adapter using docker-py socket."""
    def __init__(self):
        self._client = None
        try:
            import docker
            self._client = docker.from_env()
        except Exception as e:
            self._client = None

    def is_available(self) -> bool:
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            return False

    def get_container_status(self, container_id: str) -> Dict[str, Any]:
        if not self.is_available():
            return {"container_id": container_id, "status": "unknown"}
        try:
            c = self._client.containers.get(container_id)
            return {"container_id": container_id, "status": c.status}
        except Exception as e:
            return {"container_id": container_id, "status": "error", "error": str(e)}

    def restart_container(self, container_id: str) -> bool:
        if not self.is_available():
            return False
        try:
            c = self._client.containers.get(container_id)
            c.restart(timeout=10)
            return True
        except Exception:
            return False

    def stop_container(self, container_id: str) -> bool:
        if not self.is_available():
            return False
        try:
            c = self._client.containers.get(container_id)
            c.stop(timeout=10)
            return True
        except Exception:
            return False

    def start_container(self, container_id: str) -> bool:
        if not self.is_available():
            return False
        try:
            c = self._client.containers.get(container_id)
            c.start()
            return True
        except Exception:
            return False


# Factory provider
def get_container_adapter() -> BaseContainerAdapter:
    docker_adapter = DockerEngineAdapter()
    if docker_adapter.is_available():
        return docker_adapter
    return LocalContainerAdapter()


container_adapter = get_container_adapter()
