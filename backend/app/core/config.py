# app/core/config.py
import os
from openai import OpenAI

# OpenAI 客户端（可切换为通义千问、Ollama等）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-turbo") # 提供一个默认值
