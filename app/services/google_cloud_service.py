"""
Google Cloud Service for interacting with GCP APIs
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from google.cloud import compute_v1, storage, bigquery, iam_v1
from google.cloud import monitoring_v3, logging_v2
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleCloudService:
    """Google Cloud Service for managing GCP resources"""
    
    def __init__(self):
        self.project_id = settings.google_cloud_project_id
        self.credentials = None
        self.compute_client = None
        self.storage_client = None
        self.bigquery_client = None
        self.iam_client = None
        self.monitoring_client = None
        self.logging_client = None
        
        # Initialize clients
        self._initialize_clients()
    
    def is_healthy(self) -> bool:
        """Check if the Google Cloud service is healthy"""
        try:
            # Test basic connectivity
            return self.project_id is not None and self.credentials is not None
        except Exception as e:
            logger.error(f"Google Cloud Service health check failed: {e}")
            return False
    
    def _initialize_clients(self):
        """Initialize Google Cloud clients"""
        try:
            # Get credentials
            self.credentials, _ = default()
            
            # Initialize clients
            if self.project_id:
                self.compute_client = compute_v1.InstancesClient(credentials=self.credentials)
                self.storage_client = storage.Client(project=self.project_id, credentials=self.credentials)
                self.bigquery_client = bigquery.Client(project=self.project_id, credentials=self.credentials)
                self.iam_client = iam_v1.IAMClient(credentials=self.credentials)
                self.monitoring_client = monitoring_v3.MetricServiceClient(credentials=self.credentials)
                self.logging_client = logging_v2.LoggingServiceV2Client(credentials=self.credentials)
                
                logger.info(f"Initialized Google Cloud clients for project: {self.project_id}")
            else:
                logger.warning("No Google Cloud project ID configured")
                
        except DefaultCredentialsError:
            logger.error("Google Cloud credentials not found. Please run 'gcloud auth application-default login'")
        except Exception as e:
            logger.error(f"Error initializing Google Cloud clients: {e}")
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List Google Cloud projects"""
        try:
            # For MVP, return mock data
            # In production, use the Resource Manager API
            return [
                {
                    "project_id": self.project_id or "demo-project",
                    "name": "Demo Project",
                    "project_number": "123456789",
                    "state": "ACTIVE"
                }
            ]
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []
    
    async def list_instances(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Compute Engine instances"""
        try:
            if not self.compute_client:
                return []
            
            project = project_id or self.project_id
            if not project:
                return []
            
            # List instances across all zones
            instances = []
            
            # Get list of zones
            zones_client = compute_v1.ZonesClient(credentials=self.credentials)
            zones_request = compute_v1.ListZonesRequest(project=project)
            zones = zones_client.list(request=zones_request)
            
            for zone in zones:
                try:
                    request = compute_v1.ListInstancesRequest(
                        project=project,
                        zone=zone.name
                    )
                    zone_instances = self.compute_client.list(request=request)
                    
                    for instance in zone_instances:
                        instances.append({
                            "id": instance.id,
                            "name": instance.name,
                            "zone": zone.name,
                            "machine_type": instance.machine_type.split('/')[-1],
                            "status": instance.status,
                            "creation_timestamp": instance.creation_timestamp,
                            "network_interfaces": [
                                {
                                    "network": ni.network.split('/')[-1],
                                    "subnetwork": ni.subnetwork.split('/')[-1] if ni.subnetwork else None,
                                    "internal_ip": ni.network_i_p,
                                    "external_ip": ni.access_configs[0].nat_i_p if ni.access_configs else None
                                }
                                for ni in instance.network_interfaces
                            ],
                            "disks": [
                                {
                                    "name": disk.device_name,
                                    "size_gb": disk.disk_size_gb,
                                    "type": disk.type_.split('/')[-1]
                                }
                                for disk in instance.disks
                            ]
                        })
                except Exception as e:
                    logger.warning(f"Error listing instances in zone {zone.name}: {e}")
                    continue
            
            return instances
            
        except Exception as e:
            logger.error(f"Error listing instances: {e}")
            return []
    
    async def create_instance(
        self, 
        name: str, 
        zone: str, 
        machine_type: str = "e2-micro",
        image_family: str = "debian-11",
        image_project: str = "debian-cloud",
        disk_size_gb: int = 10
    ) -> Dict[str, Any]:
        """Create a Compute Engine instance"""
        try:
            if not self.compute_client:
                raise ValueError("Compute client not initialized")
            
            project = self.project_id
            if not project:
                raise ValueError("No project ID configured")
            
            # Get the latest image
            images_client = compute_v1.ImagesClient(credentials=self.credentials)
            image_response = images_client.get_from_family(
                project=image_project,
                family=image_family
            )
            
            # Create disk configuration
            disk = compute_v1.AttachedDisk(
                auto_delete=True,
                boot=True,
                size_gb=disk_size_gb,
                source_image=image_response.self_link,
                type_=compute_v1.AttachedDisk.Type.PERSISTENT
            )
            
            # Create network interface
            network_interface = compute_v1.NetworkInterface(
                name="global/networks/default",
                access_configs=[
                    compute_v1.AccessConfig(
                        name="External NAT",
                        type_=compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT
                    )
                ]
            )
            
            # Create instance
            instance = compute_v1.Instance(
                name=name,
                disks=[disk],
                machine_type=f"zones/{zone}/machineTypes/{machine_type}",
                network_interfaces=[network_interface]
            )
            
            # Insert instance
            request = compute_v1.InsertInstanceRequest(
                project=project,
                zone=zone,
                instance_resource=instance
            )
            
            operation = self.compute_client.insert(request=request)
            
            # Wait for operation to complete
            await self._wait_for_operation(operation, project, zone)
            
            return {
                "name": name,
                "zone": zone,
                "status": "RUNNING",
                "message": "Instance created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating instance: {e}")
            raise
    
    async def delete_instance(self, name: str, zone: str) -> Dict[str, Any]:
        """Delete a Compute Engine instance"""
        try:
            if not self.compute_client:
                raise ValueError("Compute client not initialized")
            
            project = self.project_id
            if not project:
                raise ValueError("No project ID configured")
            
            request = compute_v1.DeleteInstanceRequest(
                project=project,
                zone=zone,
                instance=name
            )
            
            operation = self.compute_client.delete(request=request)
            
            # Wait for operation to complete
            await self._wait_for_operation(operation, project, zone)
            
            return {
                "name": name,
                "zone": zone,
                "status": "DELETED",
                "message": "Instance deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting instance: {e}")
            raise
    
    async def start_instance(self, name: str, zone: str) -> Dict[str, Any]:
        """Start a Compute Engine instance"""
        try:
            if not self.compute_client:
                raise ValueError("Compute client not initialized")
            
            project = self.project_id
            if not project:
                raise ValueError("No project ID configured")
            
            request = compute_v1.StartInstanceRequest(
                project=project,
                zone=zone,
                instance=name
            )
            
            operation = self.compute_client.start(request=request)
            
            # Wait for operation to complete
            await self._wait_for_operation(operation, project, zone)
            
            return {
                "name": name,
                "zone": zone,
                "status": "RUNNING",
                "message": "Instance started successfully"
            }
            
        except Exception as e:
            logger.error(f"Error starting instance: {e}")
            raise
    
    async def stop_instance(self, name: str, zone: str) -> Dict[str, Any]:
        """Stop a Compute Engine instance"""
        try:
            if not self.compute_client:
                raise ValueError("Compute client not initialized")
            
            project = self.project_id
            if not project:
                raise ValueError("No project ID configured")
            
            request = compute_v1.StopInstanceRequest(
                project=project,
                zone=zone,
                instance=name
            )
            
            operation = self.compute_client.stop(request=request)
            
            # Wait for operation to complete
            await self._wait_for_operation(operation, project, zone)
            
            return {
                "name": name,
                "zone": zone,
                "status": "TERMINATED",
                "message": "Instance stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"Error stopping instance: {e}")
            raise
    
    async def list_storage_buckets(self) -> List[Dict[str, Any]]:
        """List Cloud Storage buckets"""
        try:
            if not self.storage_client:
                return []
            
            buckets = []
            for bucket in self.storage_client.list_buckets():
                buckets.append({
                    "name": bucket.name,
                    "location": bucket.location,
                    "storage_class": bucket.storage_class,
                    "created": bucket.time_created,
                    "updated": bucket.updated,
                    "labels": dict(bucket.labels) if bucket.labels else {}
                })
            
            return buckets
            
        except Exception as e:
            logger.error(f"Error listing storage buckets: {e}")
            return []
    
    async def create_storage_bucket(
        self, 
        name: str, 
        location: str = "US",
        storage_class: str = "STANDARD"
    ) -> Dict[str, Any]:
        """Create a Cloud Storage bucket"""
        try:
            if not self.storage_client:
                raise ValueError("Storage client not initialized")
            
            bucket = self.storage_client.bucket(name)
            bucket.location = location
            bucket.storage_class = storage_class
            
            bucket.create()
            
            return {
                "name": name,
                "location": location,
                "storage_class": storage_class,
                "status": "created",
                "message": "Bucket created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating storage bucket: {e}")
            raise
    
    async def delete_storage_bucket(self, name: str) -> Dict[str, Any]:
        """Delete a Cloud Storage bucket"""
        try:
            if not self.storage_client:
                raise ValueError("Storage client not initialized")
            
            bucket = self.storage_client.bucket(name)
            bucket.delete(force=True)
            
            return {
                "name": name,
                "status": "deleted",
                "message": "Bucket deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting storage bucket: {e}")
            raise
    
    async def list_bigquery_datasets(self) -> List[Dict[str, Any]]:
        """List BigQuery datasets"""
        try:
            if not self.bigquery_client:
                return []
            
            datasets = []
            for dataset in self.bigquery_client.list_datasets():
                datasets.append({
                    "dataset_id": dataset.dataset_id,
                    "friendly_name": dataset.friendly_name,
                    "description": dataset.description,
                    "created": dataset.created,
                    "modified": dataset.modified,
                    "labels": dict(dataset.labels) if dataset.labels else {}
                })
            
            return datasets
            
        except Exception as e:
            logger.error(f"Error listing BigQuery datasets: {e}")
            return []
    
    async def create_bigquery_dataset(
        self, 
        dataset_id: str, 
        friendly_name: str = "",
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a BigQuery dataset"""
        try:
            if not self.bigquery_client:
                raise ValueError("BigQuery client not initialized")
            
            dataset_ref = self.bigquery_client.dataset(dataset_id)
            dataset = bigquery.Dataset(dataset_ref)
            dataset.friendly_name = friendly_name
            dataset.description = description
            
            dataset = self.bigquery_client.create_dataset(dataset)
            
            return {
                "dataset_id": dataset.dataset_id,
                "friendly_name": dataset.friendly_name,
                "description": dataset.description,
                "status": "created",
                "message": "Dataset created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating BigQuery dataset: {e}")
            raise
    
    async def get_iam_policies(self) -> List[Dict[str, Any]]:
        """Get IAM policies for the project"""
        try:
            if not self.iam_client:
                return []
            
            project = self.project_id
            if not project:
                return []
            
            # Get project IAM policy
            request = iam_v1.GetIamPolicyRequest(
                resource=f"projects/{project}"
            )
            
            policy = self.iam_client.get_iam_policy(request=request)
            
            bindings = []
            for binding in policy.bindings:
                bindings.append({
                    "role": binding.role,
                    "members": list(binding.members)
                })
            
            return bindings
            
        except Exception as e:
            logger.error(f"Error getting IAM policies: {e}")
            return []
    
    async def get_monitoring_metrics(self, metric_type: str = "compute.googleapis.com/instance/cpu/utilization") -> List[Dict[str, Any]]:
        """Get monitoring metrics"""
        try:
            if not self.monitoring_client:
                return []
            
            project = self.project_id
            if not project:
                return []
            
            # Get time series data
            request = monitoring_v3.ListTimeSeriesRequest(
                name=f"projects/{project}",
                filter=f'metric.type = "{metric_type}"',
                interval=monitoring_v3.TimeInterval({
                    "end_time": {"seconds": int(asyncio.get_event_loop().time())},
                    "start_time": {"seconds": int(asyncio.get_event_loop().time()) - 3600}  # Last hour
                })
            )
            
            time_series = self.monitoring_client.list_time_series(request=request)
            
            metrics = []
            for series in time_series:
                metrics.append({
                    "metric_type": series.metric.type,
                    "resource_type": series.resource.type,
                    "resource_labels": dict(series.resource.labels),
                    "metric_labels": dict(series.metric.labels),
                    "points": [
                        {
                            "value": point.value.double_value or point.value.int64_value,
                            "timestamp": point.interval.end_time.ToDatetime()
                        }
                        for point in series.points
                    ]
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting monitoring metrics: {e}")
            return []
    
    async def _wait_for_operation(self, operation, project: str, zone: str = None):
        """Wait for a compute operation to complete"""
        try:
            while operation.status != "DONE":
                await asyncio.sleep(1)
                
                if zone:
                    request = compute_v1.GetZoneOperationRequest(
                        project=project,
                        zone=zone,
                        operation=operation.name
                    )
                    operation = self.compute_client.get(request=request)
                else:
                    # For global operations
                    request = compute_v1.GetGlobalOperationRequest(
                        project=project,
                        operation=operation.name
                    )
                    operation = self.compute_client.get(request=request)
            
            if operation.error:
                raise Exception(f"Operation failed: {operation.error}")
                
        except Exception as e:
            logger.error(f"Error waiting for operation: {e}")
            raise
    
    async def get_resource_usage(self) -> Dict[str, Any]:
        """Get overall resource usage for the project"""
        try:
            usage = {
                "compute": {
                    "instances": len(await self.list_instances()),
                    "running_instances": 0,
                    "stopped_instances": 0
                },
                "storage": {
                    "buckets": len(await self.list_storage_buckets()),
                    "total_objects": 0,
                    "total_size_gb": 0
                },
                "database": {
                    "datasets": len(await self.list_bigquery_datasets()),
                    "tables": 0
                }
            }
            
            # Count running/stopped instances
            instances = await self.list_instances()
            for instance in instances:
                if instance["status"] == "RUNNING":
                    usage["compute"]["running_instances"] += 1
                elif instance["status"] == "TERMINATED":
                    usage["compute"]["stopped_instances"] += 1
            
            return usage
            
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {}
    
    async def estimate_costs(self) -> Dict[str, Any]:
        """Estimate costs for the project (mock implementation)"""
        try:
            instances = await self.list_instances()
            buckets = await self.list_storage_buckets()
            datasets = await self.list_bigquery_datasets()
            
            # Simple cost estimation (mock)
            compute_cost = len(instances) * 50  # $50 per instance per month
            storage_cost = len(buckets) * 5     # $5 per bucket per month
            bigquery_cost = len(datasets) * 10  # $10 per dataset per month
            
            total_cost = compute_cost + storage_cost + bigquery_cost
            
            return {
                "total_monthly_cost": total_cost,
                "breakdown": {
                    "compute": compute_cost,
                    "storage": storage_cost,
                    "bigquery": bigquery_cost
                },
                "currency": "USD",
                "period": "monthly"
            }
            
        except Exception as e:
            logger.error(f"Error estimating costs: {e}")
            return {} 