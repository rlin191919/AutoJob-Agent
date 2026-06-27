# AutoJob-Agent: 基于大模型的简历优化与自动投递助手 

AutoJob-Agent 是一个智能求职自动化 Agent。用户只需提供原始简历（PDF/Word）和目标岗位 JD，Agent 将自动进行深度匹配、简历定制化润色，并根据用户的投递意向（公司类型、岗位）实现自动化精准投递。

本项目致力于解放求职者双手，用 AI 提升拿到面试邀请的概率。

✨ 核心特性

📄 多格式简历解析**：支持 Word、PDF 格式简历的一键上传与内容结构化提取。

🎯 简历智能精准润色**：基于大模型（LLM），深度对比原始简历与目标岗位 JD，自动查漏补缺，用专业术语和 STAR 法则美化简历。

💼 投递意向匹配**：用户指定目标公司类型（如：大厂、外企、初创公司）和岗位，Agent 自动筛选最匹配的职位。

🤖 自动化一键投递**：结合浏览器自动化技术，模拟真实用户在主流招聘平台进行投递（开发中）。

🛠️ 技术架构

- **LLM 驱动**：GPT-4o / Claude 3.5 Sonnet / DeepSeek
- **Agent 框架**：LangChain / CrewAI (实现解析、优化、投递多角色协同)
- **前端界面**：Streamlit (极简的交互式 Web 界面)
- **自动化工具**：Playwright / Python-docx / PyPDF2

📅 开发计划与路线图 (Roadmap)

 项目立项与核心架构设计
Phase 1: 简历与 JD 文本解析模块开发 (进行中)
Phase 2: 基于 STAR 法则的简历深度优化 Prompt 调试
Phase 3: Streamlit 交互前端页面搭建
Phase 4: 浏览器自动化投递脚本集成（Playwright）
- [ ] **Phase 5**: 商业化探索与多账号管理

## 开发者共享指南

非常欢迎任何形式的贡献！如果你有任何想法、Bug 反馈或功能建议，请随时提交 Issue 或 Pull Request。
本项目的口号是：“从 Vibe Coding 走向生产级 Agent 开发！”
