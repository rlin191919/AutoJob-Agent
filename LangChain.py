"""
chain.py - LangChain Chain 编排
Phase 1 MVP：构建简历优化 Chain，串联 Prompt + LLM + Memory
"""

from typing import Optional
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

from llm import get_llm
from prompts import get_optimization_prompt

# ==========================================
# 1. 构建简历优化 Chain
# ==========================================
def build_optimization_chain(
    llm=None, 
    memory: Optional[ConversationBufferMemory] = None
) -> LLMChain:
    """
    构建简历优化 LLMChain

    实现方式：
    1. 使用 prompts.py 中的优化 Prompt 模板
    2. 使用 llm.py 中的 LLM 实例
    3. 使用 memory.py 中的 Memory 实例（可选）
    4. 组合成 LLMChain，支持变量注入和上下文记忆

    Args:
        llm: LLM 实例（默认使用 DeepSeek-V3）
        memory: Memory 实例（可选，用于上下文记忆）

    Returns:
        LLMChain 实例

    Usage:
        chain = build_optimization_chain()
        result = chain.run(resume=resume_text, jd=jd_text, company_type="大厂")
    """
    # 1. 获取 LLM（如果未提供）
    if llm is None:
        llm = get_llm(model_name="DeepSeek-V3")

    # 2. 获取 Prompt 模板
    prompt = get_optimization_prompt()

    # 3. 构建 Chain
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,  # 如果提供，会自动注入 chat_history
        verbose=True,     # 开发时打印详细日志
    )

    return chain

# ==========================================
# 2. 构建简历解析 Chain（Phase 1 扩展）
# ==========================================
def build_parse_chain(llm=None) -> LLMChain:
    """
    构建简历解析 Chain（提取结构化信息）

    Args:
        llm: LLM 实例

    Returns:
        LLMChain 实例
    """
    from prompts import get_parse_prompt

    if llm is None:
        llm = get_llm(model_name="DeepSeek-V3")

    prompt = get_parse_prompt()

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
    )

    return chain

# ==========================================
# 3. 构建 JD 解析 Chain（Phase 1 扩展）
# ==========================================
def build_jd_parse_chain(llm=None) -> LLMChain:
    """
    构建 JD 解析 Chain（提取关键信息）

    Args:
        llm: LLM 实例

    Returns:
        LLMChain 实例
    """
    from prompts import get_jd_parse_prompt

    if llm is None:
        llm = get_llm(model_name="DeepSeek-V3")

    prompt = get_jd_parse_prompt()

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
    )

    return chain
