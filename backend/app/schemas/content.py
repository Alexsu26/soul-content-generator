# app/schemas/content.py
from pydantic import BaseModel
from typing import List, Optional

class ContentRequest(BaseModel):
    """用户请求模型"""
    user_input: str
    user_id: Optional[str] = None  # 用于个性化（后续扩展）


class ContentVersion(BaseModel):
    """文案版本"""
    style: str
    content: str
    description: str


class ImageSuggestion(BaseModel):
    """配图建议"""
    description: str
    keywords: str
    style: str


class ContentResponse(BaseModel):
    """响应模型"""
    refined_versions: List[ContentVersion]
    tags: List[str]
    image_suggestions: List[ImageSuggestion]
