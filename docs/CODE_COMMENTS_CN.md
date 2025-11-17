# 代码中文注释说明文档

本文档为 Fitness Planner Agent 项目的核心代码提供详细的中文注释说明。

## 📂 后端架构说明

### 1. 应用入口 (`backend/app/main.py`)

**作用**: FastAPI 主应用入口，负责应用初始化和路由注册

**关键组件**:
- `FastAPI()`: 创建应用实例，配置标题、版本、描述
- `CORSMiddleware`: 配置跨域策略，允许前端访问
- `include_router()`: 注册各功能模块的API路由

**端点**:
- `GET /`: 根路径，返回应用信息
- `GET /health`: 健康检查，用于监控和负载均衡

---

### 2. 配置管理 (`backend/app/core/config.py`)

**作用**: 集中管理应用配置，使用 Pydantic Settings 从环境变量读取配置

**主要配置**:
```python
class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str              # 应用名称
    APP_VERSION: str           # 版本号
    DEBUG: bool                # 调试模式

    # LLM 配置
    OPENAI_API_KEY: str        # OpenAI API 密钥（必填）
    LLM_MODEL: str             # 使用的模型名称
    LLM_TEMPERATURE: float     # 创造性程度 (0-1)
    LLM_MAX_TOKENS: int        # 最大生成长度

    # 数据库配置
    DATABASE_URL: str          # 数据库连接URL

    # 安全配置
    SECRET_KEY: str            # JWT 密钥
    ALGORITHM: str             # 加密算法
```

**使用方式**: 通过 `.env` 文件设置环境变量

---

### 3. 数据库管理 (`backend/app/core/database.py`)

**作用**: 管理数据库连接和会话

**核心组件**:
```python
# 异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,  # 是否打印SQL语句
    future=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后对象不过期
)

# 获取数据库会话（依赖注入）
async def get_db() -> AsyncSession:
    """FastAPI 依赖项，为每个请求提供数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**使用示例**:
```python
@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

---

## 🤖 AI Agent 架构说明

### 1. 主协调 Agent (`backend/app/agents/fitness_agent.py`)

**作用**: 主对话协调器，负责理解用户意图并调度专门的 Agent

**核心功能**:

#### `__init__()` 初始化
```python
def __init__(self):
    # 初始化 OpenAI LLM
    self.llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    # 系统提示词：定义 Agent 的角色和能力
    self.system_prompt = """你是专业的健身助手..."""

    # 对话记忆：保存历史消息
    self.memory = ConversationBufferMemory()
```

#### `async chat()` 处理对话
```python
async def chat(message, user_context, chat_history):
    """
    处理用户消息并生成响应

    Args:
        message: 用户输入的消息
        user_context: 用户上下文信息（目标、身体数据等）
        chat_history: 历史对话记录

    Returns:
        str: Agent 的回复
    """
    # 1. 构建上下文
    context = self._build_context(user_context)

    # 2. 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", self.system_prompt.format(context=context)),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    # 3. 生成回复
    response = await conversation.apredict(input=message)

    return response
```

#### `_build_context()` 构建用户上下文
```python
def _build_context(self, user_context):
    """
    将用户信息格式化为易于 LLM 理解的文本

    包括：身体数据、健身目标、训练频率、器械条件等
    """
    context_parts = []

    if user_context.get("fitness_goal"):
        goal_map = {
            "muscle_gain": "增肌",
            "fat_loss": "减脂",
            # ...
        }
        context_parts.append(f"健身目标：{goal_map[goal]}")

    # ... 处理其他字段

    return "\n".join(context_parts)
```

---

### 2. 训练计划生成 Agent (`backend/app/agents/workout_planner.py`)

**作用**: 专门负责生成个性化训练计划

**核心方法**:

#### `generate_workout_plan()` 生成训练计划
```python
async def generate_workout_plan(user_profile: Dict) -> Dict:
    """
    基于用户资料生成训练计划

    Args:
        user_profile: {
            "fitness_goal": "muscle_gain",
            "experience_level": "intermediate",
            "training_frequency": 5,  # 每周5次
            "equipment_access": "gym",
        }

    Returns:
        {
            "plan_name": "5天增肌计划（推拉腿）",
            "workout_type": "push_pull_legs",
            "weekly_schedule": [
                {
                    "day": 1,
                    "name": "推（胸+肩+三头）",
                    "exercises": [...]
                }
            ],
            "rationale": "为什么这样安排...",
            "progression_advice": "如何渐进..."
        }
    """
    # 1. 构建详细的 prompt
    prompt = self._create_workout_plan_prompt(user_profile)

    # 2. 调用 LLM 生成计划
    response = await self.llm.apredict(prompt)

    # 3. 解析 JSON 响应
    plan = self._parse_workout_plan(response)

    return plan
```

