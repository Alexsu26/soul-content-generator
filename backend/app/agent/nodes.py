# app/agent/nodes.py
import json
from typing import Dict

from app.core.config import client, MODEL_NAME
from .state import ContentState

def load_prompt(file_name: str) -> str:
    """从 prompts 目录加载 Prompt 模板"""
    with open(f"app/agent/prompts/{file_name}", "r", encoding="utf-8") as f:
        return f.read()

def refine_content_node(state: ContentState) -> ContentState:
    """节点1：文案细化"""
    user_input = state["user_input"]
    prompt_template = load_prompt("refine_content.txt")
    prompt = prompt_template.format(user_input=user_input)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
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
    if not state["refined_versions"]:
        return {**state, "tags": []}

    content = state["refined_versions"][0]["content"]
    prompt_template = load_prompt("generate_tags.txt")
    prompt = prompt_template.format(content=content)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
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
    prompt_template = load_prompt("suggest_images.txt")
    prompt = prompt_template.format(content=content)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
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
