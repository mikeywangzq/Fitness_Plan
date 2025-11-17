"""
认证依赖和中间件

提供 FastAPI 依赖注入函数，用于保护需要认证的路由
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import decode_access_token
from app.models.user import User
from app.core.database import get_db

# OAuth2 密码认证方案
# tokenUrl 指向登录接口，用于 Swagger UI 的测试
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login/oauth2")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    从 JWT token 中获取当前用户

    这是一个 FastAPI 依赖函数，可以注入到任何需要认证的路由中

    Args:
        token: 从请求头 Authorization 中提取的 JWT token
        db: 数据库会话

    Returns:
        User: 当前认证的用户对象

    Raises:
        HTTPException: 如果 token 无效或用户不存在
    """
    # 定义认证失败的异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码 JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # 从 payload 中提取用户 ID
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # 从数据库中查询用户
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    确保当前用户是激活状态

    Args:
        current_user: 从 get_current_user 依赖注入的用户

    Returns:
        User: 激活的用户对象

    Raises:
        HTTPException: 如果用户被禁用
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    return current_user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[str]:
    """
    可选的用户认证依赖

    用于可以公开访问但对认证用户提供额外功能的路由

    Args:
        token: JWT token（可选）

    Returns:
        Optional[str]: 用户 ID 或 None
    """
    if token is None:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    return payload.get("sub")