**Prompt 设计要点**:
```python
def _create_workout_plan_prompt(self, user_profile):
    """
    创建结构化的提示词

    要求 LLM 返回 JSON 格式，包含：
    - plan_name: 计划名称
    - workout_type: 训练类型
    - weekly_schedule: 周计划数组
      - day: 星期几
      - exercises: 动作列表
        - name: 动作名
        - sets: 组数
        - reps: 次数
        - rest_seconds: 休息时间
        - notes: 要点提示
    """
    return f"""作为专业健身教练，为以下用户生成训练计划：

用户信息：
- 目标：{user_profile['fitness_goal']}
- 经验：{user_profile['experience_level']}
- 频率：每周{user_profile['training_frequency']}次

请以 JSON 格式返回...
```json
{{
    "plan_name": "...",
    "weekly_schedule": [...]
}}
```
"""
```

---

### 3. 营养规划 Agent (`backend/app/agents/nutrition_planner.py`)

**作用**: 计算营养需求、生成饮食计划、解析饮食记录

**核心方法**:

#### `calculate_macros()` 计算宏量营养素
```python
async def calculate_macros(user_profile: Dict) -> Dict:
    """
    计算每日营养需求

    基于以下公式：
    1. BMR (基础代谢率) = Mifflin-St Jeor 公式
    2. TDEE (每日总消耗) = BMR × 活动系数
    3. 目标热量 = TDEE ± 调整值
    4. 宏量分配 = 根据目标分配蛋白质/碳水/脂肪比例

    Returns:
        {
            "bmr": 1650,
            "tdee": 2400,
            "target_calories": 2700,
            "macros": {
                "protein_g": 180,
                "carbs_g": 350,
                "fats_g": 63
            }
        }
    """
```

#### `parse_food_description()` 解析自然语言饮食
```python
async def parse_food_description(description: str) -> Dict:
    """
    解析自然语言食物描述

    示例输入: "我中午吃了150克鸡胸肉和一个苹果"

    输出: {
        "foods": [
            {
                "name": "鸡胸肉",
                "amount_g": 150,
                "calories": 165,
                "protein_g": 31,
                "carbs_g": 0,
                "fats_g": 3.6,
                "confidence": "high"
            },
            {
                "name": "苹果",
                "amount_g": 150,
                "calories": 78,
                ...
            }
        ],
        "total_macros": {...}
    }
    """
    # 使用 LLM 的自然语言理解能力
    # 识别食物种类、估算份量、计算营养
```

---

### 4. 进度分析 Agent (`backend/app/agents/progress_analyzer.py`)

**作用**: 分析训练和身体数据，检测平台期，提供调整建议

**核心方法**:

#### `analyze_training_progress()` 分析训练进度
```python
async def analyze_training_progress(
    workout_history: List[Dict],
    user_goal: str
) -> Dict:
    """
    分析训练数据，识别进步模式和问题

    分析维度：
    1. 训练一致性（完成率）
    2. 力量进步趋势
    3. 平台期检测
    4. 训练量分析

    Returns:
        {
            "consistency_score": 85,  # 0-100
            "strength_progress": {
                "trend": "improving",
                "key_lifts": [
                    {
                        "exercise": "卧推",
                        "initial_weight": 80,
                        "current_weight": 85,
                        "improvement_percentage": 6.25
                    }
                ]
            },
            "plateau_detected": false,
            "recommendations": [...]
        }
    """
```

#### `generate_weekly_report()` 生成周报
```python
async def generate_weekly_report(week_data: Dict) -> Dict:
    """
    生成全面的周健身报告

    包含：
    - 训练完成情况统计
    - 营养摄入分析
    - 身体指标变化
    - 本周亮点和成就
    - 需要改进的地方
    - 下周建议
    """
```

---

## 🌐 API 端点说明

### 1. 聊天 API (`backend/app/api/chat.py`)

**路由前缀**: `/api/chat`

#### `POST /message` 发送消息
```python
@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    发送消息给 AI 助手

    请求体:
    {
        "message": "我想制定训练计划",
        "conversation_id": "uuid",  # 可选
        "include_history": true
    }

    响应:
    {
        "message": "AI 的回复...",
        "conversation_id": "uuid",
        "intent": "workout_plan",  # 识别的意图
        "metadata": {}
    }

    流程:
    1. 获取或创建 conversation_id
    2. 加载对话历史
    3. 调用 FitnessAgent.chat()
    4. 保存消息记录
    5. 分析用户意图
    6. 返回响应
    """
```

