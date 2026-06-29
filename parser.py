"""
parser.py - 简历/JD 解析模块
Phase 1 MVP：提取 PDF/DOCX 纯文本，基础信息检测
"""

import io
import docx
import pdfplumber
from typing import Optional, List
import re

# ==========================================
# 1. 文本提取函数（PDF/DOCX）
# ==========================================
def extract_text(file) -> Optional[str]:
    """
    从上传的文件中提取纯文本

    实现方式：
    1. 读取文件字节流
    2. 根据扩展名判断文件类型（pdf/docx）
    3. 使用对应库提取文本
    4. 返回清洗后的文本

    Args:
        file: Streamlit UploadedFile 对象

    Returns:
        提取的文本字符串，失败返回 None
    """
    if file is None:
        return None

    try:
        file_bytes = file.read()
        ext = file.name.split(".")[-1].lower()
        text = ""

        if ext == "pdf":
            # 使用 pdfplumber 提取 PDF 文本
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

        elif ext == "docx":
            # 使用 python-docx 提取 Word 文本
            doc = docx.Document(io.BytesIO(file_bytes))
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
        else:
            return None

        return text.strip() if text.strip() else None

    except Exception as e:
        print(f"文件解析失败: {e}")
        return None

# ==========================================
# 2. 城市检测函数
# ==========================================
def extract_cities_from_resume(text: str, city_list: List[str]) -> List[str]:
    """
    从简历文本中提取意向城市

    实现方式：
    1. 遍历预定义城市列表
    2. 检查城市名是否在文本中
    3. 去重并限制数量

    Args:
        text: 简历文本
        city_list: 城市名称列表

    Returns:
        检测到的城市列表（最多 3 个）
    """
    if not text:
        return []

    found_cities = []
    for city in city_list:
        if city in text and city not in found_cities:
            found_cities.append(city)

    return found_cities[:3]  # 最多返回 3 个

# ==========================================
# 3. 基础信息提取（正则/规则）
# ==========================================
def extract_basic_info(text: str) -> dict:
    """
    使用正则表达式提取基础信息（Phase 1 简化版）

    提取字段：
    - 手机号
    - 邮箱
    - 姓名（简化规则）

    Args:
        text: 简历文本

    Returns:
        基础信息字典
    """
    info = {
        "phone": None,
        "email": None,
        "name": None,
    }

    # 手机号正则（中国大陆）
    phone_pattern = r'1[3-9]\d{9}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        info["phone"] = phone_match.group()

    # 邮箱正则
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    if email_match:
        info["email"] = email_match.group()

    return info
