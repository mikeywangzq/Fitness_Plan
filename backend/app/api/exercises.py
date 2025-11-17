"""
动作库 API 端点

提供查询和搜索动作的接口
V1.1 新功能
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.rag import get_exercise_rag

router = APIRouter()


class ExerciseResponse(BaseModel):
    """动作响应模型"""
    id: str
    name: str
    english_name: str
    category: str
    target_muscles: List[str]
    equipment: str
    difficulty: str
    description: str
    instructions: List[str]
    tips: List[str]
    common_mistakes: List[str]
    alternatives: List[str]


@router.get("/", response_model=List[ExerciseResponse])
async def get_all_exercises():
    """
    获取所有动作
    """
    try:
        rag = get_exercise_rag()
        exercises = rag.get_all_exercises()
        return exercises
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取动作失败: {str(e)}")


@router.get("/search", response_model=List[ExerciseResponse])
async def search_exercises(
    query: str = Query(..., description="搜索查询"),
    n_results: int = Query(5, ge=1, le=20, description="返回结果数量")
):
    """
    搜索动作
    
    使用自然语言搜索相关动作，基于语义相似度
    
    示例：
    - "锻炼胸部的动作"
    - "适合新手的腿部训练"
    - "徒手背部动作"
    """
    try:
        rag = get_exercise_rag()
        exercises = rag.search_exercises(query, n_results)
        return exercises
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/category/{category}", response_model=List[ExerciseResponse])
async def get_exercises_by_category(category: str):
    """
    根据类别获取动作
    
    类别: 胸部、背部、腿部、肩部、手臂、核心
    """
    try:
        rag = get_exercise_rag()
        exercises = rag.get_exercises_by_category(category)
        return exercises
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/equipment/{equipment}", response_model=List[ExerciseResponse])
async def get_exercises_by_equipment(equipment: str):
    """
    根据设备获取动作
    
    设备: 徒手、哑铃、杠铃、单杠、罗马椅等
    """
    try:
        rag = get_exercise_rag()
        exercises = rag.get_exercises_by_equipment(equipment)
        return exercises
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/muscle/{muscle}", response_model=List[ExerciseResponse])
async def get_exercises_by_muscle(muscle: str):
    """
    根据目标肌群获取动作
    
    肌群: 胸大肌、背阔肌、股四头肌、臀大肌等
    """
    try:
        rag = get_exercise_rag()
        exercises = rag.get_exercises_by_muscle(muscle)
        return exercises
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/{name}", response_model=ExerciseResponse)
async def get_exercise_details(name: str):
    """
    获取动作详细信息
    
    根据动作名称（中文或英文）获取完整信息
    """
    try:
        rag = get_exercise_rag()
        exercise = rag.get_exercise_details(name)
        
        if not exercise:
            raise HTTPException(status_code=404, detail=f"未找到动作: {name}")
        
        return exercise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/recommend", response_model=List[ExerciseResponse])
async def recommend_exercises(
    goal: str,
    equipment: str,
    difficulty: str,
    n_results: int = Query(8, ge=1, le=20)
):
    """
    推荐动作
    
    根据健身目标、设备和难度推荐合适的动作
    """
    try:
        rag = get_exercise_rag()
        exercises = rag.recommend_exercises(goal, equipment, difficulty, n_results)
        return exercises
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")
