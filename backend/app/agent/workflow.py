# app/agent/workflow.py
from langgraph.graph import StateGraph, END
from .nodes import refine_content_node, generate_tags_node, suggest_images_node
from .state import ContentState

def create_workflow():
    """创建并编译工作流"""
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
