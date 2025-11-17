"""
动作库 RAG (检索增强生成) 服务

使用 ChromaDB 存储动作知识库的向量表示，
提供基于语义的动作检索功能，增强训练计划生成的准确性
"""
import json
import os
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain.embeddings import OpenAIEmbeddings
from app.core.config import settings


class ExerciseRAG:
    """动作库 RAG 系统"""
    
    def __init__(self):
        """初始化 RAG 系统"""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.chroma_dir = self.data_dir / "chroma_db"
        self.exercises_file = self.data_dir / "exercises.json"
        
        # 初始化 ChromaDB 客户端
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=str(self.chroma_dir)
        ))
        
        # 初始化 OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="exercises",
            metadata={"description": "健身动作知识库"}
        )
        
        # 如果集合为空，加载数据
        if self.collection.count() == 0:
            self._load_exercises()
    
    def _load_exercises(self):
        """从 JSON 文件加载动作数据并向量化"""
        if not self.exercises_file.exists():
            print(f"警告: 动作数据文件不存在: {self.exercises_file}")
            return
        
        with open(self.exercises_file, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
        
        print(f"加载 {len(exercises)} 个动作到向量数据库...")
        
        for exercise in exercises:
            # 构建用于向量化的文本
            text = self._exercise_to_text(exercise)
            
            # 生成嵌入向量
            embedding = self.embeddings.embed_query(text)
            
            # 添加到 ChromaDB
            self.collection.add(
                ids=[exercise['id']],
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    'name': exercise['name'],
                    'english_name': exercise['english_name'],
                    'category': exercise['category'],
                    'equipment': exercise['equipment'],
                    'difficulty': exercise['difficulty'],
                    'target_muscles': ','.join(exercise['target_muscles'])
                }]
            )
        
        print(f"成功加载 {len(exercises)} 个动作")
    
    def _exercise_to_text(self, exercise: Dict) -> str:
        """将动作对象转换为用于向量化的文本"""
        text_parts = [
            f"动作名称: {exercise['name']} ({exercise['english_name']})",
            f"类别: {exercise['category']}",
            f"目标肌群: {', '.join(exercise['target_muscles'])}",
            f"设备: {exercise['equipment']}",
            f"难度: {exercise['difficulty']}",
            f"描述: {exercise['description']}",
            f"要点: {' '.join(exercise['tips'])}",
            f"常见错误: {', '.join(exercise['common_mistakes'])}",
        ]
        return ' '.join(text_parts)
    
    def search_exercises(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        根据查询搜索相关动作
        
        Args:
            query: 搜索查询（自然语言）
            n_results: 返回结果数量
            filters: 过滤条件，如 {"category": "腿部"}
        
        Returns:
            List[Dict]: 相关动作列表
        """
        # 生成查询向量
        query_embedding = self.embeddings.embed_query(query)
        
        # 构建 where 子句
        where = None
        if filters:
            where = filters
        
        # 在 ChromaDB 中搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        # 从原始数据中获取完整信息
        exercises = []
        for doc_id in results['ids'][0]:
            exercise = self._get_exercise_by_id(doc_id)
            if exercise:
                exercises.append(exercise)
        
        return exercises
    
    def _get_exercise_by_id(self, exercise_id: str) -> Optional[Dict]:
        """根据 ID 获取完整的动作信息"""
        with open(self.exercises_file, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
        
        for exercise in exercises:
            if exercise['id'] == exercise_id:
                return exercise
        
        return None
    
    def get_exercises_by_category(self, category: str) -> List[Dict]:
        """获取指定类别的所有动作"""
        return self.search_exercises(
            query=f"{category}训练动作",
            n_results=20,
            filters={"category": category}
        )
    
    def get_exercises_by_equipment(self, equipment: str) -> List[Dict]:
        """获取使用指定设备的动作"""
        return self.search_exercises(
            query=f"使用{equipment}的训练动作",
            n_results=20,
            filters={"equipment": equipment}
        )
    
    def get_exercises_by_muscle(self, muscle: str) -> List[Dict]:
        """获取锻炼指定肌群的动作"""
        with open(self.exercises_file, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
        
        matching_exercises = []
        for exercise in exercises:
            if muscle in exercise['target_muscles']:
                matching_exercises.append(exercise)
        
        return matching_exercises
    
    def recommend_exercises(
        self,
        goal: str,
        equipment: str,
        difficulty: str,
        n_results: int = 8
    ) -> List[Dict]:
        """
        根据用户目标、设备和难度推荐动作
        
        Args:
            goal: 健身目标（如"增肌"、"减脂"）
            equipment: 可用设备
            difficulty: 难度等级
            n_results: 返回结果数量
        
        Returns:
            List[Dict]: 推荐动作列表
        """
        query = f"{goal} {equipment} {difficulty}"
        
        # 根据设备过滤
        equipment_filter = None
        if equipment != "专业健身房":
            equipment_filter = {"equipment": equipment}
        
        return self.search_exercises(
            query=query,
            n_results=n_results,
            filters=equipment_filter
        )
    
    def get_all_exercises(self) -> List[Dict]:
        """获取所有动作"""
        with open(self.exercises_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_exercise_details(self, exercise_name: str) -> Optional[Dict]:
        """根据动作名称获取详细信息"""
        with open(self.exercises_file, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
        
        for exercise in exercises:
            if exercise['name'] == exercise_name or exercise['english_name'] == exercise_name:
                return exercise
        
        return None


# 全局 RAG 实例
_exercise_rag = None


def get_exercise_rag() -> ExerciseRAG:
    """获取 Exercise RAG 单例"""
    global _exercise_rag
    if _exercise_rag is None:
        _exercise_rag = ExerciseRAG()
    return _exercise_rag
