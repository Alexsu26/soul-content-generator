# app/agent/state.py
from typing import List, Dict, TypedDict, Optional

class ContentState(TypedDict):
    """工作流状态"""
    user_input: str
    refined_versions: List[Dict]
    tags: List[str]
    image_suggestions: List[Dict]
    error: Optional[str]
