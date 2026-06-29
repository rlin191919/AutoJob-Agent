"""
utils.py - 工具函数集合
Phase 1 MVP：通用辅助函数
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

# ==========================================
# 1. 文件保存工具
# ==========================================
def save_text_to_file(text: str, filename: str, output_dir: str = "./output") -> str:
    """
    保存文本到文件

    Args:
        text: 文本内容
        filename: 文件名
        output_dir: 输出目录

    Returns:
        保存的文件路径
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

    return filepath

# ==========================================
# 2. JSON 保存/加载
# ==========================================
def save_json(data: Dict[str, Any], filename: str, output_dir: str = "./output") -> str:
    """保存字典为 JSON 文件"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath

def load_json(filename: str, input_dir: str = "./output") -> Optional[Dict[str, Any]]:
    """从 JSON 文件加载字典"""
    filepath = os.path.join(input_dir, filename)
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# ==========================================
# 3. 文本处理工具
# ==========================================
def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本，超出部分显示省略号"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def count_words(text: str) -> int:
    """统计中文字符数（粗略）"""
    return len(text.replace(" ", "").replace("\n", ""))

# ==========================================
# 4. 时间格式化
# ==========================================
def get_timestamp() -> str:
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def format_datetime(dt: datetime = None) -> str:
    """格式化日期时间"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# 5. 环境检查
# ==========================================
def check_env_variables(required_vars: list) -> Dict[str, bool]:
    """
    检查必需的环境变量是否设置

    Args:
        required_vars: 环境变量名列表

    Returns:
        检查结果字典 {var_name: is_set}
    """
    return {var: os.getenv(var) is not None for var in required_vars}
