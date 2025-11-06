# app/services/content_service.py
from app.agent.workflow import create_workflow
from app.schemas.content import ContentResponse, ContentVersion, ImageSuggestion

# 编译工作流，这是一个全局实例
content_generator = create_workflow()

def generate_soul_content(user_input: str) -> dict:
    """执行内容生成工作流并格式化结果"""
    
    # 准备工作流的初始状态
    initial_state = {
        "user_input": user_input,
        "refined_versions": [],
        "tags": [],
        "image_suggestions": [],
        "error": None
    }

    # 执行工作流
    result = content_generator.invoke(initial_state)

    # 检查是否有错误
    if error := result.get("error"):
        # 在实际应用中，这里可能需要更复杂的错误处理逻辑
        # 例如，记录日志、根据错误类型返回不同的信息等
        # 为了保持简单，我们直接在响应中体现错误，由API层处理
        raise Exception(error)

    # 格式化响应
    # 注意：这里我们返回一个字典，API层会用Pydantic模型进行最终验证和序列化
    return {
        "refined_versions": result.get("refined_versions", []),
        "tags": result.get("tags", []),
        "image_suggestions": result.get("image_suggestions", [])
    }
