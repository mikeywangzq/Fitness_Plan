"""
FastAPI 主应用入口文件

这是整个健身规划 Agent 后端服务的入口点，负责：
1. 创建和配置 FastAPI 应用实例
2. 设置 CORS 跨域策略
3. 注册所有 API 路由模块
4. 提供健康检查端点
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import chat, users, workouts, nutrition, progress, exercises

# 创建 FastAPI 应用实例
# title: API 文档标题
# version: 版本号，从配置中读取
# description: API 描述信息
# debug: 调试模式，开启后提供详细错误信息
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于 AI 的智能健身训练规划和营养追踪系统",
    debug=settings.DEBUG,
)

# 配置跨域资源共享 (CORS) 中间件
# 允许前端应用从不同域名访问后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 允许的源地址列表
    allow_credentials=True,                 # 允许携带认证信息（cookies）
    allow_methods=["*"],                    # 允许所有 HTTP 方法
    allow_headers=["*"],                    # 允许所有请求头
)


# 注册各个功能模块的路由
# 每个模块处理特定领域的功能

# 聊天模块：处理与 AI Agent 的对话交互
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# 用户模块：处理用户注册、登录、个人信息管理
app.include_router(users.router, prefix="/api/users", tags=["Users"])

# 训练模块：处理训练计划生成、训练记录等
app.include_router(workouts.router, prefix="/api/workouts", tags=["Workouts"])

# 营养模块：处理营养计划、饮食记录等
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])

# 进度模块：处理进度追踪、数据分析等
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])

# 动作库模块：处理动作查询和推荐（V1.1 新功能）
app.include_router(exercises.router, prefix="/api/exercises", tags=["Exercises"])


@app.get("/")
async def root():
    """
    根路径端点

    返回应用基本信息和状态
    用于快速检查服务是否正常运行
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs",  # Swagger UI 文档地址
        "message": "欢迎使用健身训练规划 Agent API"
    }


@app.get("/health")
async def health_check():
    """
    健康检查端点

    用于监控系统和负载均衡器检查服务健康状态
    返回简单的状态信息
    """
    return {"status": "healthy"}


# 程序入口点
# 仅在直接运行此文件时执行（不通过 uvicorn 命令）
if __name__ == "__main__":
    import uvicorn
    # 启动 ASGI 服务器
    uvicorn.run(
        "app.main:app",        # 应用路径
        host=settings.HOST,     # 监听地址
        port=settings.PORT,     # 监听端口
        reload=settings.DEBUG,  # 调试模式下启用热重载
    )
