# 🚀 AutoJob-Agent 开发日志

## 【2026-06-27】Day 1: 从 Vibe Coding 迈向 Agent 开发的第一步

### 1. 今日进展
- **项目立项**：明确了产品定位——一款集“解析-优化-投递”于一体的智能求职 Agent。
- **仓库初始化**：在 GitHub 建立了开源仓库，编写了第一版 `README.md`。
- **技术选型思考**：
  - 我目前擅长 Vibe Coding（通过与 AI 对话写代码），因此决定选择 **Streamlit** 作为前端，因为它不需要我懂复杂的 React/Vue，全靠 Python 驱动。
  - 核心 Agent 逻辑准备尝试 **CrewAI**，把“简历优化师”和“投递机器人”做成两个不同的 Agent 角色。

### 2. Agent 核心 Prompt 构想 (我的第一个提示词工程)
为了让 AI 完美美化简历，我初步设计了“简历优化 Agent”的系统提示词：
> **Role**: 资深 HR 与职业规划专家
> **Task**: 对比 `User_Resume` 和 `Job_JD`。找出用户缺少的关键词，使用 STAR 原则（情景、任务、行动、结果）重写用户的项目经历，使其与 JD 的匹配度达到 90% 以上。保持真实性，严禁凭空捏造经历。

### 3. 遇到的挑战与今日复盘
- **挑战**：PDF 和 Word 里面可能包含复杂的表格，单纯用 `PyPDF2` 提取文本可能会乱序。
- **解法（Vibe Coding 经验）**：明天准备让 Cursor/Copilot 帮我写一个基于 `pdfplumber` 或利用大模型多模态（Vision）直接读取简历截图的方案。

### 4. 明日计划
- 编写 Python 脚本，实现 PDF/Word 简历的文本提取。
- 在 Streamlit 上搭建一个极其简单的文件上传按钮。
