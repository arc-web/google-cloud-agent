"""
Gemini Service for enhanced Google Cloud management capabilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
import subprocess
import json
import os
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini Service for enhanced Google Cloud management"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY") or settings.google_api_key
        self.model_name = "gemini-pro"
        self.llm = None
        self.is_initialized = False
        
        # Initialize Gemini
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini API"""
        try:
            if not self.api_key:
                logger.warning("Google API key not found. Gemini features will be limited.")
                return
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize LangChain integration
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.1,
                max_output_tokens=2048
            )
            
            self.is_initialized = True
            logger.info("Gemini service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.is_initialized = False
    
    async def analyze_cloud_architecture(self, project_id: str) -> Dict[str, Any]:
        """Analyze Google Cloud architecture using Gemini"""
        try:
            if not self.is_initialized:
                return {"error": "Gemini not initialized"}
            
            # Get current cloud resources
            resources = await self._get_cloud_resources(project_id)
            
            # Create analysis prompt
            prompt = f"""
            Analyze the following Google Cloud architecture and provide recommendations:
            
            Project ID: {project_id}
            Resources: {json.dumps(resources, indent=2)}
            
            Please provide:
            1. Architecture overview
            2. Security assessment
            3. Cost optimization opportunities
            4. Performance recommendations
            5. Best practices suggestions
            6. Potential improvements
            
            Format the response as JSON with the following structure:
            {{
                "architecture_overview": "description",
                "security_assessment": {{
                    "score": 0-100,
                    "issues": ["list of issues"],
                    "recommendations": ["list of recommendations"]
                }},
                "cost_optimization": {{
                    "estimated_savings": "amount",
                    "opportunities": ["list of opportunities"]
                }},
                "performance_recommendations": ["list of recommendations"],
                "best_practices": ["list of practices"],
                "improvements": ["list of improvements"]
            }}
            """
            
            # Get Gemini response
            response = await self._get_gemini_response(prompt)
            
            # Parse response
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                # Fallback to text parsing
                return {"analysis": response, "format": "text"}
                
        except Exception as e:
            logger.error(f"Error analyzing cloud architecture: {e}")
            return {"error": str(e)}
    
    async def generate_terraform_config(self, requirements: str) -> Dict[str, Any]:
        """Generate Terraform configuration using Gemini"""
        try:
            if not self.is_initialized:
                return {"error": "Gemini not initialized"}
            
            prompt = f"""
            Generate Terraform configuration for the following Google Cloud requirements:
            
            Requirements: {requirements}
            
            Please provide:
            1. Complete Terraform configuration files
            2. Variables file
            3. Outputs file
            4. README with usage instructions
            
            Format the response as JSON with the following structure:
            {{
                "main.tf": "terraform configuration",
                "variables.tf": "variables definition",
                "outputs.tf": "outputs definition",
                "README.md": "usage instructions",
                "terraform.tfvars.example": "example variables"
            }}
            
            Ensure the configuration follows Google Cloud best practices and includes proper security configurations.
            """
            
            response = await self._get_gemini_response(prompt)
            
            try:
                config = json.loads(response)
                return config
            except json.JSONDecodeError:
                return {"terraform_config": response, "format": "text"}
                
        except Exception as e:
            logger.error(f"Error generating Terraform config: {e}")
            return {"error": str(e)}
    
    async def optimize_cloud_costs(self, current_costs: Dict[str, Any]) -> Dict[str, Any]:
        """Get cost optimization recommendations from Gemini"""
        try:
            if not self.is_initialized:
                return {"error": "Gemini not initialized"}
            
            prompt = f"""
            Analyze the following Google Cloud costs and provide optimization recommendations:
            
            Current Costs: {json.dumps(current_costs, indent=2)}
            
            Please provide:
            1. Detailed cost analysis
            2. Specific optimization recommendations
            3. Estimated savings for each recommendation
            4. Implementation steps
            5. Risk assessment for each change
            
            Format the response as JSON with the following structure:
            {{
                "cost_analysis": "detailed analysis",
                "recommendations": [
                    {{
                        "title": "recommendation title",
                        "description": "detailed description",
                        "estimated_savings": "monthly savings",
                        "implementation_steps": ["step1", "step2"],
                        "risk_level": "low/medium/high",
                        "effort": "low/medium/high"
                    }}
                ],
                "total_potential_savings": "total amount",
                "priority_order": ["recommendation1", "recommendation2"]
            }}
            """
            
            response = await self._get_gemini_response(prompt)
            
            try:
                optimization = json.loads(response)
                return optimization
            except json.JSONDecodeError:
                return {"optimization_plan": response, "format": "text"}
                
        except Exception as e:
            logger.error(f"Error optimizing cloud costs: {e}")
            return {"error": str(e)}
    
    async def generate_security_policy(self, requirements: str) -> Dict[str, Any]:
        """Generate security policies using Gemini"""
        try:
            if not self.is_initialized:
                return {"error": "Gemini not initialized"}
            
            prompt = f"""
            Generate comprehensive security policies for Google Cloud based on these requirements:
            
            Requirements: {requirements}
            
            Please provide:
            1. IAM policies
            2. Network security rules
            3. Data protection policies
            4. Compliance configurations
            5. Monitoring and alerting setup
            
            Format the response as JSON with the following structure:
            {{
                "iam_policies": {{
                    "roles": ["list of roles"],
                    "bindings": ["list of bindings"],
                    "service_accounts": ["list of service accounts"]
                }},
                "network_security": {{
                    "firewall_rules": ["list of rules"],
                    "vpc_config": "vpc configuration",
                    "subnet_config": "subnet configuration"
                }},
                "data_protection": {{
                    "encryption": "encryption settings",
                    "backup_policies": "backup configuration",
                    "retention_policies": "retention settings"
                }},
                "compliance": {{
                    "audit_logging": "audit configuration",
                    "monitoring": "monitoring setup",
                    "alerts": "alert configuration"
                }}
            }}
            """
            
            response = await self._get_gemini_response(prompt)
            
            try:
                policies = json.loads(response)
                return policies
            except json.JSONDecodeError:
                return {"security_policies": response, "format": "text"}
                
        except Exception as e:
            logger.error(f"Error generating security policies: {e}")
            return {"error": str(e)}
    
    async def code_review_and_suggestions(self, code: str, context: str = "") -> Dict[str, Any]:
        """Review code and provide suggestions using Gemini"""
        try:
            if not self.is_initialized:
                return {"error": "Gemini not initialized"}
            
            prompt = f"""
            Review the following code and provide suggestions for improvement:
            
            Context: {context}
            
            Code:
            {code}
            
            Please provide:
            1. Code quality assessment
            2. Security review
            3. Performance optimizations
            4. Best practices suggestions
            5. Specific improvements with code examples
            
            Format the response as JSON with the following structure:
            {{
                "quality_assessment": {{
                    "score": 0-100,
                    "issues": ["list of issues"],
                    "strengths": ["list of strengths"]
                }},
                "security_review": {{
                    "vulnerabilities": ["list of vulnerabilities"],
                    "recommendations": ["security recommendations"]
                }},
                "performance_optimizations": ["list of optimizations"],
                "best_practices": ["list of practices"],
                "improvements": [
                    {{
                        "type": "improvement type",
                        "description": "description",
                        "code_example": "improved code"
                    }}
                ]
            }}
            """
            
            response = await self._get_gemini_response(prompt)
            
            try:
                review = json.loads(response)
                return review
            except json.JSONDecodeError:
                return {"code_review": response, "format": "text"}
                
        except Exception as e:
            logger.error(f"Error reviewing code: {e}")
            return {"error": str(e)}
    
    async def generate_documentation(self, code_or_config: str, doc_type: str = "README") -> Dict[str, Any]:
        """Generate documentation using Gemini"""
        try:
            if not self.is_initialized:
                return {"error": "Gemini not initialized"}
            
            prompt = f"""
            Generate {doc_type} documentation for the following:
            
            Content:
            {code_or_config}
            
            Please provide comprehensive documentation including:
            1. Overview and purpose
            2. Installation and setup instructions
            3. Usage examples
            4. Configuration options
            5. Troubleshooting guide
            6. API reference (if applicable)
            
            Format the response as JSON with the following structure:
            {{
                "overview": "overview section",
                "installation": "installation instructions",
                "usage": "usage examples",
                "configuration": "configuration options",
                "troubleshooting": "troubleshooting guide",
                "api_reference": "api documentation",
                "full_documentation": "complete markdown document"
            }}
            """
            
            response = await self._get_gemini_response(prompt)
            
            try:
                documentation = json.loads(response)
                return documentation
            except json.JSONDecodeError:
                return {"documentation": response, "format": "text"}
                
        except Exception as e:
            logger.error(f"Error generating documentation: {e}")
            return {"error": str(e)}
    
    async def _get_gemini_response(self, prompt: str) -> str:
        """Get response from Gemini"""
        try:
            if not self.llm:
                return "Gemini not available"
            
            # Use LangChain for async compatibility
            messages = [
                SystemMessage(content="You are a Google Cloud expert assistant. Provide detailed, accurate, and practical advice."),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
            
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            return f"Error: {str(e)}"
    
    async def _get_cloud_resources(self, project_id: str) -> Dict[str, Any]:
        """Get current cloud resources for analysis"""
        try:
            # This would integrate with your existing GoogleCloudService
            # For now, return mock data
            return {
                "project_id": project_id,
                "compute_instances": [],
                "storage_buckets": [],
                "databases": [],
                "networks": [],
                "iam_policies": []
            }
        except Exception as e:
            logger.error(f"Error getting cloud resources: {e}")
            return {}
    
    def is_healthy(self) -> bool:
        """Check if Gemini service is healthy"""
        return self.is_initialized and self.api_key is not None 