"""
Executor Agent - Creates detailed implementation plan and timeline
"""
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class Executor:
    """
    Agent responsible for creating detailed implementation plans,
    timelines, resource allocation, and risk management.
    """
    
    def __init__(self):
        self.client = Config.get_openai_client()
        self.model = Config.MODEL_NAME
        
    def create_execution_plan(
        self,
        strategy: str,
        creative_concepts: List[Dict[str, Any]],
        channels: List[Dict[str, Any]],
        budget: float,
        duration: int
    ) -> Dict[str, Any]:
        """
        Create comprehensive execution plan
        
        Args:
            strategy (str): Campaign strategy
            creative_concepts (List): Creative concepts
            channels (List): Channel recommendations
            budget (float): Available budget
            duration (int): Campaign duration in days
            
        Returns:
            Dict containing timeline, resources, steps, and risks
        """
        
        try:
            # Create execution plan using AI
            execution_plan = self._ai_generate_plan(
                strategy, creative_concepts, channels, budget, duration
            )
            
            # Enhance with structured timeline and resource allocation
            execution_plan = self._enhance_execution_plan(
                execution_plan, budget, duration, channels
            )
            
            return execution_plan
            
        except Exception as e:
            print(f"Error in execution planning: {str(e)}")
            return self._get_fallback_execution_plan(budget, duration, channels)
    
    def _ai_generate_plan(
        self,
        strategy: str,
        creative_concepts: List[Dict[str, Any]],
        channels: List[Dict[str, Any]],
        budget: float,
        duration: int
    ) -> Dict[str, Any]:
        """Generate execution plan using AI"""
        
        # Prepare creative summary
        concepts_summary = "\n".join([
            f"- {concept.get('name', 'Concept')}: {concept.get('description', '')[:100]}"
            for concept in creative_concepts[:3]
        ])
        
        # Prepare channel summary
        channels_summary = "\n".join([
            f"- {channel.get('name', 'Channel')}: ${channel.get('budget_allocation', 0):,.0f}"
            for channel in channels[:5]
        ])
        
        prompt = f"""
        Create a detailed execution plan for this campaign:
        
        STRATEGY:
        {strategy}
        
        CREATIVE CONCEPTS:
        {concepts_summary}
        
        CHANNELS & BUDGET:
        {channels_summary}
        
        CAMPAIGN PARAMETERS:
        - Total Budget: ${budget:,.2f}
        - Duration: {duration} days
        - Start Date: {datetime.now().strftime('%Y-%m-%d')}
        
        REQUIRED OUTPUT:
        Create a comprehensive execution plan including:
        
        1. TIMELINE: Week-by-week breakdown of activities
        2. RESOURCE ALLOCATION: Team roles, budget distribution, tools needed
        3. IMPLEMENTATION STEPS: Detailed action items with deadlines
        4. RISK MITIGATION: Potential risks and mitigation strategies
        5. QUALITY CHECKPOINTS: Review gates and approval processes
        
        Focus on practical, actionable steps that ensure campaign success.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a marketing campaign project manager. "
                        "Respond with ONLY a valid JSON object — no markdown, no backticks, no extra text. "
                        "Use this exact structure: "
                        '{"timeline": {"pre_launch": ["activity"], "week_1": ["activity"], "week_2": ["activity"], "post_campaign": ["activity"]}, '
                        '"resources": {"team_requirements": ["string"], "budget_breakdown": ["string"], "tools_needed": ["string"]}, '
                        '"steps": [{"task": "max 5 words", "priority": "high|medium|low", "estimated_hours": number, "assignee": "string", "deadline": "YYYY-MM-DD"}], '
                        '"risks": ["string"]}. '
                        "CRITICAL: every step task field MUST be 4-5 words maximum (e.g. 'Launch social media ads', 'Brief creative team', 'Set up tracking'). "
                        "Do not include any text outside the JSON object."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=2500
        )
        
        plan_text = response.choices[0].message.content
        return self._parse_execution_plan(plan_text)
    
    def _parse_execution_plan(self, plan_text: str) -> Dict[str, Any]:
        """Parse AI response into structured execution plan (4-layer JSON pipeline)."""

        import re

        def _truncate_tasks(data: Dict) -> Dict:
            """Ensure every step task is at most 5 words."""
            for step in data.get("steps", []):
                words = step.get("task", "").split()
                if len(words) > 5:
                    step["task"] = " ".join(words[:5])
            return data

        # -- 1. Direct JSON parse -------------------------------------------
        try:
            data = json.loads(plan_text.strip())
            if isinstance(data, dict):
                return _truncate_tasks(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # -- 2. Strip markdown fences then parse ----------------------------
        try:
            cleaned = re.sub(r"```(?:json)?|```", "", plan_text).strip()
            data = json.loads(cleaned)
            if isinstance(data, dict):
                return _truncate_tasks(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # -- 3. Extract outermost { } block ---------------------------------
        try:
            start = plan_text.find("{")
            end = plan_text.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(plan_text[start:end])
                if isinstance(data, dict):
                    return _truncate_tasks(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # -- 4. Return empty dict — _enhance_execution_plan fills defaults --
        return {}
    
    def _extract_week_number(self, line: str) -> str:
        """Extract week identifier from timeline line"""
        line_lower = line.lower()
        if "week 1" in line_lower or "week one" in line_lower:
            return "week_1"
        elif "week 2" in line_lower or "week two" in line_lower:
            return "week_2"
        elif "week 3" in line_lower or "week three" in line_lower:
            return "week_3"
        elif "week 4" in line_lower or "week four" in line_lower:
            return "week_4"
        elif "pre" in line_lower or "preparation" in line_lower:
            return "pre_launch"
        elif "launch" in line_lower:
            return "launch_week"
        elif "post" in line_lower or "wrap" in line_lower:
            return "post_campaign"
        else:
            return None
    
    def _create_implementation_step(self, content: str) -> Dict[str, Any]:
        """Create structured implementation step"""
        return {
            "task": content,
            "priority": self._determine_priority(content),
            "estimated_hours": self._estimate_hours(content),
            "dependencies": [],
            "assignee": self._suggest_assignee(content),
            "deadline": self._calculate_deadline(content)
        }
    
    def _determine_priority(self, task: str) -> str:
        """Determine task priority based on content"""
        task_lower = task.lower()
        high_priority_keywords = ["launch", "approval", "legal", "creative", "strategy"]
        medium_priority_keywords = ["content", "design", "setup", "test"]
        
        for keyword in high_priority_keywords:
            if keyword in task_lower:
                return "high"
        
        for keyword in medium_priority_keywords:
            if keyword in task_lower:
                return "medium"
        
        return "low"
    
    def _estimate_hours(self, task: str) -> int:
        """Estimate hours required for task"""
        task_lower = task.lower()
        if "strategy" in task_lower or "planning" in task_lower:
            return 16
        elif "creative" in task_lower or "design" in task_lower:
            return 24
        elif "content" in task_lower:
            return 8
        elif "setup" in task_lower or "configuration" in task_lower:
            return 4
        else:
            return 4
    
    def _suggest_assignee(self, task: str) -> str:
        """Suggest team member for task"""
        task_lower = task.lower()
        if "creative" in task_lower or "design" in task_lower:
            return "Creative Team"
        elif "content" in task_lower or "copy" in task_lower:
            return "Content Team"
        elif "strategy" in task_lower or "planning" in task_lower:
            return "Strategy Team"
        elif "technical" in task_lower or "setup" in task_lower:
            return "Technical Team"
        elif "legal" in task_lower or "approval" in task_lower:
            return "Legal/Compliance"
        else:
            return "Campaign Manager"
    
    def _calculate_deadline(self, task: str) -> str:
        """Calculate deadline for task"""
        # Simplified deadline calculation
        base_date = datetime.now()
        task_lower = task.lower()
        
        if "immediate" in task_lower or "urgent" in task_lower:
            deadline = base_date + timedelta(days=2)
        elif "preparation" in task_lower or "setup" in task_lower:
            deadline = base_date + timedelta(days=7)
        elif "creative" in task_lower:
            deadline = base_date + timedelta(days=10)
        elif "launch" in task_lower:
            deadline = base_date + timedelta(days=14)
        else:
            deadline = base_date + timedelta(days=5)
        
        return deadline.strftime("%Y-%m-%d")
    
    def _add_resource_detail(self, resources: Dict, content: str) -> None:
        """Add resource detail to resources dictionary"""
        content_lower = content.lower()
        
        if "team" in content_lower or "people" in content_lower:
            if "team_requirements" not in resources:
                resources["team_requirements"] = []
            resources["team_requirements"].append(content)
        elif "budget" in content_lower or "cost" in content_lower or "$" in content:
            if "budget_breakdown" not in resources:
                resources["budget_breakdown"] = []
            resources["budget_breakdown"].append(content)
        elif "tool" in content_lower or "software" in content_lower or "platform" in content_lower:
            if "tools_needed" not in resources:
                resources["tools_needed"] = []
            resources["tools_needed"].append(content)
        else:
            if "additional_resources" not in resources:
                resources["additional_resources"] = []
            resources["additional_resources"].append(content)
    
    def _normalize_list_fields(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all fields that should be lists are actually lists, not strings."""
        # Normalize top-level list fields
        for key in ("risks",):
            val = plan.get(key)
            if isinstance(val, str):
                plan[key] = [item.strip() for item in val.split(",") if item.strip()]

        # Normalize nested resource list fields
        resources = plan.get("resources")
        if isinstance(resources, dict):
            for key in ("team_requirements", "budget_breakdown", "tools_needed"):
                val = resources.get(key)
                if isinstance(val, str):
                    resources[key] = [item.strip() for item in val.split(",") if item.strip()]

        # Normalize timeline list fields
        timeline = plan.get("timeline")
        if isinstance(timeline, dict):
            for key, val in timeline.items():
                if isinstance(val, str):
                    timeline[key] = [item.strip() for item in val.split(",") if item.strip()]

        return plan

    def _enhance_execution_plan(
        self,
        plan: Dict[str, Any],
        budget: float,
        duration: int,
        channels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhance execution plan with structured data"""

        # Fix any string fields that should be lists before applying defaults
        plan = self._normalize_list_fields(plan)

        # Ensure timeline has proper structure
        if not plan.get("timeline"):
            plan["timeline"] = self._create_default_timeline(duration)
        
        # Ensure resource allocation
        if not plan.get("resources"):
            plan["resources"] = self._create_default_resources(budget, channels)
        
        # Ensure implementation steps
        if not plan.get("steps"):
            plan["steps"] = self._create_default_steps(channels)
        
        # Ensure risk mitigation
        if not plan.get("risks"):
            plan["risks"] = self._create_default_risks()
        
        return plan
    
    def _create_default_timeline(self, duration: int) -> Dict[str, List[str]]:
        """Create default timeline structure"""
        weeks = max(1, duration // 7)
        timeline = {}
        
        # Pre-launch
        timeline["pre_launch"] = [
            "Finalize campaign strategy and creative concepts",
            "Set up tracking and analytics",
            "Prepare content assets",
            "Configure advertising accounts"
        ]
        
        # Campaign weeks
        for i in range(1, min(weeks + 1, 5)):  # Limit to 4 active weeks
            week_key = f"week_{i}"
            if i == 1:
                timeline[week_key] = [
                    "Launch campaign across all channels",
                    "Monitor initial performance",
                    "Daily optimization and adjustments",
                    "Stakeholder communication"
                ]
            else:
                timeline[week_key] = [
                    "Continue campaign optimization",
                    "A/B test new creative variations",
                    "Analyze performance data",
                    "Adjust targeting and budgets"
                ]
        
        # Post-campaign
        timeline["post_campaign"] = [
            "Campaign wrap-up and final optimization",
            "Comprehensive performance analysis",
            "Insights documentation and reporting",
            "Team debrief and lessons learned"
        ]
        
        return timeline
    
    def _create_default_resources(
        self, 
        budget: float, 
        channels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create default resource allocation"""
        return {
            "team_requirements": [
                "Campaign Manager (full-time)",
                "Creative Designer (0.5 FTE)",
                "Content Creator (0.5 FTE)",
                "Data Analyst (0.25 FTE)",
                "Account Manager (0.25 FTE)"
            ],
            "budget_breakdown": [
                f"Media spend: ${budget * 0.70:,.2f}",
                f"Creative production: ${budget * 0.15:,.2f}",
                f"Tools and platforms: ${budget * 0.10:,.2f}",
                f"Contingency: ${budget * 0.05:,.2f}"
            ],
            "tools_needed": [
                "Campaign management platform",
                "Analytics and tracking tools",
                "Creative design software",
                "Social media management tools",
                "Reporting and dashboard tools"
            ]
        }
    
    def _create_default_steps(self, channels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create default implementation steps with short task names (max 5 words)."""
        steps = [
            {
                "task": "Finalise strategy & objectives",
                "priority": "high",
                "estimated_hours": 16,
                "assignee": "Strategy Team",
                "deadline": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            },
            {
                "task": "Develop creative concepts",
                "priority": "high",
                "estimated_hours": 32,
                "assignee": "Creative Team",
                "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            }
        ]

        for channel in channels:
            name_words = channel.get("name", "Channel").split()[:3]
            steps.append({
                "task": f"Set up {' '.join(name_words)}",
                "priority": "medium",
                "estimated_hours": 8,
                "assignee": "Campaign Manager",
                "deadline": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
            })

        steps.extend([
            {
                "task": "Launch & monitor campaign",
                "priority": "high",
                "estimated_hours": 12,
                "assignee": "Campaign Manager",
                "deadline": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            },
            {
                "task": "Weekly performance review",
                "priority": "medium",
                "estimated_hours": 8,
                "assignee": "Data Analyst",
                "deadline": "Recurring"
            }
        ])

        return steps
    
    def _create_default_risks(self) -> List[str]:
        """Create default risk mitigation strategies"""
        return [
            "Budget overrun - Implement daily budget monitoring and automated caps",
            "Low performance - Prepare backup creative variations and targeting options",
            "Technical issues - Have technical support contacts and backup systems ready",
            "Competitive response - Monitor competitor activities and prepare counter-strategies",
            "Creative fatigue - Develop content refresh schedule and additional asset pipeline",
            "Regulatory changes - Stay updated on platform policies and legal requirements",
            "Team capacity - Cross-train team members and identify backup resources",
            "External factors - Monitor market conditions and prepare contingency plans"
        ]
    
    def _get_fallback_execution_plan(
        self,
        budget: float,
        duration: int,
        channels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Provide fallback execution plan if AI call fails"""
        return {
            "timeline": self._create_default_timeline(duration),
            "resources": self._create_default_resources(budget, channels),
            "steps": self._create_default_steps(channels),
            "risks": self._create_default_risks()
        }