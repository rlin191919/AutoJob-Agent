"""
prompts.py - Prompt 模板管理
Phase 1 MVP：简历优化核心 Prompt
"""

from langchain.prompts import PromptTemplate

# ==========================================
# 1. 简历优化主 Prompt
# ==========================================
RESUME_OPTIMIZATION_PROMPT = """
你是一位资深 HR 和职业规划专家，擅长根据目标岗位 JD 优化简历。

## 原始简历
{resume}

## 目标岗位 JD
{jd}

## 目标公司类型
{company_type}

## 优化要求
1. **关键词匹配**：提取 JD 中的核心关键词，自然融入简历
2. **量化成果**：将描述性语言改为数据驱动的成果展示
3. **结构调整**：按照 JD 的优先级重新排列经历顺序
4. **去冗余**：删除与目标岗位无关的内容
5. **STAR 法则**：对项目经历使用 Situation-Task-Action-Result 结构
6. **公司类型适配**：
   - 大厂：强调技术深度、系统设计、大规模经验
   - 国央企：强调稳定性、党建活动、合规意识
   - 外企：强调跨文化沟通、英语能力、国际视野
   - 独角兽：强调快速迭代、全栈能力、创业精神

## 输出格式
请直接输出优化后的完整简历文本，保持 Markdown 格式，包含以下部分：
- 个人信息（保留原样）
- 求职意向
- 专业技能（匹配 JD 关键词）
- 工作经历（按 JD 优先级排序，量化成果）
- 项目经历（STAR 法则）
- 教育背景

优化后的简历：
"""

def get_optimization_prompt() -> PromptTemplate:
    """获取简历优化 Prompt 模板"""
    return PromptTemplate(
        input_variables=["resume", "jd", "company_type"],
        template=RESUME_OPTIMIZATION_PROMPT
    )

# ==========================================
# 2. 简历解析 Prompt（用于提取结构化信息）
# ==========================================
RESUME_PARSE_PROMPT = """
请从以下简历文本中提取结构化信息，以 JSON 格式返回：

简历文本：
{resume_text}

请提取以下字段：
- name: 姓名
- phone: 电话
- email: 邮箱
- education: 教育背景列表（学校、专业、学历、时间）
- work_experience: 工作经历列表（公司、职位、时间、职责）
- skills: 技能列表
- projects: 项目经历列表
- certifications: 证书列表

只返回 JSON，不要其他解释。
"""

def get_parse_prompt() -> PromptTemplate:
    """获取简历解析 Prompt 模板"""
    return PromptTemplate(
        input_variables=["resume_text"],
        template=RESUME_PARSE_PROMPT
    )

# ==========================================
# 3. JD 解析 Prompt
# ==========================================
JD_PARSE_PROMPT = """
请从以下职位描述中提取关键信息，以 JSON 格式返回：

JD 文本：
{jd_text}

请提取以下字段：
- position: 职位名称
- department: 部门
- required_skills: 必需技能列表
- preferred_skills: 加分技能列表
- responsibilities: 职责列表
- requirements: 硬性要求（学历、年限等）
- company_type: 公司类型推测
- keywords: 高频关键词列表
- match_hints: 简历应突出的重点

只返回 JSON，不要其他解释。
"""

def get_jd_parse_prompt() -> PromptTemplate:
    """获取 JD 解析 Prompt 模板"""
    return PromptTemplate(
        input_variables=["jd_text"],
        template=JD_PARSE_PROMPT
    )
