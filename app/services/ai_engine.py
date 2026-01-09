"""
AI Engine for natural language processing and command interpretation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import json
import re
from datetime import datetime

# Import Gemini instead of OpenAI
from app.services.gemini_service import GeminiService
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIEngine:
    """AI Engine for processing natural language commands"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.is_healthy = True
    
    async def process_command(self, command: str, context: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process natural language command and convert to executable workflow
        """
        try:
            # Build the prompt for Gemini
            prompt = self._build_command_prompt(command, context, user_id)
            
            # Get response from Gemini
            response = await self.gemini_service._get_gemini_response(prompt)
            
            # Parse the response
            result = self._parse_ai_response(response, command)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return {
                "interpreted_command": f"Error: {str(e)}",
                "confidence": 0.0,
                "suggested_actions": [],
                "estimated_impact": "Unknown",
                "requires_approval": True,
                "error": str(e)
            }
    
    def _build_command_prompt(self, command: str, context: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> str:
        """Build prompt for command interpretation"""
        
        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context, indent=2)}"
        
        prompt = f"""
        You are an expert Google Cloud manager. Analyze the following user command and provide a structured response.
        
        User Command: {command}
        User ID: {user_id or 'unknown'}{context_str}
        
        Please provide a JSON response with the following structure:
        {{
            "interpreted_command": "Clear description of what the command does",
            "confidence": 0.85,
            "suggested_actions": [
                "Action 1 description",
                "Action 2 description",
                "Action 3 description"
            ],
            "estimated_impact": "Low/Medium/High - brief description of impact",
            "requires_approval": true/false,
            "estimated_cost": "$X/month or 'minimal'",
            "estimated_time": "X minutes/hours",
            "security_notes": "Any security considerations",
            "best_practices": ["Best practice 1", "Best practice 2"],
            "workflow_steps": [
                {{
                    "step": 1,
                    "action": "Action description",
                    "service": "Google Cloud service name",
                    "estimated_duration": "X minutes"
                }}
            ]
        }}
        
        Focus on Google Cloud services and best practices. Be specific about the actions needed.
        """
        
        return prompt
    
    def _parse_ai_response(self, response: str, original_command: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                # Fallback parsing
                parsed = self._fallback_parsing(response)
            
            # Ensure all required fields are present
            result = {
                "interpreted_command": parsed.get("interpreted_command", f"Execute: {original_command}"),
                "confidence": parsed.get("confidence", 0.7),
                "suggested_actions": parsed.get("suggested_actions", ["Process command"]),
                "estimated_impact": parsed.get("estimated_impact", "Medium"),
                "requires_approval": parsed.get("requires_approval", True),
                "estimated_cost": parsed.get("estimated_cost", "Unknown"),
                "estimated_time": parsed.get("estimated_time", "Unknown"),
                "security_notes": parsed.get("security_notes", "Review before execution"),
                "best_practices": parsed.get("best_practices", []),
                "workflow_steps": parsed.get("workflow_steps", [])
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                "interpreted_command": f"Execute: {original_command}",
                "confidence": 0.5,
                "suggested_actions": ["Process command with caution"],
                "estimated_impact": "Unknown",
                "requires_approval": True,
                "error": f"Parse error: {str(e)}"
            }
    
    def _fallback_parsing(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        return {
            "interpreted_command": response[:200] + "..." if len(response) > 200 else response,
            "confidence": 0.6,
            "suggested_actions": ["Review and execute manually"],
            "estimated_impact": "Medium",
            "requires_approval": True
        }
    
    def is_healthy(self) -> bool:
        """Check if AI engine is healthy"""
        return self.is_healthy and self.gemini_service.is_healthy() 