"""
memory.py - Memory 管理模块
Phase 1 MVP：使用 LangChain Memory 实现对话历史管理
功能：保存每次优化的输入输出，支持上下文记忆
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# ==========================================
# 1. 全局 Memory 存储（内存 + 文件持久化）
# ==========================================
# 内存缓存：session_id -> ConversationBufferMemory
_MEMORY_CACHE: Dict[str, ConversationBufferMemory] = {}

# 持久化目录
MEMORY_DIR = "./memory_storage"
os.makedirs(MEMORY_DIR, exist_ok=True)

# ==========================================
# 2. 获取 Memory 实例（核心函数）
# ==========================================
def get_memory(session_id: str = "default") -> ConversationBufferMemory:
    """
    获取或创建指定 session 的 Memory 实例

    实现方式：
    1. 检查内存缓存是否有该 session 的 Memory
    2. 如果有，直接返回（保持上下文连续性）
    3. 如果没有，尝试从文件加载历史记录
    4. 如果文件也没有，创建新的 Memory 实例

    Args:
        session_id: 会话标识（可用用户 ID 或随机 UUID）

    Returns:
        ConversationBufferMemory 实例
    """
    # 1. 检查内存缓存
    if session_id in _MEMORY_CACHE:
        return _MEMORY_CACHE[session_id]

    # 2. 尝试从文件加载历史
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,  # 返回 Message 对象列表
    )

    history_file = os.path.join(MEMORY_DIR, f"{session_id}.json")
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 恢复历史消息
                for msg in data.get("history", []):
                    if msg["type"] == "human":
                        memory.chat_memory.add_user_message(msg["content"])
                    elif msg["type"] == "ai":
                        memory.chat_memory.add_ai_message(msg["content"])
        except Exception as e:
            print(f"加载 Memory 历史失败: {e}")

    # 3. 缓存到内存
    _MEMORY_CACHE[session_id] = memory
    return memory

# ==========================================
# 3. 保存对话到 Memory
# ==========================================
def save_to_memory(
    session_id: str, 
    input_data: Dict[str, Any], 
    output_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    保存单次优化记录到 Memory

    实现方式：
    1. 将输入输出格式化为对话消息
    2. 添加到 ConversationBufferMemory
    3. 异步保存到文件（JSON 格式）

    Args:
        session_id: 会话标识
        input_data: 输入数据（简历长度、JD 长度等）
        output_data: 输出数据（优化后简历长度等）
        metadata: 额外元数据（时间、模型、分数等）
    """
    memory = get_memory(session_id)

    # 构建人类输入（简化版）
    human_input = f"优化简历 | 简历长度: {input_data.get('resume_length', 0)} | JD长度: {input_data.get('jd_length', 0)}"

    # 构建 AI 输出
    ai_output = f"优化完成 | 输出长度: {output_data.get('optimized_length', 0)} | 匹配分数: {metadata.get('match_score', 'N/A') if metadata else 'N/A'}"

    # 添加到 Memory
    memory.chat_memory.add_user_message(human_input)
    memory.chat_memory.add_ai_message(ai_output)

    # 保存到文件
    _persist_memory(session_id, memory, metadata)

# ==========================================
# 4. 从 Memory 加载历史
# ==========================================
def load_from_memory(session_id: str) -> List[Dict[str, Any]]:
    """
    加载指定 session 的历史记录

    Returns:
        历史记录列表，每条包含 type, content, timestamp
    """
    memory = get_memory(session_id)
    messages = memory.chat_memory.messages

    history = []
    for msg in messages:
        history.append({
            "type": "human" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content,
            "timestamp": datetime.now().isoformat()
        })

    return history

# ==========================================
# 5. 获取 Memory 摘要（用于上下文压缩）
# ==========================================
def get_memory_summary(session_id: str) -> str:
    """
    获取 Memory 摘要，用于注入 Prompt 上下文

    Phase 1 MVP：简单返回最近 3 轮对话的摘要
    Phase 2：可实现 Token 压缩、向量检索等高级功能
    """
    history = load_from_memory(session_id)
    if not history:
        return "暂无历史优化记录"

    # 取最近 3 轮（6 条消息）
    recent = history[-6:]
    summary = "\n".join([
        f"{'用户' if h['type'] == 'human' else 'AI'}: {h['content'][:100]}..."
        for h in recent
    ])
    return summary

# ==========================================
# 6. 清空 Memory
# ==========================================
def clear_memory(session_id: str) -> None:
    """清空指定 session 的 Memory"""
    if session_id in _MEMORY_CACHE:
        del _MEMORY_CACHE[session_id]

    history_file = os.path.join(MEMORY_DIR, f"{session_id}.json")
    if os.path.exists(history_file):
        os.remove(history_file)

# ==========================================
# 7. 内部函数：持久化到文件
# ==========================================
def _persist_memory(
    session_id: str, 
    memory: ConversationBufferMemory,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """将 Memory 持久化到 JSON 文件"""
    history_file = os.path.join(MEMORY_DIR, f"{session_id}.json")

    data = {
        "session_id": session_id,
        "last_updated": datetime.now().isoformat(),
        "metadata": metadata or {},
        "history": []
    }

    for msg in memory.chat_memory.messages:
        data["history"].append({
            "type": "human" if isinstance(msg, HumanMessage) else "ai",
            "content": msg.content
        })

    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
