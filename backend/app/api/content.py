# app/api/content.py
from fastapi import APIRouter, HTTPException

from app.schemas.content import ContentRequest, ContentResponse
from app.services import content_service

router = APIRouter()

@router.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """生成内容"""

    if not request.user_input.strip():
        raise HTTPException(status_code=400, detail="输入内容不能为空")

    try:
        result = content_service.generate_soul_content(request.user_input)
        return ContentResponse(**result)
    except Exception as e:
        # 更精细的错误处理可以在这里添加
        # 例如，区分是生成错误还是其他系统错误
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
