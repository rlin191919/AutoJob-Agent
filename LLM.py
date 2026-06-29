"""
llm.py - LLM 调用封装
Phase 1 MVP：支持多模型切换（DeepSeek / OpenAI / Claude）
"""

import os
from typing import Optional
from langchain.llms.base import LLM
from langchain.chat_models import ChatOpenAI

# ==========================================
# 1. 模型配置映射
# ==========================================
MODEL_CONFIG = {
    "DeepSeek-V3": {
        "base_url": "https://api.deepseek.com/v1",
        "model_name": "deepseek-chat",  # DeepSeek-V3 的模型标识
        "api_key_env": "DEEPSEEK_API_KEY",
    },
    "GPT-4o": {
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
    },
    "Claude 3.5": {
        "base_url": "https://api.anthropic.com/v1",  # 或通过第三方代理
        "model_name": "claude-3-5-sonnet-20241022",
        "api_key_env": "ANTHROPIC_API_KEY",
    }
}

# ==========================================
# 2. 获取 LLM 实例
# ==========================================
def get_llm(model_name: str = "DeepSeek-V3", temperature: float = 0.7) -> ChatOpenAI:
    """
    根据模型名称获取 LLM 实例

    Args:
        model_name: 模型名称（DeepSeek-V3 / GPT-4o / Claude 3.5）
        temperature: 生成温度，默认 0.7

    Returns:
        ChatOpenAI 实例（兼容 OpenAI API 格式）

    Raises:
        ValueError: 模型名称不支持
        KeyError: API Key 未设置
    """
    if model_name not in MODEL_CONFIG:
        raise ValueError(f"不支持的模型: {model_name}。可选: {list(MODEL_CONFIG.keys())}")

    config = MODEL_CONFIG[model_name]
    api_key = os.getenv(config["api_key_env"])

    if not api_key:
        raise KeyError(
            f"未设置环境变量 {config['api_key_env']}。"
            f"请在 .env 文件或系统环境中设置 API Key。"
        )

    # 使用 LangChain 的 ChatOpenAI（兼容 OpenAI API 格式，DeepSeek 也兼容）
    llm = ChatOpenAI(
        model_name=config["model_name"],
        openai_api_base=config["base_url"],
        openai_api_key=api_key,
        temperature=temperature,
        max_tokens=4096,  # 简历优化需要较长输出
        streaming=False,   # Phase 1 先不用流式，简化逻辑
    )

    return llm

# ==========================================
# 3. 流式输出（Phase 2 扩展）
# ==========================================
def get_llm_streaming(model_name: str = "DeepSeek-V3", temperature: float = 0.7) -> ChatOpenAI:
    """获取支持流式输出的 LLM 实例"""
    llm = get_llm(model_name, temperature)
    llm.streaming = True
    return llm

# ==========================================
# 4. 模型可用性检查
# ==========================================
def check_model_availability(model_name: str) -> bool:
    """检查指定模型是否可用（API Key 是否设置）"""
    if model_name not in MODEL_CONFIG:
        return False
    return os.getenv(MODEL_CONFIG[model_name]["api_key_env"]) is not None

def list_available_models() -> list:
    """列出所有可用模型"""
    return [name for name in MODEL_CONFIG.keys() if check_model_availability(name)]
