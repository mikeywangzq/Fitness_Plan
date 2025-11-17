"""
Progress Analysis Agent - Analyzes user progress and provides recommendations.
"""
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from app.core.config import settings
import json
from datetime import datetime, timedelta


class ProgressAnalyzerAgent:
    """
    Specialized agent for analyzing user progress and providing adjustments.
    Implements FR-4: 进度分析与调整
    """

    def __init__(self):
        """Initialize the progress analyzer agent."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.4,
            max_tokens=2500,
            openai_api_key=settings.OPENAI_API_KEY,
        )

    async def analyze_training_progress(
        self,
        workout_history: List[Dict[str, Any]],
        user_goal: str
    ) -> Dict[str, Any]:
        """
        Analyze user's training progress.

        Args:
            workout_history: List of completed workouts with performance data
            user_goal: User's fitness goal

        Returns:
            Analysis and recommendations
        """
        prompt = f"""分析用户的训练进度：

**用户目标**：{user_goal}

**训练历史**：
{json.dumps(workout_history, ensure_ascii=False, indent=2)}

**分析要点**：
1. 训练一致性（是否按计划完成）
2. 力量/耐力进步趋势
3. 主要动作的表现变化
4. 是否存在平台期
5. 建议的调整方向

请以JSON格式返回：
```json
{{
    "consistency_score": 0-100,
    "consistency_analysis": "训练一致性评估",
    "strength_progress": {{
        "trend": "improving/stable/declining",
        "key_lifts": [
            {{
                "exercise": "动作名称",
                "initial_weight": 初始重量,
                "current_weight": 当前重量,
                "improvement_percentage": 提升百分比,
                "trend": "上升/稳定/下降"
            }}
        ]
    }},
    "plateau_detected": true/false,
    "plateau_analysis": "平台期分析（如果存在）",
    "recommendations": [
        {{
            "category": "训练/营养/恢复",
            "recommendation": "具体建议",
            "priority": "high/medium/low",
            "rationale": "建议原因"
        }}
    ],
    "overall_assessment": "总体评估",
    "motivation_message": "鼓励的话"
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response)

    async def analyze_body_metrics(
        self,
        metrics_history: List[Dict[str, Any]],
        user_goal: str,
        target_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Analyze changes in body metrics over time.

        Args:
            metrics_history: Historical body measurements
            user_goal: User's fitness goal
            target_metrics: Target weight, body fat, etc.

        Returns:
            Analysis of progress towards goals
        """
        prompt = f"""分析用户的身体指标变化：

**用户目标**：{user_goal}

**目标指标**：
{json.dumps(target_metrics, ensure_ascii=False, indent=2)}

**历史数据**：
{json.dumps(metrics_history, ensure_ascii=False, indent=2)}

**分析要点**：
1. 体重变化趋势和速率
2. 体脂率变化（如果有数据）
3. 是否朝着目标前进
4. 变化速度是否健康和可持续
5. 需要的调整建议

请以JSON格式返回：
```json
{{
    "weight_analysis": {{
        "start_weight": 起始体重,
        "current_weight": 当前体重,
        "change": 变化量,
        "change_percentage": 变化百分比,
        "trend": "increasing/decreasing/stable",
        "weekly_average_change": 周均变化,
        "is_healthy_rate": true/false
    }},
    "body_fat_analysis": {{
        "start_bf": 起始体脂,
        "current_bf": 当前体脂,
        "change": 变化量,
        "trend": "improving/stable/worsening"
    }},
    "goal_progress": {{
        "target_weight": 目标体重,
        "current_weight": 当前体重,
        "remaining": 剩余差距,
        "percentage_complete": 完成百分比,
        "estimated_weeks_to_goal": 预估达成周数
    }},
    "health_assessment": "健康状况评估",
    "recommendations": [
        "调整建议"
    ],
    "concerns": [
        "需要注意的问题（如果有）"
    ]
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response)

    async def generate_weekly_report(
        self,
        week_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive weekly progress report.

        Args:
            week_data: All data from the past week (workouts, nutrition, metrics)

        Returns:
            Weekly report with insights
        """
        prompt = f"""为用户生成本周的健身进度报告：

**本周数据**：
{json.dumps(week_data, ensure_ascii=False, indent=2)}

请生成一份全面的周报，包括：
1. 训练完成情况总结
2. 营养摄入分析
3. 身体指标变化
4. 本周亮点和成就
5. 需要改进的地方
6. 下周建议

以JSON格式返回：
```json
{{
    "week_number": 周数,
    "date_range": "日期范围",
    "training_summary": {{
        "workouts_completed": 完成次数,
        "workouts_planned": 计划次数,
        "completion_rate": 完成率,
        "total_volume": 总训练量,
        "highlights": ["本周训练亮点"]
    }},
    "nutrition_summary": {{
        "average_calories": 平均热量,
        "average_protein": 平均蛋白质,
        "adherence_rate": 饮食计划遵守率,
        "notes": "营养方面的观察"
    }},
    "body_metrics_change": {{
        "weight_change": 体重变化,
        "trend": "趋势"
    }},
    "achievements": [
        "本周成就"
    ],
    "areas_for_improvement": [
        "需要改进的地方"
    ],
    "next_week_focus": [
        "下周重点"
    ],
    "motivational_message": "鼓励的话"
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response)

    async def suggest_adjustments(
        self,
        current_plan: Dict[str, Any],
        progress_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest specific adjustments to workout or nutrition plan.

        Args:
            current_plan: Current workout/nutrition plan
            progress_analysis: Recent progress analysis

        Returns:
            Specific adjustment recommendations
        """
        prompt = f"""基于进度分析，建议对当前计划的调整：

**当前计划**：
{json.dumps(current_plan, ensure_ascii=False, indent=2)}

**进度分析**：
{json.dumps(progress_analysis, ensure_ascii=False, indent=2)}

请提供具体的调整建议：

以JSON格式返回：
```json
{{
    "adjustment_needed": true/false,
    "urgency": "high/medium/low",
    "workout_adjustments": [
        {{
            "type": "调整类型（增加重量/改变动作/调整组数等）",
            "specific_change": "具体改变",
            "reason": "原因",
            "expected_outcome": "预期效果"
        }}
    ],
    "nutrition_adjustments": [
        {{
            "nutrient": "营养素",
            "current": 当前值,
            "suggested": 建议值,
            "reason": "原因"
        }}
    ],
    "recovery_recommendations": [
        "恢复建议"
    ],
    "implementation_plan": "如何实施这些调整",
    "monitoring_points": [
        "需要监控的指标"
    ]
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response)

    async def detect_issues(
        self,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect potential issues like overtraining, under-eating, etc.

        Args:
            user_data: Comprehensive user data

        Returns:
            Issue detection and warnings
        """
        prompt = f"""分析用户数据，检测潜在问题：

**用户数据**：
{json.dumps(user_data, ensure_ascii=False, indent=2)}

检测以下问题：
1. 过度训练迹象
2. 营养不足
3. 恢复不充分
4. 不健康的减重速度
5. 训练不平衡
6. 其他健康风险

以JSON格式返回：
```json
{{
    "issues_detected": [
        {{
            "issue_type": "问题类型",
            "severity": "high/medium/low",
            "description": "问题描述",
            "indicators": ["支持这个判断的指标"],
            "recommendations": ["解决建议"],
            "action_required": "是否需要立即行动"
        }}
    ],
    "overall_health_score": 0-100,
    "warnings": [
        "警告信息"
    ],
    "positive_notes": [
        "做得好的地方"
    ]
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response)

    def _parse_json_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            if "```json" in llm_response:
                start = llm_response.find("```json") + 7
                end = llm_response.find("```", start)
                json_str = llm_response[start:end].strip()
            elif "```" in llm_response:
                start = llm_response.find("```") + 3
                end = llm_response.find("```", start)
                json_str = llm_response[start:end].strip()
            else:
                json_str = llm_response.strip()

            return json.loads(json_str)

        except json.JSONDecodeError:
            return {
                "error": "Failed to parse response",
                "raw_response": llm_response
            }