---

### 2. 训练 API (`backend/app/api/workouts.py`)

**路由前缀**: `/api/workouts`

#### `POST /plan/generate` 生成训练计划
```python
@router.post("/plan/generate")
async def generate_workout_plan(db: AsyncSession = Depends(get_db)):
    """
    为当前用户生成个性化训练计划

    流程:
    1. 获取当前用户信息（TODO: 从认证中获取）
    2. 构建用户画像
    3. 调用 WorkoutPlannerAgent.generate_workout_plan()
    4. 保存计划到数据库
    5. 返回生成的计划
    """
```

---

### 3. 营养 API (`backend/app/api/nutrition.py`)

**路由前缀**: `/api/nutrition`

#### `POST /meal/parse` 解析饮食记录
```python
@router.post("/meal/parse")
async def parse_meal_description(description: str):
    """
    解析自然语言饮食描述

    示例:
    输入: "我中午吃了150克鸡胸肉"
    输出: {
        "foods": [{...营养数据...}],
        "total_macros": {...}
    }

    应用场景:
    - 用户无需手动查找食物数据库
    - 快速记录饮食
    - 自动计算营养摄入
    """
```

---

## 📊 数据库模型说明

### 1. 用户模型 (`backend/app/models/user.py`)

**表名**: `users`

**核心字段**:
```python
class User(Base):
    # 账户信息
    id: int                    # 主键
    email: str                 # 邮箱（唯一）
    username: str              # 用户名（唯一）
    hashed_password: str       # 密码哈希

    # 身体数据
    age: int                   # 年龄
    gender: str                # 性别
    height: float              # 身高 (cm)
    weight: float              # 体重 (kg)
    body_fat_percentage: float # 体脂率 (%)

    # 健身画像
    fitness_goal: FitnessGoal  # 健身目标枚举
    experience_level: ExperienceLevel  # 经验水平
    training_frequency: int    # 训练频率（每周）
    equipment_access: EquipmentAccess  # 器械条件

    # 目标
    target_weight: float       # 目标体重
    target_body_fat: float     # 目标体脂
    goal_timeframe: int        # 目标时间框架（周）

    # 关系
    workout_plans: List[WorkoutPlan]
    nutrition_plans: List[NutritionPlan]
    progress_logs: List[ProgressLog]
```

---

### 2. 训练计划模型 (`backend/app/models/workout.py`)

**主要表**:

#### `WorkoutPlan` 训练计划
```python
class WorkoutPlan(Base):
    # 基本信息
    name: str                  # 计划名称
    workout_type: WorkoutType  # 训练类型（推拉腿/上下肢等）
    frequency_per_week: int    # 每周频率
    duration_weeks: int        # 持续周数

    # AI 生成信息
    generation_prompt: str     # 生成时使用的 prompt
    ai_rationale: str          # AI 的解释理由

    # 关系
    user: User
    workout_sessions: List[WorkoutSession]
```

#### `WorkoutSession` 训练会话
```python
class WorkoutSession(Base):
    # 会话信息
    name: str                  # 会话名称（如"推日"）
    day_of_week: int          # 星期几 (0-6)
    target_muscle_groups: str  # 目标肌群（JSON）

    # 状态
    completed: bool            # 是否完成
    scheduled_date: datetime   # 计划日期
    completed_date: datetime   # 实际完成日期

    # 关系
    exercises: List[WorkoutExercise]
```

#### `WorkoutExercise` 训练动作
```python
class WorkoutExercise(Base):
    # 处方（计划）
    sets: int                  # 组数
    reps: int                  # 次数
    weight: float              # 重量 (kg)
    rest_seconds: int          # 休息时间 (秒)

    # 实际表现
    actual_sets: int           # 实际完成组数
    actual_reps: int           # 实际完成次数
    actual_weight: float       # 实际使用重量
    completed: bool            # 是否完成

    # 关系
    exercise: Exercise         # 关联到动作库
    workout_session: WorkoutSession
```

---

## 📱 前端架构说明

### 1. 主应用 (`frontend/src/App.jsx`)

**作用**: 应用的根组件，配置路由

