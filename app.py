import streamlit as st
import docx
import pdfplumber
import io
import time

# ==========================================
# 1. 页面配置
# ==========================================
st.set_page_config(
    page_title="AutoJob-Agent | 智能海投系统",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. 高级 CSS - 紧凑毛玻璃 + 原位下拉 + 微交互动画
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 26%, #f093fb 52%, #6dd5ed 76%, #667eea 100%) !important;
        background-size: 420% 420% !important;
        animation: gradientShift 18s ease infinite !important;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .block-container {
        padding: 1.15rem 1.6rem !important;
        max-width: 1060px !important;
    }

    .title-glass-card {
        background: rgba(255, 255, 255, 0.13) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 0.9rem 1.2rem;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.22);
        box-shadow: 0 10px 30px rgba(31, 38, 135, 0.16);
        text-align: center;
        margin-bottom: 1.05rem;
        animation: fadeInDown 0.75s ease-out both;
        transition: 0.35s ease;
    }

    .title-glass-card:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        transform: translateY(-2px);
    }

    .main-header {
        font-size: 2.25rem;
        font-weight: 800;
        color: rgba(255,255,255,0.96);
        margin: 0 0 0.15rem 0;
        letter-spacing: -0.02em;
    }

    .sub-header {
        font-size: 0.92rem;
        color: rgba(255,255,255,0.76);
        margin: 0;
    }

    /* 瘦身后的毛玻璃卡片：更小 padding、更小间距，紧紧包裹内容 */
    .glass-panel {
        background: rgba(255, 255, 255, 0.145) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 0.78rem 0.95rem 0.82rem !important;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.24);
        box-shadow: 0 6px 22px rgba(31, 38, 135, 0.13);
        margin-bottom: 0.65rem !important;
        transition: transform 0.28s ease, background 0.28s ease, border-color 0.28s ease, box-shadow 0.28s ease;
        animation: fadeInUp 0.58s ease-out both;
    }

    .glass-panel:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.205) !important;
        border-color: rgba(255, 255, 255, 0.36);
        box-shadow: 0 10px 28px rgba(31, 38, 135, 0.18);
    }

    .glass-panel h3 {
        color: rgba(255,255,255,0.96) !important;
        font-weight: 750 !important;
        font-size: 1.02rem !important;
        margin: 0 0 0.58rem 0 !important;
        letter-spacing: 0;
    }

    /* Streamlit 组件整体收紧 */
    div[data-testid="stVerticalBlock"] {
        gap: 0.42rem !important;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 1rem !important;
    }

    div[data-testid="stWidgetLabel"] {
        min-height: 0 !important;
    }

    div[data-testid="stFileUploader"] {
        padding-top: 0 !important;
    }

    div[data-testid="stFileUploader"] section {
        padding: 0.62rem !important;
        border-radius: 12px !important;
        background: rgba(255,255,255,0.1) !important;
        border: 1px dashed rgba(255,255,255,0.32) !important;
        transition: 0.25s ease;
    }

    div[data-testid="stFileUploader"] section:hover {
        background: rgba(255,255,255,0.16) !important;
        border-color: rgba(255,255,255,0.55) !important;
    }

    /* 输入框、选择框、文本域微交互 */
    .stTextArea textarea,
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] input {
        background: rgba(20, 24, 44, 0.2) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 10px !important;
        color: rgba(255,255,255,0.9) !important;
        transition: background 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
    }

    .stTextArea textarea:hover,
    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="input"] input:hover {
        background: rgba(255,255,255,0.16) !important;
        border-color: rgba(255,255,255,0.44) !important;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.08) !important;
    }

    .stTextArea textarea:focus,
    div[data-baseweb="select"] > div:focus-within,
    div[data-baseweb="input"] input:focus {
        background: rgba(255,255,255,0.18) !important;
        border-color: rgba(255,255,255,0.62) !important;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.13) !important;
    }

    div[data-baseweb="select"] {
        min-height: 38px !important;
    }

    div[data-baseweb="select"] > div {
        min-height: 38px !important;
    }

    div[data-baseweb="select"] span {
        color: rgba(255,255,255,0.92) !important;
        font-size: 0.88rem !important;
    }

    /* 彻底限制下拉层高度：原位向下展开，内部滚动 */
    div[data-baseweb="popover"] {
        z-index: 999999 !important;
        margin-top: 4px !important;
        transform-origin: top center !important;
        animation: dropdownOpen 0.18s ease-out both !important;
        filter: drop-shadow(0 12px 26px rgba(15, 23, 42, 0.22)) !important;
    }

    div[data-baseweb="popover"] > div {
        max-height: 172px !important;
        overflow: hidden !important;
        border-radius: 12px !important;
    }

    [data-baseweb="menu"] {
        max-height: 172px !important;
        overflow-y: auto !important;
        overscroll-behavior: contain !important;
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(18px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
        border: 1px solid rgba(255,255,255,0.65) !important;
        border-radius: 12px !important;
        padding: 0.28rem !important;
    }

    [data-baseweb="menu"] ul {
        max-height: 172px !important;
        overflow-y: auto !important;
    }

    [data-baseweb="menu"] li {
        color: #1e293b !important;
        font-weight: 560 !important;
        font-size: 0.84rem !important;
        line-height: 1.25 !important;
        padding: 7px 10px !important;
        border-radius: 8px !important;
        transition: background 0.16s ease, color 0.16s ease, transform 0.16s ease;
    }

    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] li[aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102,126,234,0.14), rgba(240,147,251,0.16)) !important;
        color: #334155 !important;
        transform: translateX(2px);
    }

    [data-baseweb="menu"]::-webkit-scrollbar,
    [data-baseweb="menu"] ul::-webkit-scrollbar {
        width: 5px;
    }

    [data-baseweb="menu"]::-webkit-scrollbar-track,
    [data-baseweb="menu"] ul::-webkit-scrollbar-track {
        background: transparent;
    }

    [data-baseweb="menu"]::-webkit-scrollbar-thumb,
    [data-baseweb="menu"] ul::-webkit-scrollbar-thumb {
        background: rgba(100, 116, 139, 0.34);
        border-radius: 999px;
    }

    [data-baseweb="menu"]::-webkit-scrollbar-thumb:hover,
    [data-baseweb="menu"] ul::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 116, 139, 0.55);
    }

    @keyframes dropdownOpen {
        from { opacity: 0; transform: translateY(-5px) scale(0.985); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .step-track {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        margin-bottom: 1.05rem;
    }

    .step-line {
        width: 46px;
        height: 2px;
        background: rgba(255,255,255,0.22);
    }

    .step-line.active {
        background: linear-gradient(90deg, rgba(255,255,255,0.55), rgba(255,255,255,0.92));
    }

    .step-node {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: rgba(255,255,255,0.12);
        border: 2px solid rgba(255,255,255,0.34);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.78rem;
        font-weight: 750;
        color: rgba(255,255,255,0.68);
        transition: 0.25s ease;
    }

    .step-node:hover {
        background: rgba(255,255,255,0.22);
        color: white;
        transform: scale(1.05);
    }

    .step-node.active {
        background: rgba(255,255,255,0.26);
        border-color: rgba(255,255,255,0.85);
        color: rgba(255,255,255,0.96);
    }

    .step-node.completed {
        background: rgba(255,255,255,0.92);
        border-color: rgba(255,255,255,0.92);
        color: #667eea;
    }

    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.32rem;
        padding: 0.24rem 0.68rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 650;
        transition: 0.22s ease;
    }

    .status-chip:hover {
        transform: translateY(-1px);
        filter: brightness(1.08);
    }

    .chip-ready {
        background: rgba(16, 185, 129, 0.24);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.34);
    }

    .chip-wait {
        background: rgba(255, 255, 255, 0.11);
        color: rgba(255,255,255,0.68);
        border: 1px solid rgba(255,255,255,0.17);
    }

    .stButton > button {
        transition: background 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
    }

    .stButton > button[kind="primary"] {
        background: rgba(255, 255, 255, 0.24) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.42) !important;
        color: rgba(255,255,255,0.96) !important;
        border-radius: 12px !important;
        font-weight: 680 !important;
        height: 42px !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: rgba(255, 255, 255, 0.36) !important;
        border-color: rgba(255,255,255,0.7) !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(31, 38, 135, 0.18);
    }

    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.13) !important;
        color: rgba(255,255,255,0.9) !important;
        border: 1px solid rgba(255,255,255,0.24) !important;
        border-radius: 11px !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(255,255,255,0.22) !important;
        transform: translateY(-1px);
    }

    .city-detected,
    .city-not-detected {
        border-radius: 9px;
        padding: 0.46rem 0.65rem;
        font-size: 0.82rem;
        margin-bottom: 0.52rem;
        transition: 0.25s ease;
    }

    .city-detected {
        background: rgba(16, 185, 129, 0.16) !important;
        border: 1px solid rgba(16, 185, 129, 0.28) !important;
        color: #6ee7b7;
    }

    .city-not-detected {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255,255,255,0.13) !important;
        color: rgba(255,255,255,0.68);
    }

    .city-detected:hover,
    .city-not-detected:hover {
        background: rgba(255,255,255,0.16) !important;
        border-color: rgba(255,255,255,0.35) !important;
    }

    .hint-text {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 650 !important;
        font-size: 0.82rem !important;
        margin: 0 0 0.35rem 0 !important;
    }

    .stTextArea textarea {
        min-height: 108px !important;
    }

    .result-header-glass {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 0.9rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        margin-bottom: 1.05rem;
        text-align: center;
        animation: fadeInDown 0.65s ease-out both;
    }

    .result-header-glass h3 {
        margin: 0 !important;
        color: rgba(255,255,255,0.96) !important;
        font-weight: 760 !important;
        font-size: 1.15rem !important;
    }

    .result-glass {
        background: rgba(255, 255, 255, 0.13) !important;
        backdrop-filter: blur(20px) saturate(150%) !important;
        padding: 1rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.22);
        transition: 0.28s ease;
        animation: fadeInUp 0.6s ease-out both;
    }

    .result-glass:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        transform: translateY(-2px);
    }

    .result-title {
        font-size: 0.98rem;
        font-weight: 750;
        color: rgba(255,255,255,0.96);
        margin-bottom: 0.2rem;
    }

    .result-meta {
        font-size: 0.74rem;
        color: rgba(255,255,255,0.56);
        margin-bottom: 0.62rem;
    }

    .success-glass {
        background: rgba(16, 185, 129, 0.2) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(16, 185, 129, 0.34) !important;
        color: #6ee7b7 !important;
        padding: 0.58rem 1rem;
        border-radius: 10px;
        font-weight: 560;
        margin-bottom: 0.88rem;
        animation: fadeInUp 0.55s ease-out both;
    }

    .footer-hint {
        text-align: center;
        color: rgba(255,255,255,0.48);
        font-size: 0.78rem;
        margin-top: 1.15rem;
    }

    hr {
        margin: 0.75rem 0 0.85rem !important;
        border-color: rgba(255,255,255,0.18) !important;
    }

    #MainMenu,
    footer,
    .stDeployButton,
    header {
        visibility: hidden;
        display: none !important;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-14px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(14px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 基础配置城市数据
# ==========================================
CHINA_CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "重庆", "苏州", "长沙", "东莞", "珠海"]
OVERSEAS_COUNTRIES = ["美国", "英国", "加拿大", "澳大利亚", "新加坡", "日本", "其他"]

# ==========================================
# 4. 文本解析函数
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
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            for p in doc.paragraphs:
                text += p.text + "\n"

        return text.strip() if text.strip() else None

    except Exception:
        return None


def extract_cities_from_resume(text):
    if not text:
        return []

    found_cities = [city for city in CHINA_CITIES if city in text]
    return list(dict.fromkeys(found_cities))[:3]


# ==========================================
# 5. 会话状态初始化
# ==========================================
for key, val in [
    ("app_stage", "input"),
    ("loading", False),
    ("resume_content", ""),
    ("jd_content", ""),
    ("detected_cities", [])
]:
    if key not in st.session_state:
        st.session_state[key] = val


# ==========================================
# 6. 渲染逻辑：数据源输入页
# ==========================================
if st.session_state.app_stage == "input":

    st.markdown("""
    <div class="title-glass-card">
        <h1 class="main-header">💼 AutoJob-Agent</h1>
        <p class="sub-header">基于大模型的智能简历精准润色与海投一体化看板</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="step-track">'
        '<div class="step-node active">1</div>'
        '<div class="step-line active"></div>'
        '<div class="step-node">2</div>'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="glass-panel"><h3>📄 原始简历上传</h3>', unsafe_allow_html=True)
        uploaded_resume = st.file_uploader("上传简历", type=["pdf", "docx"], label_visibility="collapsed")

        if uploaded_resume:
            resume_text_temp = extract_text(uploaded_resume)
            if resume_text_temp:
                st.session_state.detected_cities = extract_cities_from_resume(resume_text_temp)
            st.markdown(f'<div class="status-chip chip-ready">✓ {uploaded_resume.name}</div>', unsafe_allow_html=True)
        else:
            st.session_state.detected_cities = []
            st.markdown('<div class="status-chip chip-wait">○ 等待上传</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-panel"><h3>🤖 智能投递意向</h3>', unsafe_allow_html=True)
        st.selectbox("意向公司类型", ["大厂", "独角兽", "国央企", "外企/跨国公司", "中小型科技公司"])
        st.selectbox("大模型内核", ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude 3.5"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-panel"><h3>🎯 目标岗位 JD</h3>', unsafe_allow_html=True)
        jd_method = st.radio("提供方式", ["手动粘贴文本", "上传 JD 文档"], horizontal=True, label_visibility="collapsed")
        jd_text_raw = ""

        if jd_method == "手动粘贴文本":
            st.markdown('<div class="hint-text">请把招聘软件上的职位描述(JD)粘贴在这里</div>', unsafe_allow_html=True)
            jd_text_raw = st.text_area(
                "粘贴 JD",
                placeholder="在此粘贴职位描述...",
                height=110,
                label_visibility="collapsed"
            )
        else:
            uploaded_jd = st.file_uploader("上传 JD", type=["pdf", "docx"], label_visibility="collapsed")
            if uploaded_jd:
                jd_text_raw = extract_text(uploaded_jd)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-panel"><h3>📍 投递意向地区</h3>', unsafe_allow_html=True)

        if st.session_state.detected_cities:
            st.markdown(
                f'<div class="city-detected">🎯 已从简历检测到意向城市：{"、".join(st.session_state.detected_cities)}</div>',
                unsafe_allow_html=True
            )
            st.selectbox(
                "确认意向城市",
                st.session_state.detected_cities + ["其他（手动输入）"],
                label_visibility="collapsed"
            )
        else:
            st.markdown(
                '<div class="city-not-detected">○ 未从简历检测到意向城市，请手动选择</div>',
                unsafe_allow_html=True
            )
            scope = st.radio("地区范围", ["国内", "海外"], horizontal=True, label_visibility="collapsed")
            st.selectbox(
                "选择目标区域",
                CHINA_CITIES if scope == "国内" else OVERSEAS_COUNTRIES,
                label_visibility="collapsed"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    has_res = uploaded_resume is not None
    has_jd = bool(jd_text_raw and len(jd_text_raw.strip()) >= 10)

    col_s, col_b = st.columns([1, 2])

    col_s.markdown(
        '<div class="status-chip chip-ready">✓ 信息已就绪</div>'
        if (has_res and has_jd)
        else '<div class="status-chip chip-wait">○ 待完善输入源数据</div>',
        unsafe_allow_html=True
    )

    with col_b:
        if st.button("✨ 一键开始智能匹配", use_container_width=True, disabled=not (has_res and has_jd)):
            st.session_state.resume_content = extract_text(uploaded_resume)
            st.session_state.jd_content = jd_text_raw
            st.session_state.loading = True
            st.rerun()


# ==========================================
# 7. 渲染逻辑：流式加载中
# ==========================================
elif st.session_state.loading:
    p_text = st.empty()
    p_bar = st.progress(0)

    stages = [
        ("📄 解析简历结构", 30),
        ("🎯 分析岗位 JD", 60),
        ("🤖 生成匹配策略", 90),
        ("✨ 即将完成", 100)
    ]

    for i in range(100):
        time.sleep(0.015)
        p_bar.progress(i + 1)

        for text, threshold in stages:
            if i < threshold:
                p_text.markdown(
                    f"<div style='text-align:center; color:white; font-weight:600;'>{text} {i + 1}%</div>",
                    unsafe_allow_html=True
                )
                break

    st.session_state.loading = False
    st.session_state.app_stage = "result"
    st.rerun()


# ==========================================
# 8. 渲染逻辑：结果展现页
# ==========================================
elif st.session_state.app_stage == "result":

    st.markdown("""
    <div class="result-header-glass">
        <h3>🔍 智能解析对比看板</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="step-track">'
        '<div class="step-node completed">✓</div>'
        '<div class="step-line active"></div>'
        '<div class="step-node active">2</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="success-glass">🎉 Agent 已完成深度解析，以下是实时多维对比视图</div>',
        unsafe_allow_html=True
    )

    if st.button("← 返回修改数据", key="back_btn"):
        st.session_state.app_stage = "input"
        st.rerun()

    res_col1, res_col2 = st.columns(2, gap="large")

    with res_col1:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">📄 简历解析 results</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="result-meta">{len(st.session_state.resume_content)} 字符 · 数据已完全解构</div>',
            unsafe_allow_html=True
        )
        st.text_area(
            "R",
            value=st.session_state.resume_content,
            height=400,
            disabled=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col2:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">🎯 目标岗位 JD</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="result-meta">{len(st.session_state.jd_content)} 字符 · 上下文已注入容器</div>',
            unsafe_allow_html=True
        )
        st.text_area(
            "J",
            value=st.session_state.jd_content,
            height=400,
            disabled=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        "<div class='footer-hint'>💡 对比视图已生成，后续可接入大模型进行智能润色与匹配分析</div>",
        unsafe_allow_html=True
    )
