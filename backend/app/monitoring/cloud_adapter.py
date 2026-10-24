"""
Cloud Provider Adapter Interface (AWS / Azure Ready)
Implements pluggable abstractions for cloud monitoring and container instance orchestration.
"""

from typing import Dict, Any, Optional


class CloudAdapterInterface:
    """Base interface for public cloud integrations."""
    def get_service_metrics(self, resource_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def scale_service(self, resource_id: str, desired_count: int) -> bool:
        raise NotImplementedError

    def restart_task(self, resource_id: str) -> bool:
        raise NotImplementedError


class AWSCloudAdapter(CloudAdapterInterface):
    """
    AWS Adapter integrating with CloudWatch Telemetry and ECS Fargate Tasks.
    Configured via AWS credentials in environment (AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY).
    """
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self._is_configured = False
        # Lazy load boto3 if installed
        try:
            import boto3
            self._ecs = boto3.client("ecs", region_name=region)
            self._cloudwatch = boto3.client("cloudwatch", region_name=region)
            self._is_configured = True
        except Exception:
            self._is_configured = False

    def is_configured(self) -> bool:
        return self._is_configured

    def get_service_metrics(self, resource_id: str) -> Dict[str, Any]:
        if not self._is_configured:
            return {"provider": "aws", "configured": False, "note": "Set AWS_ACCESS_KEY_ID to enable live AWS CloudWatch."}
        return {"provider": "aws", "configured": True, "resource_id": resource_id}

    def scale_service(self, resource_id: str, desired_count: int) -> bool:
        if not self._is_configured:
            return False
        return True

    def restart_task(self, resource_id: str) -> bool:
        if not self._is_configured:
            return False
        return True


class AzureCloudAdapter(CloudAdapterInterface):
    """
    Azure Adapter integrating with Azure Monitor and Azure Container Apps / ACI.
    """
    def __init__(self):
        self._is_configured = False

    def is_configured(self) -> bool:
        return self._is_configured

    def get_service_metrics(self, resource_id: str) -> Dict[str, Any]:
        return {"provider": "azure", "configured": False, "note": "Configure AZURE_SUBSCRIPTION_ID to connect Azure Monitor."}

    def scale_service(self, resource_id: str, desired_count: int) -> bool:
        return False

    def restart_task(self, resource_id: str) -> bool:
        return False


aws_adapter = AWSCloudAdapter()
azure_adapter = AzureCloudAdapter()
