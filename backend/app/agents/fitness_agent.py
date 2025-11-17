"""
Main Fitness Planning Agent.
This is the orchestrator that coordinates all specialized agents.
"""
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from app.core.config import settings


class FitnessAgent:
    """
    Main fitness planning agent that handles user conversations
    and coordinates specialized agents.
    """

    def __init__(self):
        """Initialize the fitness agent."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY,
        )

        self.system_prompt = """你是一个专业的健身训练规划助手，名叫 Fitness Planner AI。
你的目标是帮助用户达成他们的健身目标，提供个性化的训练计划、营养建议和进度追踪。

你的能力包括：
1. **用户引导**：帮助用户设定清晰、可量化的健身目标
2. **训练计划**：根据用户的目标、经验水平和训练频率，生成科学的训练计划
3. **营养建议**：计算每日所需的营养素，并提供饮食搭配建议
4. **进度分析**：分析用户的训练数据和身体指标，提供调整建议

你的特点：
- 专业：基于运动科学和营养学原理提供建议
- 个性化：根据每个用户的独特情况定制方案
- 耐心：引导初学者，挑战高级用户
- 鼓励：积极正面，帮助用户保持动力
- 安全：始终将用户的安全放在首位

当前对话上下文：
{context}

请用友好、专业的方式回应用户。如果需要更多信息才能提供建议，请主动询问。
"""

        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

    async def chat(
        self,
        message: str,
        user_context: Optional[Dict[str, Any]] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process user message and generate response.

        Args:
            message: User's message
            user_context: User profile and context information
            chat_history: Previous conversation history

        Returns:
            Agent's response
        """
        # Build context from user information
        context = self._build_context(user_context)

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt.format(context=context)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        # Create conversation chain
        conversation = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt,
            verbose=True
        )

        # Load chat history if provided
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    self.memory.chat_memory.add_user_message(msg["content"])
                else:
                    self.memory.chat_memory.add_ai_message(msg["content"])

        # Get response
        response = await conversation.apredict(input=message)

        return response

    def _build_context(self, user_context: Optional[Dict[str, Any]]) -> str:
        """Build context string from user information."""
        if not user_context:
            return "新用户，暂无个人信息。"

        context_parts = []

        # Basic info
        if user_context.get("name"):
            context_parts.append(f"姓名：{user_context['name']}")

        if user_context.get("age"):
            context_parts.append(f"年龄：{user_context['age']}岁")

        if user_context.get("gender"):
            context_parts.append(f"性别：{user_context['gender']}")

        # Body metrics
        if user_context.get("height"):
            context_parts.append(f"身高：{user_context['height']}cm")

        if user_context.get("weight"):
            context_parts.append(f"体重：{user_context['weight']}kg")

        if user_context.get("body_fat_percentage"):
            context_parts.append(f"体脂率：{user_context['body_fat_percentage']}%")

        # Fitness profile
        if user_context.get("fitness_goal"):
            goal_map = {
                "muscle_gain": "增肌",
                "fat_loss": "减脂",
                "strength": "力量提升",
                "endurance": "耐力提升",
                "general_fitness": "整体健康",
                "body_recomposition": "身体重组"
            }
            goal = goal_map.get(user_context["fitness_goal"], user_context["fitness_goal"])
            context_parts.append(f"健身目标：{goal}")

        if user_context.get("experience_level"):
            level_map = {
                "beginner": "初学者",
                "intermediate": "中级",
                "advanced": "高级"
            }
            level = level_map.get(user_context["experience_level"], user_context["experience_level"])
            context_parts.append(f"经验水平：{level}")

        if user_context.get("training_frequency"):
            context_parts.append(f"训练频率：每周{user_context['training_frequency']}次")

        if user_context.get("equipment_access"):
            equipment_map = {
                "gym": "健身房",
                "home": "家庭器械",
                "bodyweight": "自重训练",
                "minimal": "基础器械"
            }
            equipment = equipment_map.get(user_context["equipment_access"], user_context["equipment_access"])
            context_parts.append(f"器械条件：{equipment}")

        # Goals
        if user_context.get("target_weight"):
            context_parts.append(f"目标体重：{user_context['target_weight']}kg")

        if user_context.get("goal_timeframe"):
            context_parts.append(f"目标时间：{user_context['goal_timeframe']}周")

        # Dietary info
        if user_context.get("dietary_restrictions"):
            context_parts.append(f"饮食限制：{user_context['dietary_restrictions']}")

        if user_context.get("allergies"):
            context_parts.append(f"过敏原：{user_context['allergies']}")

        return "\n".join(context_parts) if context_parts else "新用户，暂无个人信息。"

    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user's intent from their message.

        Returns:
            Dictionary with intent type and extracted information
        """
        analysis_prompt = f"""分析以下用户消息，识别用户的意图和需求：

用户消息：{message}

请识别以下几类意图之一：
1. onboarding - 用户想要开始健身，需要引导设置目标
2. workout_plan - 用户需要训练计划
3. nutrition_advice - 用户需要营养建议
4. progress_update - 用户汇报进度或身体数据
5. question - 用户提问
6. general - 一般对话

请以JSON格式返回：
{{
    "intent": "意图类型",
    "confidence": 0.0-1.0,
    "extracted_info": {{}}
}}
"""

        response = await self.llm.apredict(analysis_prompt)

        # Parse response (simplified - in production use proper JSON parsing)
        return {
            "intent": "general",
            "confidence": 0.5,
            "extracted_info": {}
        }

    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
