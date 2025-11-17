"""
用户 API 端点

处理用户注册、登录、个人信息管理等功能
实现 V1.1 用户认证和授权系统
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.auth import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserOnboarding,
    UserUpdate,
    UserLogin,
    Token
)

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册

    创建新用户账户，密码会被安全哈希存储

    Args:
        user: 用户注册信息（邮箱、用户名、密码）
        db: 数据库会话

    Returns:
        Token: 包含 JWT token 和用户信息

    Raises:
        HTTPException: 如果邮箱或用户名已存在
    """
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用"
        )

    # 创建新用户
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        is_active=True,
        onboarding_completed=False
    )

    try:
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户创建失败，请稍后重试"
        )

    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(db_user)
    )


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录

    验证用户凭据并返回 JWT token

    Args:
        user_credentials: 登录凭据（邮箱、密码）
        db: 数据库会话

    Returns:
        Token: 包含 JWT token 和用户信息

    Raises:
        HTTPException: 如果凭据无效
    """
    # 查找用户
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalar_one_or_none()

    # 验证用户和密码
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否被禁用
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/login/oauth2", response_model=Token)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 兼容的登录端点

    用于 Swagger UI 的 "Authorize" 功能
    使用用户名（或邮箱）和密码登录

    Args:
        form_data: OAuth2 表单数据
        db: 数据库会话

    Returns:
        Token: JWT token
    """
    # 尝试使用邮箱或用户名登录
    result = await db.execute(
        select(User).where(
            (User.email == form_data.username) | (User.username == form_data.username)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前认证用户信息

    需要在请求头中携带有效的 JWT token

    Args:
        current_user: 从 token 中提取的当前用户

    Returns:
        UserResponse: 用户信息
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息

    允许用户更新个人资料、健身目标等信息

    Args:
        user_update: 要更新的用户信息
        current_user: 当前认证用户
        db: 数据库会话

    Returns:
        UserResponse: 更新后的用户信息
    """
    # 更新用户字段
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    try:
        await db.commit()
        await db.refresh(current_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="更新失败，请检查输入数据"
        )

    return UserResponse.model_validate(current_user)


@router.post("/me/onboarding", response_model=UserResponse)
async def complete_onboarding(
    onboarding_data: UserOnboarding,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    完成用户引导流程

    实现 FR-1: 用户引导与目标设定
    收集用户的健身目标、身体数据、设备情况等信息

    Args:
        onboarding_data: 引导流程数据
        current_user: 当前认证用户
        db: 数据库会话

    Returns:
        UserResponse: 更新后的用户信息
    """
    # 更新用户的引导数据
    onboarding_dict = onboarding_data.model_dump(exclude_unset=True)
    for field, value in onboarding_dict.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)

    # 标记引导完成
    current_user.onboarding_completed = True

    try:
        await db.commit()
        await db.refresh(current_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="引导流程完成失败，请检查输入数据"
        )

    return UserResponse.model_validate(current_user)


@router.get("/me/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取完整的用户资料

    包括健身目标、身体数据、训练偏好等所有信息

    Args:
        current_user: 当前认证用户

    Returns:
        dict: 完整的用户资料信息
    """
    return {
        "user": UserResponse.model_validate(current_user),
        "fitness_profile": {
            "goal": current_user.fitness_goal,
            "experience_level": current_user.experience_level,
            "equipment_access": current_user.equipment_access,
            "training_frequency": current_user.training_frequency,
            "target_weight": current_user.target_weight,
            "target_body_fat": current_user.target_body_fat,
            "goal_timeframe": current_user.goal_timeframe,
        },
        "dietary_info": {
            "restrictions": current_user.dietary_restrictions,
            "allergies": current_user.allergies,
        },
        "body_metrics": {
            "age": current_user.age,
            "gender": current_user.gender,
            "height": current_user.height,
            "weight": current_user.weight,
            "body_fat_percentage": current_user.body_fat_percentage,
        },
        "onboarding_completed": current_user.onboarding_completed,
    }