```jsx
function App() {
  return (
    <Routes>
      {/* 主布局：包含侧边栏 */}
      <Route path="/" element={<Layout />}>
        {/* 默认路由：聊天页面 */}
        <Route index element={<ChatPage />} />

        {/* 其他页面 */}
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="workout" element={<WorkoutPage />} />
        <Route path="nutrition" element={<NutritionPage />} />
        <Route path="progress" element={<ProgressPage />} />
      </Route>
    </Routes>
  )
}
```

**路由说明**:
- `/`: 聊天助手页面（默认）
- `/dashboard`: 仪表盘（概览）
- `/workout`: 训练计划页面
- `/nutrition`: 营养追踪页面
- `/progress`: 进度分析页面

---

### 2. 聊天页面 (`frontend/src/pages/ChatPage.jsx`)

**作用**: 提供与 AI 助手的对话界面

**核心状态**:
```jsx
const [messages, setMessages] = useState([])  // 消息列表
const [input, setInput] = useState('')        // 输入框内容
const [conversationId, setConversationId] = useState(null)  // 对话ID
```

**核心功能**:

#### 发送消息
```jsx
const sendMessageMutation = useMutation({
  mutationFn: async (message) => {
    // 调用后端 API
    const response = await axios.post('/api/chat/message', {
      message,
      conversation_id: conversationId,
      include_history: true,
    })
    return response.data
  },
  onSuccess: (data) => {
    // 更新 conversation_id
    setConversationId(data.conversation_id)

    // 添加 AI 回复到消息列表
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: data.message,
      intent: data.intent
    }])
  }
})
```

#### 处理表单提交
```jsx
const handleSubmit = (e) => {
  e.preventDefault()
  if (!input.trim()) return

  // 添加用户消息到列表
  setMessages(prev => [...prev, {
    role: 'user',
    content: input
  }])

  // 发送到服务器
  sendMessageMutation.mutate(input)

  // 清空输入框
  setInput('')
}
```

**UI 组件**:
- 消息列表：显示历史对话
- 输入框：用户输入消息
- 发送按钮：提交消息
- 快速操作：预设的常用问题

---

### 3. 布局组件 (`frontend/src/components/Layout.jsx`)

**作用**: 提供整体布局框架（侧边栏 + 主内容区）

```jsx
function Layout() {
  const location = useLocation()

  return (
    <div className="app-container">
      {/* 侧边栏导航 */}
      <nav className="sidebar">
        <div className="sidebar-header">
          <h1>💪 Fitness Planner</h1>
        </div>

        {/* 导航菜单 */}
        <ul className="nav-menu">
          {navigation.map(item => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
              >
                {item.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* 主内容区 */}
      <main className="main-content">
        <Outlet />  {/* 子路由渲染位置 */}
      </main>
    </div>
  )
}
```

---

## 🎨 样式设计说明

### CSS 变量系统 (`frontend/src/styles/index.css`)

**颜色主题**:
```css
:root {
  --primary-color: #4f46e5;     /* 主色调（紫色） */
  --secondary-color: #10b981;   /* 辅助色（绿色） */
  --background: #f9fafb;        /* 背景色 */
  --surface: #ffffff;           /* 表面色（卡片） */
  --text-primary: #111827;      /* 主要文字 */
  --text-secondary: #6b7280;    /* 次要文字 */
  --border: #e5e7eb;            /* 边框色 */
  --error: #ef4444;             /* 错误色 */
  --success: #10b981;           /* 成功色 */
}
```

---

## 🔧 开发最佳实践

### 1. 添加新的 Agent

1. 在 `backend/app/agents/` 创建新文件
2. 继承基础配置，初始化 LLM
3. 实现核心处理方法
4. 在 API 路由中集成

### 2. 添加新的 API 端点

1. 在相应的 `backend/app/api/` 文件中添加路由
2. 使用 `@router.post/get/put/delete` 装饰器
3. 添加类型注解和文档字符串
4. 使用依赖注入获取数据库会话

### 3. 前端数据获取

使用 TanStack Query (React Query) 进行数据获取：

```jsx
const { data, isLoading, error } = useQuery({
  queryKey: ['workouts'],
  queryFn: async () => {
    const res = await axios.get('/api/workouts/plan/current')
    return res.data
  }
})
```

### 4. 错误处理

后端:
```python
try:
    # 业务逻辑
    result = await some_operation()
    return {"success": True, "data": result}
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

前端:
```jsx
if (error) {
  return <div>错误：{error.message}</div>
}
```

---

## 📚 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [LangChain 文档](https://python.langchain.com/)
- [React Query 文档](https://tanstack.com/query/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

---

**最后更新**: 2024-11-17
