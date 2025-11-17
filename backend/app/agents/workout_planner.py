"""
Workout Planning Agent - Specialized in creating training plans.

V1.1: 集成 RAG (检索增强生成) 系统，使用动作知识库提升计划质量
"""
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.services.rag import get_exercise_rag
import json


class WorkoutPlannerAgent:
    """
    Specialized agent for generating personalized workout plans.
    Implements FR-2: 智能化训练计划定制

    V1.1 Updates:
    - 集成动作库 RAG 系统
    - 基于向量检索推荐最佳动作
    - 提供详细的动作说明和技巧
    """

    def __init__(self):
        """Initialize the workout planner agent with RAG support."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.3,  # Lower temperature for more consistent plans
            max_tokens=3000,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        # 初始化 RAG 系统
        try:
            self.exercise_rag = get_exercise_rag()
        except Exception as e:
            print(f"警告: RAG 系统初始化失败: {e}")
            self.exercise_rag = None

    def _retrieve_relevant_exercises(
        self,
        user_profile: Dict[str, Any],
        n_results: int = 12
    ) -> List[Dict[str, Any]]:
        """
        使用 RAG 系统检索相关动作

        Args:
            user_profile: 用户资料
            n_results: 返回动作数量

        Returns:
            相关动作列表
        """
        if not self.exercise_rag:
            return []

        goal = user_profile.get("fitness_goal", "general_fitness")
        equipment = user_profile.get("equipment_access", "bodyweight")
        experience = user_profile.get("experience_level", "beginner")

        # 使用 RAG 推荐动作
        exercises = self.exercise_rag.recommend_exercises(
            goal=goal,
            equipment=equipment,
            difficulty=experience,
            n_results=n_results
        )

        return exercises

    async def generate_workout_plan(
        self,
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a personalized workout plan based on user profile.

        V1.1: 使用 RAG 系统检索最佳动作

        Args:
            user_profile: Dictionary containing user information

        Returns:
            Structured workout plan
        """
        # 检索相关动作
        relevant_exercises = self._retrieve_relevant_exercises(user_profile)

        # 生成计划提示词（包含RAG检索的动作）
        prompt = self._create_workout_plan_prompt(user_profile, relevant_exercises)
        response = await self.llm.apredict(prompt)

        # Parse and structure the response
        plan = self._parse_workout_plan(response, user_profile)

        # 添加RAG检索的动作详情
        if relevant_exercises:
            plan["recommended_exercises"] = relevant_exercises

        return plan

    def _create_workout_plan_prompt(
        self,
        user_profile: Dict[str, Any],
        relevant_exercises: List[Dict[str, Any]] = None
    ) -> str:
        """
        Create a detailed prompt for workout plan generation.

        V1.1: 包含 RAG 检索的推荐动作
        """

        goal = user_profile.get("fitness_goal", "general_fitness")
        experience = user_profile.get("experience_level", "beginner")
        frequency = user_profile.get("training_frequency", 3)
        equipment = user_profile.get("equipment_access", "bodyweight")

        # 构建推荐动作列表
        exercises_text = ""
        if relevant_exercises:
            exercises_text = "\n\n**推荐动作库**（从这些动作中选择）：\n"
            for ex in relevant_exercises:
                exercises_text += f"\n- **{ex['name']}** ({ex['english_name']})\n"
                exercises_text += f"  - 类别: {ex['category']}\n"
                exercises_text += f"  - 目标肌群: {', '.join(ex['target_muscles'])}\n"
                exercises_text += f"  - 设备: {ex['equipment']}\n"
                exercises_text += f"  - 难度: {ex['difficulty']}\n"
                exercises_text += f"  - 描述: {ex['description']}\n"

        prompt = f"""作为专业的健身教练，为以下用户生成一个详细的周训练计划：

**用户信息**：
- 健身目标：{goal}
- 经验水平：{experience}
- 训练频率：每周{frequency}次
- 可用器械：{equipment}
- 年龄：{user_profile.get('age', 'N/A')}
- 性别：{user_profile.get('gender', 'N/A')}
{exercises_text}

**任务要求**：
1. 根据训练频率（{frequency}次/周）合理分配训练部位
2. 对于每个训练日，提供：
   - 训练日名称（如：胸+三头、背+二头等）
   - 目标肌群
   - 具体动作列表（每个动作包括：名称、组数、次数、休息时间）
3. 解释为什么这样安排训练（训练原理）
4. 提供渐进建议

请以以下JSON格式返回：
```json
{{
    "plan_name": "计划名称",
    "workout_type": "训练类型（如：push_pull_legs, body_part_split等）",
    "duration_weeks": 12,
    "frequency_per_week": {frequency},
    "rationale": "为什么选择这个训练方案的详细解释",
    "weekly_schedule": [
        {{
            "day": 1,
            "name": "训练日名称",
            "target_muscles": ["目标肌群1", "目标肌群2"],
            "exercises": [
                {{
                    "name": "动作名称",
                    "sets": 3,
                    "reps": 10,
                    "rest_seconds": 60,
                    "notes": "动作要点"
                }}
            ]
        }}
    ],
    "progression_advice": "如何随着时间推进训练强度"
}}
```

确保计划科学、安全，适合用户的经验水平。
"""

        return prompt

    def _parse_workout_plan(self, llm_response: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse LLM response into structured workout plan.
        """
        try:
            # Try to extract JSON from response
            # Look for content between ```json and ```
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

            plan = json.loads(json_str)

            # Add user context
            plan["user_id"] = user_profile.get("user_id")
            plan["generation_prompt"] = llm_response

            return plan

        except json.JSONDecodeError:
            # Fallback: return a basic structure
            frequency = user_profile.get("training_frequency", 3)

            return {
                "plan_name": "个性化训练计划",
                "workout_type": "custom",
                "duration_weeks": 12,
                "frequency_per_week": frequency,
                "rationale": llm_response,
                "weekly_schedule": [],
                "progression_advice": "请咨询专业教练",
                "generation_prompt": llm_response,
                "user_id": user_profile.get("user_id")
            }

    async def suggest_workout_split(
        self,
        frequency: int,
        goal: str,
        experience: str
    ) -> Dict[str, Any]:
        """
        Suggest optimal workout split based on frequency and goals.
        """
        prompt = f"""为以下训练参数推荐最佳的训练分化方式：

训练频率：每周{frequency}次
健身目标：{goal}
经验水平：{experience}

请推荐训练分化方式（如：推拉腿、上下肢分化、部位分化等），并解释原因。

以JSON格式返回：
{{
    "recommended_split": "分化名称",
    "split_type": "类型代码",
    "days_breakdown": ["周一：...", "周二：...", ...],
    "rationale": "为什么推荐这个分化方式",
    "pros": ["优点1", "优点2"],
    "cons": ["缺点1", "缺点2"]
}}
"""

        response = await self.llm.apredict(prompt)

        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)

        except json.JSONDecodeError:
            return {
                "recommended_split": "自定义",
                "split_type": "custom",
                "days_breakdown": [],
                "rationale": response,
                "pros": [],
                "cons": []
            }

    async def adjust_workout_intensity(
        self,
        current_plan: Dict[str, Any],
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest adjustments to workout intensity based on progress.
        """
        prompt = f"""基于以下进度数据，分析是否需要调整训练强度：

**当前训练计划**：
{json.dumps(current_plan, ensure_ascii=False, indent=2)}

**进度数据**：
{json.dumps(progress_data, ensure_ascii=False, indent=2)}

请分析：
1. 用户是否在进步
2. 是否需要增加强度（重量、组数、次数）
3. 是否需要调整动作或休息时间
4. 具体的调整建议

以JSON格式返回：
{{
    "adjustment_needed": true/false,
    "progress_assessment": "进度评估",
    "recommendations": [
        {{
            "exercise": "动作名称",
            "current": "当前参数",
            "suggested": "建议参数",
            "reason": "调整原因"
        }}
    ],
    "overall_feedback": "总体反馈"
}}
"""

        response = await self.llm.apredict(prompt)

        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)

        except json.JSONDecodeError:
            return {
                "adjustment_needed": False,
                "progress_assessment": response,
                "recommendations": [],
                "overall_feedback": "继续保持当前训练"
            }
