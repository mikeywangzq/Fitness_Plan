# API 使用指南

本文档提供 Fitness Planner Agent API 的详细使用说明和示例代码。

## 📋 目录

- [基础配置](#基础配置)
- [认证说明](#认证说明)
- [聊天 API](#聊天-api)
- [用户 API](#用户-api)
- [训练计划 API](#训练计划-api)
- [营养追踪 API](#营养追踪-api)
- [进度分析 API](#进度分析-api)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)

---

## 基础配置

### API 基础地址

```
开发环境: http://localhost:8000
生产环境: https://your-domain.com
```

### 请求头设置

```http
Content-Type: application/json
Accept: application/json
```

### Python 客户端示例

```python
import requests

# 配置基础 URL
BASE_URL = "http://localhost:8000/api"

# 创建会话（可选，用于保持连接）
session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json"
})
```

### JavaScript 客户端示例

```javascript
// 使用 Axios
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})
```

---

## 认证说明

> ⚠️ **注意**: V1.0 版本暂未实现完整的用户认证系统。认证功能将在 V1.1 版本中提供。

未来将支持的认证方式：

```http
Authorization: Bearer <access_token>
```

---

## 聊天 API

### 1. 发送消息给 AI 助手

**端点**: `POST /chat/message`

**描述**: 向 AI 助手发送消息并获取回复

**请求体**:
```json
{
  "message": "我想制定一个一周五次的增肌训练计划",
  "conversation_id": "optional-uuid",
  "include_history": true
}
```

**响应**:
```json
{
  "message": "好的！我很乐意帮你制定一个一周五次的增肌训练计划...",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "intent": "workout_plan",
  "metadata": {
    "detected_goal": "muscle_gain",
    "detected_frequency": 5
  }
}
```

**Python 示例**:
```python
def send_chat_message(message: str, conversation_id: str = None):
    """发送聊天消息"""
    url = f"{BASE_URL}/chat/message"
    payload = {
        "message": message,
        "conversation_id": conversation_id,
        "include_history": True
    }

    response = session.post(url, json=payload)
    response.raise_for_status()

    data = response.json()
    return data

# 使用示例
result = send_chat_message("我想制定训练计划")
print(f"AI 回复: {result['message']}")
print(f"对话ID: {result['conversation_id']}")
```

**JavaScript 示例**:
```javascript
async function sendMessage(message, conversationId = null) {
  try {
    const response = await apiClient.post('/chat/message', {
      message,
      conversation_id: conversationId,
      include_history: true
    })

    console.log('AI 回复:', response.data.message)
    console.log('对话ID:', response.data.conversation_id)

    return response.data
  } catch (error) {
    console.error('发送消息失败:', error.response?.data)
    throw error
  }
}

// 使用示例
const result = await sendMessage('我想制定训练计划')
```

**cURL 示例**:
```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想制定训练计划",
    "include_history": true
  }'
```

### 2. 用户引导对话

**端点**: `POST /chat/onboarding`

**描述**: 专门用于新用户引导的对话端点

**请求体**:
```json
{
  "message": "我刚开始健身，不知道从哪里开始",
  "conversation_id": "optional-uuid",
  "include_history": true
}
```

**响应**:
```json
{
  "message": "欢迎开始健身之旅！让我来帮你...",
  "onboarding_complete": false,
  "user_profile": null,
  "next_steps": [
    "告诉我你的健身目标",
    "分享你的身体数据"
  ]
}
```

### 3. 获取对话历史

**端点**: `GET /chat/conversation/{conversation_id}`

**描述**: 获取指定对话的历史记录

**响应**:
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "user",
      "content": "我想制定训练计划"
    },
    {
      "role": "assistant",
      "content": "好的！让我帮你..."
    }
  ]
}
```

**Python 示例**:
```python
def get_conversation_history(conversation_id: str):
    """获取对话历史"""
    url = f"{BASE_URL}/chat/conversation/{conversation_id}"
    response = session.get(url)
    response.raise_for_status()
    return response.json()
```

### 4. 清除对话历史

**端点**: `DELETE /chat/conversation/{conversation_id}`

**描述**: 删除指定对话的历史记录

---

## 训练计划 API

### 1. 生成训练计划

**端点**: `POST /workouts/plan/generate`

**描述**: 为当前用户生成个性化训练计划

**响应**:
```json
{
  "success": true,
  "plan": {
    "plan_name": "5天增肌训练计划（推拉腿）",
    "workout_type": "push_pull_legs",
    "frequency_per_week": 5,
    "duration_weeks": 12,
    "weekly_schedule": [
      {
        "day": 1,
        "name": "推（胸+肩+三头）",
        "target_muscles": ["chest", "shoulders", "triceps"],
        "exercises": [
          {
            "name": "杠铃卧推",
            "sets": 4,
            "reps": 8,
            "rest_seconds": 90,
            "notes": "保持肩胛骨后缩，下放至胸部轻触"
          },
          {
            "name": "上斜哑铃推举",
            "sets": 3,
            "reps": 10,
            "rest_seconds": 60,
            "notes": "角度30-45度，注意肩部稳定"
          },
          {
            "name": "坐姿推肩",
            "sets": 3,
            "reps": 12,
            "rest_seconds": 60,
            "notes": "核心收紧，避免过度后仰"
          }
        ]
      },
      {
        "day": 2,
        "name": "拉（背+二头）",
        "exercises": [...]
      }
    ],
    "rationale": "推拉腿分化适合一周训练5次的中高级训练者...",
    "progression_advice": "每周尝试增加2.5-5kg的负重..."
  },
  "message": "训练计划已生成"
}
```

**Python 完整示例**:
```python
def generate_workout_plan():
    """生成训练计划"""
    url = f"{BASE_URL}/workouts/plan/generate"

    response = session.post(url)
    response.raise_for_status()

    data = response.json()
    plan = data['plan']

    # 打印计划信息
    print(f"计划名称: {plan['plan_name']}")
    print(f"训练类型: {plan['workout_type']}")
    print(f"训练频率: 每周{plan['frequency_per_week']}次")
    print(f"\n周计划:")

    for session in plan['weekly_schedule']:
        print(f"\n第{session['day']}天 - {session['name']}")
        for exercise in session['exercises']:
            print(f"  • {exercise['name']}: {exercise['sets']}组 x {exercise['reps']}次")

    return plan

# 使用示例
plan = generate_workout_plan()
```

### 2. 建议训练分化方式

**端点**: `POST /workouts/split/suggest`

**描述**: 根据训练频率和目标推荐最佳训练分化

**请求体**:
```json
{
  "frequency": 5,
  "goal": "muscle_gain",
  "experience": "intermediate"
}
```

**响应**:
```json
{
  "success": true,
  "suggestion": {
    "recommended_split": "推拉腿",
    "split_type": "push_pull_legs",
    "days_breakdown": [
      "周一：推（胸+肩+三头）",
      "周二：拉（背+二头）",
      "周三：腿（股四头+腘绳肌+臀）",
      "周四：推（胸+肩+三头）",
      "周五：拉（背+二头）",
      "周六/日：休息"
    ],
    "rationale": "推拉腿分化允许每个肌群每周训练2次...",
    "pros": [
      "每个肌群有充分的恢复时间",
      "训练强度和容量平衡",
      "适合中高级训练者"
    ],
    "cons": [
      "需要较高的训练频率",
      "不适合初学者"
    ]
  }
}
```

### 3. 记录训练会话

**端点**: `POST /workouts/session/log`

**描述**: 记录完成的训练会话

**请求体**:
```json
{
  "workout_plan_id": 1,
  "name": "推日训练",
  "completed_date": "2024-01-15T18:00:00Z",
  "exercises": [
    {
      "exercise_id": 1,
      "sets": 4,
      "reps": 8,
      "weight": 80,
      "completed": true,
      "notes": "感觉良好，下次可以加重"
    }
  ],
  "notes": "整体训练强度适中，状态不错"
}
```

---

## 营养追踪 API

### 1. 生成营养计划

**端点**: `POST /nutrition/plan/generate`

**描述**: 基于用户资料生成营养计划

**响应**:
```json
{
  "success": true,
  "macro_plan": {
    "bmr": 1650,
    "tdee": 2400,
    "target_calories": 2700,
    "calorie_adjustment": "+300 kcal (增肌盈余)",
    "macros": {
      "protein_g": 180,
      "carbs_g": 350,
      "fats_g": 63,
      "fiber_g": 30
    },
    "macro_percentages": {
      "protein": "27%",
      "carbs": "52%",
      "fats": "21%"
    },
    "rationale": "基于你的目标（增肌）和活动水平...",
    "meal_timing": "建议将碳水主要分配在训练前后"
  }
}
```

### 2. 生成每日饮食计划

**端点**: `POST /nutrition/meal-plan/generate`

**描述**: 生成具体的每日三餐计划

**请求体**:
```json
{
  "macro_targets": {
    "calories": 2700,
    "protein_g": 180,
    "carbs_g": 350,
    "fats_g": 63
  }
}
```

**响应**:
```json
{
  "success": true,
  "meal_plan": {
    "daily_plan": [
      {
        "meal_type": "早餐",
        "time": "08:00",
        "foods": [
          {
            "name": "燕麦",
            "amount": "100g",
            "calories": 389,
            "protein": 17,
            "carbs": 66,
            "fats": 7
          },
          {
            "name": "鸡蛋",
            "amount": "2个",
            "calories": 155,
            "protein": 13,
            "carbs": 1,
            "fats": 11
          },
          {
            "name": "香蕉",
            "amount": "1根",
            "calories": 105,
            "protein": 1,
            "carbs": 27,
            "fats": 0
          }
        ],
        "total_macros": {
          "calories": 649,
          "protein": 31,
          "carbs": 94,
          "fats": 18
        }
      }
    ],
    "daily_totals": {
      "calories": 2680,
      "protein": 178,
      "carbs": 352,
      "fats": 61
    },
    "meal_prep_tips": "可以提前准备燕麦和鸡肉...",
    "hydration_reminder": "每天至少喝2-3升水"
  }
}
```

### 3. 解析自然语言饮食记录

**端点**: `POST /nutrition/meal/parse`

**描述**: 解析自然语言描述的饮食

**请求参数**:
```json
{
  "description": "我中午吃了150克鸡胸肉、200克米饭和一个苹果"
}
```

**响应**:
```json
{
  "success": true,
  "parsed_data": {
    "foods": [
      {
        "name": "鸡胸肉",
        "amount_g": 150,
        "amount_description": "150克",
        "calories": 165,
        "protein_g": 31,
        "carbs_g": 0,
        "fats_g": 3.6,
        "confidence": "high"
      },
      {
        "name": "米饭",
        "amount_g": 200,
        "amount_description": "200克",
        "calories": 260,
        "protein_g": 5,
        "carbs_g": 58,
        "fats_g": 0.4,
        "confidence": "high"
      },
      {
        "name": "苹果",
        "amount_g": 150,
        "amount_description": "1个（中等大小）",
        "calories": 78,
        "protein_g": 0.4,
        "carbs_g": 21,
        "fats_g": 0.2,
        "confidence": "medium"
      }
    ],
    "total_macros": {
      "calories": 503,
      "protein_g": 36.4,
      "carbs_g": 79,
      "fats_g": 4.2
    },
    "notes": "所有食物都已成功识别，营养数据为估算值"
  }
}
```

**Python 使用示例**:
```python
def log_meal_natural_language(description: str):
    """使用自然语言记录饮食"""
    url = f"{BASE_URL}/nutrition/meal/parse"

    # 解析食物描述
    response = session.post(url, params={"description": description})
    response.raise_for_status()

    parsed = response.json()['parsed_data']

    # 显示识别结果
    print("识别的食物:")
    for food in parsed['foods']:
        print(f"  • {food['name']} {food['amount_description']}")
        print(f"    热量: {food['calories']} kcal, 蛋白质: {food['protein_g']}g")

    print(f"\n总计: {parsed['total_macros']['calories']} kcal")

    return parsed

# 使用示例
meal = log_meal_natural_language("我早上吃了2个鸡蛋和一碗燕麦")
```

### 4. 分析每日饮食

**端点**: `POST /nutrition/meals/analyze`

**描述**: 分析当日饮食摄入并提供反馈

**请求体**:
```json
{
  "meals": [
    {
      "meal_type": "breakfast",
      "calories": 649,
      "protein_g": 31,
      "carbs_g": 94,
      "fats_g": 18
    },
    {
      "meal_type": "lunch",
      "calories": 503,
      "protein_g": 36,
      "carbs_g": 79,
      "fats_g": 4
    }
  ],
  "target_macros": {
    "calories": 2700,
    "protein_g": 180,
    "carbs_g": 350,
    "fats_g": 63
  }
}
```

**响应**:
```json
{
  "success": true,
  "analysis": {
    "current_status": {
      "calories": {
        "consumed": 1152,
        "remaining": 1548,
        "percentage": 43
      },
      "protein": {
        "consumed": 67,
        "remaining": 113,
        "percentage": 37
      },
      "carbs": {
        "consumed": 173,
        "remaining": 177,
        "percentage": 49
      },
      "fats": {
        "consumed": 22,
        "remaining": 41,
        "percentage": 35
      }
    },
    "feedback": "当前蛋白质摄入略低于目标进度，建议在晚餐增加高蛋白食物",
    "recommendations": [
      "晚餐建议摄入约 1550 kcal",
      "重点补充蛋白质：还需 113g",
      "可选择：200g鸡胸肉 + 250g米饭 + 蔬菜"
    ],
    "suggested_foods": [
      "鸡胸肉 200g (蛋白质 46g)",
      "鲑鱼 150g (蛋白质 31g)",
      "希腊酸奶 200g (蛋白质 20g)"
    ]
  }
}
```

---

## 进度分析 API

### 1. 记录身体数据

**端点**: `POST /progress/body-metrics`

**描述**: 记录身体测量数据

**请求体**:
```json
{
  "weight": 76.5,
  "body_fat_percentage": 15.2,
  "muscle_mass": 65.0,
  "chest": 102,
  "waist": 82,
  "bicep_right": 38,
  "measured_at": "2024-01-15T08:00:00Z",
  "notes": "早晨空腹测量"
}
```

### 2. 分析训练进度

**端点**: `POST /progress/analyze/training`

**描述**: 分析训练进度并提供建议

**响应**:
```json
{
  "success": true,
  "analysis": {
    "consistency_score": 95,
    "consistency_analysis": "过去4周保持了优秀的训练一致性",
    "strength_progress": {
      "trend": "improving",
      "key_lifts": [
        {
          "exercise": "卧推",
          "initial_weight": 80,
          "current_weight": 87.5,
          "improvement_percentage": 9.4,
          "trend": "上升"
        },
        {
          "exercise": "深蹲",
          "initial_weight": 100,
          "current_weight": 110,
          "improvement_percentage": 10.0,
          "trend": "上升"
        },
        {
          "exercise": "硬拉",
          "initial_weight": 120,
          "current_weight": 120,
          "improvement_percentage": 0,
          "trend": "平台期"
        }
      ]
    },
    "plateau_detected": true,
    "plateau_analysis": "硬拉已3周未进步，可能遇到平台期",
    "recommendations": [
      {
        "category": "训练",
        "recommendation": "硬拉尝试相扑式变化或增加辅助训练",
        "priority": "high",
        "rationale": "打破平台期需要训练变化"
      },
      {
        "category": "营养",
        "recommendation": "确保训练日热量盈余达到+300-500 kcal",
        "priority": "medium",
        "rationale": "支持力量增长需要足够能量"
      }
    ],
    "overall_assessment": "整体进步良好，需关注硬拉平台期",
    "motivation_message": "你的努力正在得到回报！继续保持！💪"
  }
}
```

### 3. 生成周报

**端点**: `POST /progress/report/weekly`

**描述**: 生成本周健身报告

**响应**:
```json
{
  "success": true,
  "report": {
    "week_number": 4,
    "date_range": "2024-01-15 - 2024-01-21",
    "training_summary": {
      "workouts_completed": 5,
      "workouts_planned": 5,
      "completion_rate": 100,
      "total_volume": 42500,
      "highlights": [
        "卧推首次突破 85kg",
        "连续4周保持100%完成率"
      ]
    },
    "nutrition_summary": {
      "average_calories": 2650,
      "average_protein": 175,
      "adherence_rate": 86,
      "notes": "周末饮食记录缺失"
    },
    "body_metrics_change": {
      "weight_change": 0.5,
      "trend": "稳步上升"
    },
    "achievements": [
      "🏆 卧推突破 85kg",
      "⭐ 保持训练一致性"
    ],
    "areas_for_improvement": [
      "提高周末饮食记录频率",
      "增加核心训练"
    ],
    "next_week_focus": [
      "尝试深蹲增重至 115kg",
      "改善硬拉技术",
      "每天记录饮食"
    ],
    "motivational_message": "本周表现出色！下周继续加油！"
  }
}
```

---

## 错误处理

### 标准错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### 常见HTTP状态码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常处理响应数据 |
| 400 | 请求参数错误 | 检查请求体格式和必填字段 |
| 404 | 资源不找到 | 检查 URL 路径和资源 ID |
| 422 | 验证错误 | 检查数据格式和类型 |
| 500 | 服务器内部错误 | 稍后重试或联系支持 |
| 503 | 服务不可用 | 检查服务状态，稍后重试 |

### Python 错误处理示例

```python
import requests
from requests.exceptions import RequestException

def api_call_with_error_handling(url, method='GET', **kwargs):
    """带错误处理的 API 调用"""
    try:
        if method == 'GET':
            response = session.get(url, **kwargs)
        elif method == 'POST':
            response = session.post(url, **kwargs)

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        # HTTP 错误
        status_code = e.response.status_code
        error_detail = e.response.json().get('detail', 'Unknown error')

        if status_code == 400:
            print(f"请求参数错误: {error_detail}")
        elif status_code == 404:
            print(f"资源不存在: {error_detail}")
        elif status_code == 500:
            print(f"服务器错误: {error_detail}")

        raise

    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请检查网络")
        raise

    except requests.exceptions.Timeout:
        print("请求超时")
        raise

    except RequestException as e:
        print(f"请求失败: {str(e)}")
        raise
```

### JavaScript 错误处理示例

```javascript
async function apiCallWithErrorHandling(url, options = {}) {
  try {
    const response = await apiClient.request({
      url,
      ...options
    })

    return response.data

  } catch (error) {
    if (error.response) {
      // 服务器返回错误响应
      const { status, data } = error.response

      switch (status) {
        case 400:
          console.error('请求参数错误:', data.detail)
          break
        case 404:
          console.error('资源不存在:', data.detail)
          break
        case 500:
          console.error('服务器错误:', data.detail)
          break
        default:
          console.error('请求失败:', data.detail)
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('无法连接到服务器')
    } else {
      // 其他错误
      console.error('请求配置错误:', error.message)
    }

    throw error
  }
}
```

---

## 最佳实践

### 1. 使用对话 ID 维持上下文

```python
# 保存对话 ID
conversation_id = None

# 第一次对话
result = send_chat_message("我想开始健身")
conversation_id = result['conversation_id']

# 后续对话使用相同 ID
result = send_chat_message("我每周可以训练5次", conversation_id)
```

### 2. 批量操作

```python
# 不推荐：逐个记录
for meal in meals:
    log_meal(meal)  # 多次网络请求

# 推荐：批量记录
log_meals_batch(meals)  # 一次网络请求
```

### 3. 缓存常用数据

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_user_profile(user_id: int):
    """缓存用户资料"""
    return fetch_user_profile(user_id)
```

### 4. 异步并发请求

```python
import asyncio
import aiohttp

async def fetch_multiple_data():
    """并发获取多个数据"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_workout_plan(session),
            fetch_nutrition_plan(session),
            fetch_progress_data(session)
        ]

        results = await asyncio.gather(*tasks)
        return results
```

### 5. 请求重试机制

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_retry():
    """创建带重试机制的会话"""
    session = requests.Session()

    retry = Retry(
        total=3,  # 总重试次数
        backoff_factor=1,  # 重试间隔因子
        status_forcelist=[500, 502, 503, 504]  # 需要重试的状态码
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
```

---

## 完整示例：健身日志应用

```python
class FitnessPlannerClient:
    """Fitness Planner API 客户端"""

    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.session = self._create_session()
        self.conversation_id = None

    def _create_session(self):
        """创建会话"""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json"
        })
        return session

    def chat(self, message: str) -> dict:
        """发送聊天消息"""
        url = f"{self.base_url}/chat/message"
        response = self.session.post(url, json={
            "message": message,
            "conversation_id": self.conversation_id,
            "include_history": True
        })
        response.raise_for_status()

        data = response.json()
        self.conversation_id = data['conversation_id']
        return data

    def generate_workout_plan(self) -> dict:
        """生成训练计划"""
        url = f"{self.base_url}/workouts/plan/generate"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()

    def log_meal(self, description: str) -> dict:
        """记录饮食"""
        url = f"{self.base_url}/nutrition/meal/parse"
        response = self.session.post(url, params={"description": description})
        response.raise_for_status()
        return response.json()

    def get_weekly_report(self) -> dict:
        """获取周报"""
        url = f"{self.base_url}/progress/report/weekly"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()

# 使用示例
client = FitnessPlannerClient()

# 1. 与 AI 对话
response = client.chat("我想制定一个增肌计划")
print(response['message'])

# 2. 生成训练计划
plan = client.generate_workout_plan()
print(f"已生成计划: {plan['plan']['plan_name']}")

# 3. 记录饮食
meal = client.log_meal("我早上吃了2个鸡蛋和一碗燕麦")
print(f"记录成功，摄入 {meal['parsed_data']['total_macros']['calories']} kcal")

# 4. 查看周报
report = client.get_weekly_report()
print(f"本周完成 {report['report']['training_summary']['workouts_completed']} 次训练")
```

---

## 交互式 API 文档

访问 **http://localhost:8000/docs** 可以查看完整的交互式 API 文档（Swagger UI），在那里你可以：

- 📖 查看所有 API 端点
- 🧪 直接在浏览器中测试 API
- 📋 查看请求/响应模型
- 💻 生成各种语言的代码示例

---

## 获取帮助

- 📮 提交 Issue: [GitHub Issues](https://github.com/yourusername/Fitness_Plan/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/yourusername/Fitness_Plan/discussions)
- 📧 邮箱: support@example.com

---

**最后更新**: 2024-11-17
