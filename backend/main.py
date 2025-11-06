# backend/main.py
"""
Soul 内容生成助手 - 后端服务
使用 LangGraph 实现工作流
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, TypedDict, Optional
from langgraph.graph import StateGraph, END
import os
from openai import OpenAI

# ==================== 配置 ====================

app = FastAPI(title="Soul Content Generator API")

# CORS 配置（允许 Vercel 前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 客户端（可切换为通义千问、Ollama等）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL_NAME = os.getenv("MODEL_NAME")


# ==================== 数据模型 ====================

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


# ==================== LangGraph 状态定义 ====================

class ContentState(TypedDict):
    """工作流状态"""
    user_input: str
    refined_versions: List[Dict]
    tags: List[str]
    image_suggestions: List[Dict]
    error: Optional[str]


# ==================== 工作流节点函数 ====================

def refine_content_node(state: ContentState) -> ContentState:
    """节点1：文案细化"""
    user_input = state["user_input"]

    prompt = f"""你是一个专业的社交文案创作助手，为 Soul App 用户优化帖子内容。

用户原始想法：{user_input}

请生成3个不同风格的版本，每个版本要保留用户的核心意思，但优化表达方式：

1. 轻松版：活泼、有趣，可以适当使用 emoji，适合日常轻松分享
2. 文艺版：有意境、有深度，文字优美，适合情感表达
3. 真实版：口语化、接地气，像朋友间聊天，适合真实记录

要求：
- 每个版本50-80字
- 保持 Soul 平台的温暖、真实调性
- 不要过度矫饰，保留用户的真实感受

请按以下 JSON 格式返回：
{{
  "versions": [
    {{"style": "轻松版", "content": "...", "description": "活泼有趣，适合日常分享"}},
    {{"style": "文艺版", "content": "...", "description": "有意境，适合深度表达"}},
    {{"style": "真实版", "content": "...", "description": "口语化，更真实自然"}}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return {
            **state,
            "refined_versions": result.get("versions", [])
        }
    except Exception as e:
        return {
            **state,
            "refined_versions": [],
            "error": f"文案生成失败: {str(e)}"
        }


def generate_tags_node(state: ContentState) -> ContentState:
    """节点2：标签推荐"""

    # 使用第一个版本的内容来生成标签
    if not state["refined_versions"]:
        return {**state, "tags": []}

    content = state["refined_versions"][0]["content"]

    prompt = f"""你是一个社交平台标签推荐专家。

基于以下文案，推荐5-7个适合 Soul App 的标签：
{content}

要求：
- 标签要符合年轻人表达习惯
- 包含情绪类、场景类、话题类标签
- 每个标签以 # 开头
- 标签要热门且相关

请按以下 JSON 格式返回：
{{
  "tags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"]
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return {
            **state,
            "tags": result.get("tags", [])
        }
    except Exception as e:
        return {
            **state,
            "tags": [],
            "error": f"标签生成失败: {str(e)}"
        }


def suggest_images_node(state: ContentState) -> ContentState:
    """节点3：配图建议"""

    if not state["refined_versions"]:
        return {**state, "image_suggestions": []}

    content = state["refined_versions"][0]["content"]

    prompt = f"""你是一个配图建议专家。

基于以下文案，提供2-3个配图建议：
{content}

要求：
- 描述画面内容、色调、氛围
- 适合 AI 绘图或图库搜索
- 符合文案情感基调

请按以下 JSON 格式返回：
{{
  "suggestions": [
    {{
      "description": "画面描述",
      "keywords": "关键词1、关键词2、关键词3",
      "style": "风格类型（如：小清新、文艺、写实等）"
    }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return {
            **state,
            "image_suggestions": result.get("suggestions", [])
        }
    except Exception as e:
        return {
            **state,
            "image_suggestions": [],
            "error": f"配图建议生成失败: {str(e)}"
        }


# ==================== 构建 LangGraph 工作流 ====================

def create_workflow() -> StateGraph:
    """创建工作流"""
    workflow = StateGraph(ContentState)

    # 添加节点
    workflow.add_node("refine_content", refine_content_node)
    workflow.add_node("generate_tags", generate_tags_node)
    workflow.add_node("suggest_images", suggest_images_node)

    # 定义流程
    workflow.set_entry_point("refine_content")
    workflow.add_edge("refine_content", "generate_tags")
    workflow.add_edge("generate_tags", "suggest_images")
    workflow.add_edge("suggest_images", END)

    return workflow.compile()


# 编译工作流
content_generator = create_workflow()


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """健康检查"""
    return {"status": "ok", "message": "Soul Content Generator API"}


@app.post("/api/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """生成内容"""

    if not request.user_input.strip():
        raise HTTPException(status_code=400, detail="输入内容不能为空")

    try:
        # 执行工作流
        result = content_generator.invoke({
            "user_input": request.user_input,
            "refined_versions": [],
            "tags": [],
            "image_suggestions": [],
            "error": None
        })

        # 检查是否有错误
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        # 格式化响应
        return ContentResponse(
            refined_versions=[
                ContentVersion(**version)
                for version in result["refined_versions"]
            ],
            tags=result["tags"],
            image_suggestions=[
                ImageSuggestion(**suggestion)
                for suggestion in result["image_suggestions"]
            ]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


# ==================== 运行服务 ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
