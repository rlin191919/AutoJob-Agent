import streamlit as st
import docx
import pdfplumber
import io
import time

# ==========================================
# 1. 页面配置与高级动画 CSS
# ==========================================
st.set_page_config(
    page_title="AutoJob-Agent | 智能海投系统",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 注入高级动画与样式系统
st.markdown("""
<style>
    /* 全局字体优化 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* 标题区 - 动态入场 */
    .title-container { 
        text-align: center; 
        margin-bottom: 2.5rem; 
        animation: fadeInDown 0.8s ease-out;
    }
    .main-header { 
        font-size: 3.2rem; 
        font-weight: 800; 
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .sub-header { 
        font-size: 1.15rem; 
        color: #64748B; 
        font-weight: 400;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }

    /* 玻璃拟态卡片 - 悬浮动画 */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 2rem; 
        border-radius: 1.2rem; 
        border: 1px solid rgba(226, 232, 240, 0.6); 
        box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 1.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out both;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(59, 130, 246, 0.12), 0 4px 8px rgba(0,0,0,0.04);
        border-color: rgba(59, 130, 246, 0.3);
    }

    /* 输入区高亮动画 */
    .glass-card:focus-within {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15), 0 12px 24px rgba(59, 130, 246, 0.08);
    }

    /* 步骤指示器 */
    .step-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
        animation: fadeIn 0.6s ease-out 0.4s both;
    }
    .step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #CBD5E1;
        transition: all 0.3s ease;
    }
    .step-dot.active {
        width: 32px;
        border-radius: 4px;
        background: linear-gradient(90deg, #3B82F6, #06B6D4);
        animation: pulse 2s infinite;
    }
    .step-dot.completed {
        background: #10B981;
    }

    /* 结果页卡片 */
    .result-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(16px);
        padding: 1.8rem;
        border-radius: 1rem;
        border: 1px solid rgba(226, 232, 240, 0.5);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.3s ease;
        animation: slideInRight 0.6s ease-out both;
    }
    .result-card:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06);
    }
    .result-card:nth-child(2) { animation-delay: 0.15s; }

    .card-title { 
        font-size: 1.1rem; 
        font-weight: 700; 
        color: #1E293B; 
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .card-title .icon {
        font-size: 1.3rem;
    }

    /* 上传区域样式 */
    .upload-zone {
        border: 2px dashed #CBD5E1;
        border-radius: 0.8rem;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        background: rgba(248, 250, 252, 0.5);
    }
    .upload-zone:hover {
        border-color: #3B82F6;
        background: rgba(59, 130, 246, 0.04);
    }

    /* 主按钮光效 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.5) !important;
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(0);
    }

    /* 加载动画 */
    .loading-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(8px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        animation: fadeIn 0.3s ease;
    }
    .loading-spinner {
        width: 48px;
        height: 48px;
        border: 3px solid #E2E8F0;
        border-top-color: #3B82F6;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    .loading-text {
        margin-top: 1rem;
        color: #64748B;
        font-size: 0.95rem;
        animation: fadeInUp 0.5s ease;
    }

    /* 成功状态条 */
    .success-bar {
        background: linear-gradient(90deg, #10B981, #34D399);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
        animation: slideInDown 0.5s ease-out;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
    }

    /* 返回按钮 */
    .back-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        color: #64748B;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    .back-btn:hover {
        color: #3B82F6;
        gap: 0.6rem;
    }

    /* 标签样式 */
    .section-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 0.5rem;
    }

    /* 状态徽章 */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-success { background: #D1FAE5; color: #059669; }
    .badge-info { background: #DBEAFE; color: #2563EB; }
    .badge-waiting { background: #F1F5F9; color: #64748B; }

    /* 关键帧动画 */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes slideInDown {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none !important;}

    /* 文本区域优化 */
    .stTextArea textarea {
        border-radius: 0.6rem !important;
        border: 1px solid #E2E8F0 !important;
        transition: all 0.2s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }

    /* 选择器优化 */
    .stSelectbox > div > div {
        border-radius: 0.6rem !important;
    }

    /* 文件上传器优化 */
    .stFileUploader > div {
        border-radius: 0.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 文本提取函数
# ==========================================
def extract_text(file):
    if file is None: 
        return None
    file_bytes = file.read()
    ext = file.name.split(".")[-1].lower()
    try:
        text = ""
        if ext == "pdf":
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    if page.extract_text(): 
                        text += page.extract_text() + "\n"
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            for p in doc.paragraphs: 
                text += p.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    text += " | ".join([c.text.strip() for c in row.cells if c.text.strip()]) + "\n"
        return text.strip() if text.strip() else None
    except Exception:
        return None

# ==========================================
# 3. 状态管理初始化
# ==========================================
if "app_stage" not in st.session_state:
    st.session_state.app_stage = "input"
if "loading" not in st.session_state:
    st.session_state.loading = False
if "resume_content" not in st.session_state:
    st.session_state.resume_content = ""
if "jd_content" not in st.session_state:
    st.session_state.jd_content = ""

# ==========================================
# 4. 顶部标题区（始终显示）
# ==========================================
st.markdown("""
<div class="title-container">
    <div class="main-header">💼 AutoJob-Agent</div>
    <div class="sub-header">基于大模型的智能简历精准润色与海投一体化看板</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 输入页面
# ==========================================
if st.session_state.app_stage == "input":

    # 步骤指示器
    st.markdown("""
    <div class="step-indicator">
        <div class="step-dot active"></div>
        <div class="step-dot"></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        # 简历上传卡片
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📄 原始简历上传")
        st.markdown('<div class="section-label">Step 1</div>', unsafe_allow_html=True)

        uploaded_resume = st.file_uploader(
            "支持 PDF 或 DOCX 格式", 
            type=["pdf", "docx"], 
            label_visibility="collapsed",
            help="上传您的简历文件，系统将自动提取文本内容"
        )

        # 实时状态反馈
        if uploaded_resume:
            st.markdown(f'<div class="badge badge-success">✓ 已上传: {uploaded_resume.name}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-waiting">○ 等待上传</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # 智能设置卡片
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 智能投递意向")
        st.markdown('<div class="section-label">配置</div>', unsafe_allow_html=True)

        target_company = st.selectbox(
            "意向公司类型", 
            ["大厂/独角兽", "外企/跨国公司", "中小型科技公司", "不限"],
            help="选择目标公司类型以优化匹配策略"
        )
        model_provider = st.selectbox(
            "大模型内核", 
            ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude 3.5"],
            help="选择底层大模型驱动解析"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # JD 输入卡片
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 目标岗位 JD")
        st.markdown('<div class="section-label">Step 2</div>', unsafe_allow_html=True)

        jd_input_method = st.radio(
            "选择提供方式", 
            ["手动粘贴文本", "上传 JD 文档"], 
            horizontal=True,
            label_visibility="collapsed"
        )

        jd_text_raw = ""
        if jd_input_method == "手动粘贴文本":
            jd_text_raw = st.text_area(
                "粘贴职位描述", 
                placeholder="请把招聘软件上的职位描述(JD)粘贴在这里...", 
                height=180,
                label_visibility="collapsed"
            )
        else:
            uploaded_jd = st.file_uploader(
                "上传 JD 文件", 
                type=["pdf", "docx"],
                label_visibility="collapsed"
            )
            if uploaded_jd: 
                jd_text_raw = extract_text(uploaded_jd)
                if jd_text_raw:
                    st.markdown(f'<div class="badge badge-success">✓ 已提取: {uploaded_jd.name}</div>', unsafe_allow_html=True)

        # 实时字数统计
        if jd_text_raw:
            word_count = len(jd_text_raw.strip())
            st.markdown(f'<div style="text-align:right; font-size:0.8rem; color:#94A3B8; margin-top:0.5rem;">{word_count} 字符</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # 提交区域
    st.markdown("---")

    # 校验状态汇总
    has_resume = uploaded_resume is not None
    has_jd = bool(jd_text_raw and len(jd_text_raw.strip()) >= 10)

    col_status, col_btn = st.columns([1, 2])
    with col_status:
        if has_resume and has_jd:
            st.markdown('<div class="badge badge-success">✓ 所有信息已就绪</div>', unsafe_allow_html=True)
        else:
            missing = []
            if not has_resume: missing.append("简历")
            if not has_jd: missing.append("JD")
            st.markdown(f'<div class="badge badge-waiting">○ 待完善: {"/".join(missing)}</div>', unsafe_allow_html=True)

    with col_btn:
        if st.button("✨ 一键开始智能匹配与解析", type="primary", use_container_width=True, disabled=not (has_resume and has_jd)):
            resume_text = extract_text(uploaded_resume)

            if not resume_text:
                st.error("❌ 简历文件解析失败，请检查文件格式！")
            elif not jd_text_raw or len(jd_text_raw.strip()) < 10:
                st.error("❌ JD 内容过短，请提供完整的职位描述！")
            else:
                # 进入加载状态
                st.session_state.loading = True
                st.session_state.resume_content = resume_text
                st.session_state.jd_content = jd_text_raw
                st.rerun()

# ==========================================
# 6. 加载过渡页面
# ==========================================
elif st.session_state.loading:
    # 模拟处理进度
    progress_text = st.empty()
    progress_bar = st.progress(0)

    for i in range(100):
        time.sleep(0.02)
        progress_bar.progress(i + 1)
        if i < 30:
            progress_text.markdown(f"<div style='text-align:center; color:#64748B;'>📄 正在解析简历结构... {i+1}%</div>", unsafe_allow_html=True)
        elif i < 60:
            progress_text.markdown(f"<div style='text-align:center; color:#64748B;'>🎯 正在分析岗位 JD... {i+1}%</div>", unsafe_allow_html=True)
        elif i < 90:
            progress_text.markdown(f"<div style='text-align:center; color:#64748B;'>🤖 正在生成匹配策略... {i+1}%</div>", unsafe_allow_html=True)
        else:
            progress_text.markdown(f"<div style='text-align:center; color:#64748B;'>✨ 即将完成... {i+1}%</div>", unsafe_allow_html=True)

    st.session_state.loading = False
    st.session_state.app_stage = "result"
    st.rerun()

# ==========================================
# 7. 结果展示页面
# ==========================================
elif st.session_state.app_stage == "result":

    # 步骤指示器更新
    st.markdown("""
    <div class="step-indicator">
        <div class="step-dot completed"></div>
        <div class="step-dot active"></div>
    </div>
    """, unsafe_allow_html=True)

    # 成功状态条 + 自然返回（点击标题区即可返回，无需单独按钮）
    st.markdown("""
    <div class="success-bar">
        <span>🎉</span>
        <span>Agent 已完成深度解析，以下是实时对比视图</span>
    </div>
    """, unsafe_allow_html=True)

    # 使用更自然的返回方式 - 面包屑导航
    st.markdown("""
    <div class="back-btn" onclick="window.location.reload()">
        ← 返回重新配置
    </div>
    """, unsafe_allow_html=True)

    # 如果用户点击返回，通过按钮实现（保留但极简）
    if st.button("← 返回重新配置", key="back_btn", type="tertiary"):
        st.session_state.app_stage = "input"
        st.rerun()

    st.markdown("### 🔍 智能解析对比视图")

    # 两栏对比布局
    res_col1, res_col2 = st.columns(2, gap="large")

    with res_col1:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="icon">📄</span> 简历解析结果</div>', unsafe_allow_html=True)

        # 添加元信息
        resume_words = len(st.session_state.resume_content)
        st.markdown(f'<div style="font-size:0.8rem; color:#94A3B8; margin-bottom:0.75rem;">共提取 {resume_words} 字符 · 已结构化处理</div>', unsafe_allow_html=True)

        st.text_area(
            "简历内容", 
            value=st.session_state.resume_content, 
            height=420, 
            disabled=True, 
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col2:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="icon">🎯</span> 目标岗位 JD 视图</div>', unsafe_allow_html=True)

        jd_words = len(st.session_state.jd_content)
        st.markdown(f'<div style="font-size:0.8rem; color:#94A3B8; margin-bottom:0.75rem;">共提取 {jd_words} 字符 · 已锁定岗位上下文</div>', unsafe_allow_html=True)

        st.text_area(
            "JD 内容", 
            value=st.session_state.jd_content, 
            height=420, 
            disabled=True, 
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # 底部操作区
    st.markdown("---")
    st.markdown("<div style='text-align:center; color:#94A3B8; font-size:0.85rem; margin-top:1rem;'>💡 提示：对比视图已生成，后续可接入大模型进行智能润色与匹配分析</div>", unsafe_allow_html=True)
