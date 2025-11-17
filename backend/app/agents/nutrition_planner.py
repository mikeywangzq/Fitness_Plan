"""
Nutrition Planning Agent - Specialized in nutrition and diet planning.
"""
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from app.core.config import settings
import json


class NutritionPlannerAgent:
    """
    Specialized agent for nutrition planning and meal tracking.
    Implements FR-3: 营养建议与追踪
    """

    def __init__(self):
        """Initialize the nutrition planner agent."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.3,
            max_tokens=3000,
            openai_api_key=settings.OPENAI_API_KEY,
        )

    async def calculate_macros(
        self,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate daily macro requirements based on user profile and goals.

        Args:
            user_profile: User information including weight, goal, activity level

        Returns:
            Macro calculations and rationale
        """
        weight = user_profile.get("weight", 70)
        height = user_profile.get("height", 170)
        age = user_profile.get("age", 30)
        gender = user_profile.get("gender", "male")
        goal = user_profile.get("fitness_goal", "general_fitness")
        activity_level = user_profile.get("training_frequency", 3)

        prompt = f"""作为营养师，为以下用户计算每日营养需求：

**用户信息**：
- 体重：{weight}kg
- 身高：{height}cm
- 年龄：{age}岁
- 性别：{gender}
- 健身目标：{goal}
- 运动频率：每周{activity_level}次

**任务**：
1. 计算基础代谢率（BMR）
2. 计算每日总能量消耗（TDEE）
3. 根据目标调整热量摄入
4. 分配三大营养素（蛋白质、碳水、脂肪）比例
5. 提供详细解释

请以JSON格式返回：
```json
{{
    "bmr": 基础代谢率,
    "tdee": 每日总消耗,
    "target_calories": 目标热量,
    "calorie_adjustment": "热量调整说明",
    "macros": {{
        "protein_g": 蛋白质克数,
        "carbs_g": 碳水化合物克数,
        "fats_g": 脂肪克数,
        "fiber_g": 纤维克数
    }},
    "macro_percentages": {{
        "protein": "百分比",
        "carbs": "百分比",
        "fats": "百分比"
    }},
    "rationale": "为什么这样分配营养素的详细解释",
    "meal_timing": "建议的进餐时间和频率"
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response, user_profile)

    async def generate_meal_plan(
        self,
        macro_targets: Dict[str, float],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a daily meal plan based on macro targets.

        Args:
            macro_targets: Target macros (protein, carbs, fats, calories)
            user_preferences: Dietary restrictions, allergies, meal frequency

        Returns:
            Structured meal plan
        """
        dietary_restrictions = user_preferences.get("dietary_restrictions", "无")
        allergies = user_preferences.get("allergies", "无")
        meals_per_day = user_preferences.get("meals_per_day", 3)

        prompt = f"""作为营养师，设计一份符合以下营养目标的每日饮食计划：

**营养目标**：
- 每日热量：{macro_targets.get('calories', 2000)} kcal
- 蛋白质：{macro_targets.get('protein_g', 150)}g
- 碳水化合物：{macro_targets.get('carbs_g', 200)}g
- 脂肪：{macro_targets.get('fats_g', 60)}g

**用户偏好**：
- 每日餐数：{meals_per_day}餐
- 饮食限制：{dietary_restrictions}
- 过敏原：{allergies}

**要求**：
为每餐提供具体的食物和份量建议，确保总营养素接近目标值。

请以JSON格式返回：
```json
{{
    "daily_plan": [
        {{
            "meal_type": "早餐",
            "time": "建议时间",
            "foods": [
                {{
                    "name": "食物名称",
                    "amount": "份量（克）",
                    "calories": 热量,
                    "protein": 蛋白质,
                    "carbs": 碳水,
                    "fats": 脂肪
                }}
            ],
            "total_macros": {{
                "calories": 总热量,
                "protein": 总蛋白质,
                "carbs": 总碳水,
                "fats": 总脂肪
            }}
        }}
    ],
    "daily_totals": {{
        "calories": 总热量,
        "protein": 总蛋白质,
        "carbs": 总碳水,
        "fats": 总脂肪
    }},
    "meal_prep_tips": "备餐建议",
    "hydration_reminder": "水分摄入建议"
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response)

    async def analyze_meal_log(
        self,
        meals: List[Dict[str, Any]],
        target_macros: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Analyze user's meal log and provide feedback.

        Args:
            meals: List of meals logged by user
            target_macros: User's target macros

        Returns:
            Analysis and recommendations
        """
        # Calculate current totals
        current_totals = {
            "calories": sum(m.get("calories", 0) for m in meals),
            "protein_g": sum(m.get("protein_g", 0) for m in meals),
            "carbs_g": sum(m.get("carbs_g", 0) for m in meals),
            "fats_g": sum(m.get("fats_g", 0) for m in meals),
        }

        prompt = f"""分析用户今日的饮食记录：

**目标营养素**：
- 热量：{target_macros.get('calories', 2000)} kcal
- 蛋白质：{target_macros.get('protein_g', 150)}g
- 碳水：{target_macros.get('carbs_g', 200)}g
- 脂肪：{target_macros.get('fats_g', 60)}g

**当前摄入**：
- 热量：{current_totals['calories']} kcal
- 蛋白质：{current_totals['protein_g']}g
- 碳水：{current_totals['carbs_g']}g
- 脂肪：{current_totals['fats_g']}g

**已记录的餐食**：
{json.dumps(meals, ensure_ascii=False, indent=2)}

**任务**：
1. 分析当前营养素摄入是否达标
2. 指出不足或过量的部分
3. 提供即时反馈和建议

请以JSON格式返回：
```json
{{
    "current_status": {{
        "calories": {{"consumed": 已摄入, "remaining": 剩余, "percentage": 百分比}},
        "protein": {{"consumed": 已摄入, "remaining": 剩余, "percentage": 百分比}},
        "carbs": {{"consumed": 已摄入, "remaining": 剩余, "percentage": 百分比}},
        "fats": {{"consumed": 已摄入, "remaining": 剩余, "percentage": 百分比}}
    }},
    "feedback": "总体反馈",
    "recommendations": [
        "建议1：还需要摄入xxx",
        "建议2：..."
    ],
    "suggested_foods": [
        "可以吃的食物建议"
    ]
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response)

    async def parse_food_description(
        self,
        description: str
    ) -> Dict[str, Any]:
        """
        Parse natural language food description into structured data.

        Args:
            description: Natural language description (e.g., "我吃了150克鸡胸肉和一个苹果")

        Returns:
            Structured food data with estimated macros
        """
        prompt = f"""用户用自然语言描述了他们吃的食物："{description}"

请解析这段描述，识别食物种类和份量，并估算营养价值。

以JSON格式返回：
```json
{{
    "foods": [
        {{
            "name": "食物名称",
            "amount_g": 估计重量（克）,
            "amount_description": "份量描述",
            "calories": 估计热量,
            "protein_g": 估计蛋白质,
            "carbs_g": 估计碳水,
            "fats_g": 估计脂肪,
            "confidence": "估算置信度（high/medium/low）"
        }}
    ],
    "total_macros": {{
        "calories": 总热量,
        "protein_g": 总蛋白质,
        "carbs_g": 总碳水,
        "fats_g": 总脂肪
    }},
    "notes": "解析说明或不确定的地方"
}}
```
"""

        response = await self.llm.apredict(prompt)
        return self._parse_json_response(response)

    def _parse_json_response(
        self,
        llm_response: str,
        additional_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
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

            result = json.loads(json_str)

            if additional_data:
                result.update(additional_data)

            return result

        except json.JSONDecodeError:
            return {
                "error": "Failed to parse response",
                "raw_response": llm_response
            }
