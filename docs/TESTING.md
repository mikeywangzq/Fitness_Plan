# 测试文档

Fitness Planner Agent 的测试指南和示例。

## 📋 目录

- [测试环境设置](#测试环境设置)
- [单元测试](#单元测试)
- [集成测试](#集成测试)
- [API 测试](#api-测试)
- [LLM Agent 测试](#llm-agent-测试)
- [前端测试](#前端测试)
- [性能测试](#性能测试)
- [测试最佳实践](#测试最佳实践)

---

## 测试环境设置

### 安装测试依赖

\`\`\`bash
cd backend

# 安装测试依赖
pip install pytest pytest-asyncio pytest-cov httpx faker

# 或从 requirements.txt 安装（已包含）
pip install -r requirements.txt
\`\`\`

### 配置测试环境

\`\`\`bash
# 创建测试环境变量
cp .env.example .env.test

# 修改测试配置
nano .env.test
\`\`\`

**测试环境配置**:
\`\`\`bash
ENVIRONMENT=testing
DEBUG=True
DATABASE_URL=postgresql+asyncpg://test_user:test_pass@localhost:5432/fitness_planner_test
OPENAI_API_KEY=sk-test-key  # 可以使用模拟的 key
\`\`\`

### 创建测试数据库

\`\`\`bash
# 使用 Docker 启动测试数据库
docker run -d \
  --name test_postgres \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_pass \
  -e POSTGRES_DB=fitness_planner_test \
  -p 5433:5432 \
  postgres:15-alpine
\`\`\`

---

## 单元测试

### 测试数据库模型

**文件**: `backend/tests/test_models.py`

\`\`\`python
"""
测试数据库模型
"""
import pytest
from app.models.user import User, FitnessGoal, ExperienceLevel
from app.models.workout import WorkoutPlan, Exercise


class TestUserModel:
    """用户模型测试"""

    def test_create_user(self):
        """测试创建用户"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            age=25,
            weight=75.0,
            height=175.0,
            fitness_goal=FitnessGoal.MUSCLE_GAIN,
            experience_level=ExperienceLevel.INTERMEDIATE,
            training_frequency=5
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.fitness_goal == FitnessGoal.MUSCLE_GAIN
        assert user.training_frequency == 5

    def test_user_validation(self):
        """测试用户数据验证"""
        # 测试必填字段
        with pytest.raises(ValueError):
            User(username="test")  # 缺少 email

        # 测试数据类型
        with pytest.raises(ValueError):
            User(
                email="test@example.com",
                username="test",
                age="twenty"  # 错误的类型
            )


class TestWorkoutModel:
    """训练模型测试"""

    def test_create_workout_plan(self):
        """测试创建训练计划"""
        plan = WorkoutPlan(
            user_id=1,
            name="5天增肌计划",
            workout_type="push_pull_legs",
            frequency_per_week=5,
            duration_weeks=12
        )

        assert plan.name == "5天增肌计划"
        assert plan.frequency_per_week == 5

    def test_create_exercise(self):
        """测试创建动作"""
        exercise = Exercise(
            name="杠铃卧推",
            muscle_group="chest",
            exercise_type="compound",
            difficulty_level=3
        )

        assert exercise.name == "杠铃卧推"
        assert exercise.muscle_group == "chest"
\`\`\`

### 测试工具函数

**文件**: `backend/tests/test_utils.py`

\`\`\`python
"""
测试工具函数
"""
import pytest
from app.utils.calculations import calculate_bmr, calculate_tdee, calculate_macros


class TestNutritionCalculations:
    """营养计算测试"""

    def test_calculate_bmr_male(self):
        """测试男性 BMR 计算"""
        # Mifflin-St Jeor 公式
        bmr = calculate_bmr(
            weight=75,  # kg
            height=175,  # cm
            age=25,
            gender="male"
        )

        # 预期: 10 * 75 + 6.25 * 175 - 5 * 25 + 5 = 1718.75
        assert abs(bmr - 1718.75) < 1

    def test_calculate_bmr_female(self):
        """测试女性 BMR 计算"""
        bmr = calculate_bmr(
            weight=60,
            height=165,
            age=30,
            gender="female"
        )

        # 预期: 10 * 60 + 6.25 * 165 - 5 * 30 - 161 = 1370.25
        assert abs(bmr - 1370.25) < 1

    def test_calculate_tdee(self):
        """测试 TDEE 计算"""
        bmr = 1700
        activity_level = 1.55  # 中等活动

        tdee = calculate_tdee(bmr, activity_level)

        assert tdee == bmr * activity_level
        assert tdee == 2635

    def test_calculate_macros_muscle_gain(self):
        """测试增肌宏量计算"""
        tdee = 2500
        goal = "muscle_gain"

        macros = calculate_macros(tdee, goal)

        # 增肌：热量盈余 +300-500
        assert macros['calories'] > tdee
        assert macros['calories'] <= tdee + 500

        # 蛋白质：2.0-2.2g per kg
        # 碳水：较高
        # 脂肪：适中
        assert 'protein_g' in macros
        assert 'carbs_g' in macros
        assert 'fats_g' in macros


class TestWorkoutCalculations:
    """训练计算测试"""

    def test_calculate_1rm(self):
        """测试计算 1RM（最大单次重量）"""
        from app.utils.calculations import calculate_1rm

        # Epley 公式: 1RM = weight * (1 + reps/30)
        one_rm = calculate_1rm(weight=80, reps=5)

        expected = 80 * (1 + 5/30)
        assert abs(one_rm - expected) < 0.1

    def test_calculate_training_volume(self):
        """测试计算训练量"""
        from app.utils.calculations import calculate_training_volume

        volume = calculate_training_volume(
            weight=100,
            sets=4,
            reps=8
        )

        assert volume == 100 * 4 * 8
        assert volume == 3200
\`\`\`

### 运行单元测试

\`\`\`bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_models.py

# 运行特定测试类
pytest tests/test_models.py::TestUserModel

# 运行特定测试方法
pytest tests/test_models.py::TestUserModel::test_create_user

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s

# 生成覆盖率报告
pytest --cov=app --cov-report=html
\`\`\`

---

## 集成测试

### 测试 API 端点

**文件**: `backend/tests/test_api.py`

\`\`\`python
"""
API 集成测试
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
async def client():
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestChatAPI:
    """聊天 API 测试"""

    @pytest.mark.asyncio
    async def test_send_message(self, client):
        """测试发送消息"""
        response = await client.post("/api/chat/message", json={
            "message": "我想制定训练计划",
            "include_history": True
        })

        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "conversation_id" in data
        assert data["message"] != ""

    @pytest.mark.asyncio
    async def test_send_empty_message(self, client):
        """测试发送空消息"""
        response = await client.post("/api/chat/message", json={
            "message": "",
            "include_history": True
        })

        # 应该返回验证错误
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_conversation_history(self, client):
        """测试对话历史"""
        # 发送第一条消息
        response1 = await client.post("/api/chat/message", json={
            "message": "你好",
            "include_history": True
        })

        conversation_id = response1.json()["conversation_id"]

        # 发送第二条消息
        response2 = await client.post("/api/chat/message", json={
            "message": "我想增肌",
            "conversation_id": conversation_id,
            "include_history": True
        })

        assert response2.status_code == 200

        # 获取对话历史
        response3 = await client.get(f"/api/chat/conversation/{conversation_id}")

        assert response3.status_code == 200
        history = response3.json()

        assert len(history["messages"]) >= 2


class TestWorkoutAPI:
    """训练 API 测试"""

    @pytest.mark.asyncio
    async def test_generate_workout_plan(self, client):
        """测试生成训练计划"""
        response = await client.post("/api/workouts/plan/generate")

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "plan" in data

        plan = data["plan"]
        assert "plan_name" in plan
        assert "weekly_schedule" in plan
        assert len(plan["weekly_schedule"]) > 0

    @pytest.mark.asyncio
    async def test_suggest_workout_split(self, client):
        """测试训练分化建议"""
        response = await client.post("/api/workouts/split/suggest", json={
            "frequency": 5,
            "goal": "muscle_gain",
            "experience": "intermediate"
        })

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "suggestion" in data


class TestNutritionAPI:
    """营养 API 测试"""

    @pytest.mark.asyncio
    async def test_generate_nutrition_plan(self, client):
        """测试生成营养计划"""
        response = await client.post("/api/nutrition/plan/generate")

        assert response.status_code == 200

        data = response.json()
        assert "macro_plan" in data

        macros = data["macro_plan"]["macros"]
        assert "protein_g" in macros
        assert "carbs_g" in macros
        assert "fats_g" in macros

    @pytest.mark.asyncio
    async def test_parse_meal(self, client):
        """测试解析饮食描述"""
        response = await client.post(
            "/api/nutrition/meal/parse",
            params={"description": "我吃了150克鸡胸肉和一个苹果"}
        )

        assert response.status_code == 200

        data = response.json()
        assert "parsed_data" in data
        assert "foods" in data["parsed_data"]
        assert len(data["parsed_data"]["foods"]) >= 2
\`\`\`

---

## API 测试

### 使用 pytest + httpx

**运行 API 测试**:
\`\`\`bash
# 运行所有 API 测试
pytest tests/test_api.py -v

# 运行特定测试类
pytest tests/test_api.py::TestChatAPI -v
\`\`\`

### 使用 Postman 测试

**Postman 集合示例**:
\`\`\`json
{
  "info": {
    "name": "Fitness Planner API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        }
      }
    },
    {
      "name": "Send Chat Message",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"message\": \"我想制定训练计划\",\n  \"include_history\": true\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/chat/message",
          "host": ["{{base_url}}"],
          "path": ["api", "chat", "message"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
\`\`\`

### 使用 cURL 测试

\`\`\`bash
# 健康检查
curl http://localhost:8000/health

# 发送聊天消息
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想制定训练计划",
    "include_history": true
  }'

# 生成训练计划
curl -X POST http://localhost:8000/api/workouts/plan/generate

# 解析饮食
curl -X POST "http://localhost:8000/api/nutrition/meal/parse?description=我吃了鸡胸肉"
\`\`\`

---

## LLM Agent 测试

### Mock LLM 响应

**文件**: `backend/tests/test_agents.py`

\`\`\`python
"""
测试 LLM Agents
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.agents.fitness_agent import FitnessAgent
from app.agents.workout_planner import WorkoutPlannerAgent


class TestFitnessAgent:
    """测试主 Agent"""

    @pytest.mark.asyncio
    @patch('app.agents.fitness_agent.ChatOpenAI')
    async def test_chat(self, mock_llm):
        """测试聊天功能"""
        # Mock LLM 响应
        mock_instance = AsyncMock()
        mock_instance.apredict.return_value = "我可以帮你制定训练计划"
        mock_llm.return_value = mock_instance

        agent = FitnessAgent()
        response = await agent.chat(
            message="我想健身",
            user_context={"fitness_goal": "muscle_gain"}
        )

        assert response == "我可以帮你制定训练计划"
        mock_instance.apredict.assert_called_once()

    def test_build_context(self):
        """测试构建上下文"""
        agent = FitnessAgent()

        context = agent._build_context({
            "fitness_goal": "muscle_gain",
            "training_frequency": 5,
            "experience_level": "intermediate"
        })

        assert "增肌" in context
        assert "5" in context
        assert "中级" in context


class TestWorkoutPlannerAgent:
    """测试训练计划 Agent"""

    @pytest.mark.asyncio
    @patch('app.agents.workout_planner.ChatOpenAI')
    async def test_generate_workout_plan(self, mock_llm):
        """测试生成训练计划"""
        # Mock LLM 响应
        mock_response = '''
        ```json
        {
          "plan_name": "5天增肌计划",
          "workout_type": "push_pull_legs",
          "frequency_per_week": 5,
          "weekly_schedule": []
        }
        ```
        '''

        mock_instance = AsyncMock()
        mock_instance.apredict.return_value = mock_response
        mock_llm.return_value = mock_instance

        agent = WorkoutPlannerAgent()
        plan = await agent.generate_workout_plan({
            "fitness_goal": "muscle_gain",
            "training_frequency": 5
        })

        assert plan["plan_name"] == "5天增肌计划"
        assert plan["workout_type"] == "push_pull_legs"
\`\`\`

### 运行 Agent 测试

\`\`\`bash
# 运行 Agent 测试
pytest tests/test_agents.py -v

# 使用 mock，不实际调用 OpenAI API
pytest tests/test_agents.py -v --mock-llm
\`\`\`

---

## 前端测试

### 使用 Jest + React Testing Library

**安装依赖**:
\`\`\`bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest
\`\`\`

**测试示例**: `frontend/src/components/__tests__/ChatPage.test.jsx`

\`\`\`javascript
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ChatPage from '../pages/ChatPage'

const queryClient = new QueryClient()

describe('ChatPage', () => {
  it('renders chat interface', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <ChatPage />
      </QueryClientProvider>
    )

    expect(screen.getByPlaceholderText(/输入你的问题/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /发送/i })).toBeInTheDocument()
  })

  it('sends message when form is submitted', async () => {
    const user = userEvent.setup()

    render(
      <QueryClientProvider client={queryClient}>
        <ChatPage />
      </QueryClientProvider>
    )

    const input = screen.getByPlaceholderText(/输入你的问题/i)
    const sendButton = screen.getByRole('button', { name: /发送/i })

    // 输入消息
    await user.type(input, '我想制定训练计划')

    // 点击发送
    await user.click(sendButton)

    // 验证消息出现
    await waitFor(() => {
      expect(screen.getByText(/我想制定训练计划/i)).toBeInTheDocument()
    })
  })
})
\`\`\`

**运行前端测试**:
\`\`\`bash
cd frontend
npm test
\`\`\`

---

## 性能测试

### 使用 Locust 进行负载测试

**安装 Locust**:
\`\`\`bash
pip install locust
\`\`\`

**创建测试脚本**: `backend/tests/locustfile.py`

\`\`\`python
"""
Locust 性能测试
"""
from locust import HttpUser, task, between


class FitnessPlannerUser(HttpUser):
    """模拟用户行为"""

    wait_time = between(1, 3)  # 请求间隔 1-3 秒

    @task(3)
    def health_check(self):
        """健康检查（高频）"""
        self.client.get("/health")

    @task(2)
    def send_chat_message(self):
        """发送聊天消息（中频）"""
        self.client.post("/api/chat/message", json={
            "message": "我想制定训练计划",
            "include_history": True
        })

    @task(1)
    def generate_workout_plan(self):
        """生成训练计划（低频）"""
        self.client.post("/api/workouts/plan/generate")
\`\`\`

**运行性能测试**:
\`\`\`bash
# 启动 Locust
locust -f backend/tests/locustfile.py --host=http://localhost:8000

# 访问 Web UI
open http://localhost:8089

# 命令行模式（无 UI）
locust -f backend/tests/locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 1m --headless
\`\`\`

---

## 测试最佳实践

### 1. 测试组织

\`\`\`
tests/
├── __init__.py
├── conftest.py          # pytest 配置和 fixtures
├── test_models.py       # 模型测试
├── test_utils.py        # 工具函数测试
├── test_api.py          # API 集成测试
├── test_agents.py       # Agent 测试
└── locustfile.py        # 性能测试
\`\`\`

### 2. 使用 Fixtures

**conftest.py**:
\`\`\`python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.database import Base


@pytest.fixture
async def test_db():
    """创建测试数据库"""
    engine = create_async_engine(
        "postgresql+asyncpg://test_user:test_pass@localhost:5433/test_db"
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_session(test_db):
    """创建测试会话"""
    async with AsyncSession(test_db) as session:
        yield session
\`\`\`

### 3. 测试覆盖率目标

- **单元测试**: 覆盖率 > 80%
- **集成测试**: 关键 API 端点 100% 覆盖
- **边界情况**: 测试异常和边界条件

### 4. 持续集成

**GitHub Actions 示例**: `.github/workflows/test.yml`

\`\`\`yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
\`\`\`

---

## 测试清单

开发新功能时的测试清单：

- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] 测试正常情况
- [ ] 测试异常情况
- [ ] 测试边界条件
- [ ] 检查测试覆盖率
- [ ] 运行所有测试确保通过
- [ ] 更新 API 文档

---

**最后更新**: 2024-11-17
