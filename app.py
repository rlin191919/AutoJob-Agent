import streamlit as st
import docx
import pdfplumber
import io
import time
import re

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
# 2. 高级 CSS - 柔和蓝紫渐变 + iOS 毛玻璃
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    /* 全局背景 - 柔和蓝紫渐变 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #6dd5ed 75%, #667eea 100%) !important;
        background-size: 400% 400% !important;
        animation: gradientShift 20s ease infinite !important;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 主容器 */
    .block-container {
        padding: 2rem 3rem !important;
        max-width: 1200px !important;
    }

    /* 标题区 - 移入毛玻璃专属样式 */
    .title-glass-card {
        background: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 1.5rem 2rem;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        text-align: center;
        margin-bottom: 2.5rem;
        animation: fadeInDown 0.8s ease-out;
    }
    .main-header { 
        font-size: 2.8rem; 
        font-weight: 800; 
        color: rgba(255,255,255,0.95);
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.03em;
        text-shadow: 0 2px 20px rgba(0,0,0,0.15);
    }
    .sub-header { 
        font-size: 1.05rem; 
        color: rgba(255,255,255,0.75); 
        font-weight: 400;
        margin: 0;
    }

    /* iOS 毛玻璃卡片 */
    .glass-panel {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 2rem; 
        border-radius: 24px; 
        border: 1px solid rgba(255, 255, 255, 0.25); 
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        margin-bottom: 1.5rem;
        transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
        animation: fadeInUp 0.6s ease-out both;
    }
    .glass-panel:hover {
        transform: translateY(-6px) scale(1.005);
        background: rgba(255, 255, 255, 0.22) !important;
        box-shadow: 
            0 20px 48px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
        border-color: rgba(255, 255, 255, 0.4);
    }

    /* 卡片内标题 - 白色 */
    .glass-panel h3 {
        color: rgba(255,255,255,0.95) !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        margin-top: 0rem !important;
        margin-bottom: 1.2rem !important;
    }

    /* 🚨 核心改动：强制大模型下拉框选项列表向下展开 🚨 */
    [data-baseweb="popover"], .stSelectbox [data-baseweb="menu"] {
        bottom: auto !important;
        top: 100% !important;
        transform: translateY(4px) !important;
    }

    /* 步骤指示器 */
    .step-track {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        margin-bottom: 2.5rem;
        animation: fadeIn 0.6s ease-out 0.4s both;
    }
    .step-line {
        width: 60px;
        height: 2px;
        background: rgba(255,255,255,0.2);
        transition: all 0.4s ease;
    }
    .step-line.active {
        background: linear-gradient(90deg, rgba(255,255,255,0.6), rgba(255,255,255,0.9));
    }
    .step-node {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(255,255,255,0.1);
        border: 2px solid rgba(255,255,255,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        font-weight: 700;
        color: rgba(255,255,255,0.6);
        transition: all 0.4s ease;
    }
    .step-node.active {
        background: rgba(255,255,255,0.25);
        border-color: rgba(255,255,255,0.8);
        color: rgba(255,255,255,0.95);
        box-shadow: 0 0 20px rgba(255,255,255,0.2);
    }
    .step-node.completed {
        background: rgba(255,255,255,0.9);
        border-color: rgba(255,255,255,0.9);
        color: #667eea;
    }

    /* 状态标签 */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 1rem;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    .chip-ready {
        background: rgba(16, 185, 129, 0.25);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .chip-wait {
        background: rgba(255, 255, 255, 0.1);
        color: rgba(255,255,255,0.6);
        border: 1px solid rgba(255,255,255,0.15);
    }

    /* 主按钮 */
    .stButton > button[kind="primary"] {
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: rgba(255,255,255,0.95) !important;
        box-shadow: 
            0 4px 24px rgba(0,0,0,0.1),
            inset 0 1px 0 rgba(255,255,255,0.3) !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
        height: 52px !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: rgba(255, 255, 255, 0.35) !important;
        transform: translateY(-3px);
        box-shadow: 
            0 12px 40px rgba(0,0,0,0.2),
            inset 0 1px 0 rgba(255,255,255,0.4) !important;
    }

    /* 结果页并列大标题卡片 */
    .result-header-glass {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        text-align: center;
        animation: fadeInDown 0.6s both;
    }
    .result-header-glass h3 {
        margin: 0 !important;
        color: rgba(255,255,255,0.95) !important;
        font-weight: 700 !important;
        font-size: 1.35rem !important;
    }

    /* 结果内容卡片 */
    .result-glass {
        background: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(20px) saturate(150%) !important;
        padding: 1.8rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transition: all 0.4s ease;
        animation: slideInUp 0.6s ease-out both;
    }
    .result-glass:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }

    .result-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: rgba(255,255,255,0.95);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .result-meta {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.55);
        margin-bottom: 1rem;
    }

    /* 成功提示 */
    .success-glass {
        background: rgba(16, 185, 129, 0.2) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        color: #6ee7b7 !important;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }

    /* 输入提示框文字 */
    .hint-text {
        color: rgba(255,255,255,0.9) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.6rem !important;
    }

    /* 城市标签 */
    .city-detected {
        background: rgba(16, 185, 129, 0.2) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: #6ee7b7;
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
    }
    .city-not-detected {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
    }

    /* 文本区域与底层配置保持稳定 */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.15) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: rgba(255,255,255,0.85) !important;
    }
    .footer-hint { text-align: center; color: rgba(255,255,255,0.45); font-size: 0.85rem; margin-top: 2rem; }
    #MainMenu, footer, .stDeployButton, header { visibility: hidden; display: none !important; }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
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
    if file is None: return None
    file_bytes = file.read()
    ext = file.name.split(".")[-1].lower()
    try:
        text = ""
        if ext == "pdf":
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    if page.extract_text(): text += page.extract_text() + "\n"
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            for p in doc.paragraphs: text += p.text + "\n"
        return text.strip() if text.strip() else None
    except Exception: return None

def extract_cities_from_resume(text):
    if not text: return []
    found_cities = [city for city in CHINA_CITIES if city in text]
    return list(dict.fromkeys(found_cities))[:3]

# ==========================================
# 5. 会话状态初始化
# ==========================================
for key, val in [("app_stage", "input"), ("loading", False), ("resume_content", ""), ("jd_content", ""), ("detected_cities", [])]:
    if key not in st.session_state: st.session_state[key] = val

# ==========================================
# 6. 渲染逻辑：数据源输入页
# ==========================================
if st.session_state.app_stage == "input":

    # 标题放进毛玻璃卡片
    st.markdown("""
    <div class="title-glass-card">
        <h1 class="main-header">💼 AutoJob-Agent</h1>
        <p class="sub-header">基于大模型的智能简历精准润色与海投一体化看板</p>
    </div>
    """, unsafe_allow_html=True)

    # 进度树
    st.markdown('<div class="step-track"><div class="step-node active">1</div><div class="step-line active"></div><div class="step-node">2</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="glass-panel"><h3>📄 原始简历上传</h3>', unsafe_allow_html=True)
        uploaded_resume = st.file_uploader("上传简历", type=["pdf", "docx"], label_visibility="collapsed")
        if uploaded_resume:
            resume_text_temp = extract_text(uploaded_resume)
            if resume_text_temp: st.session_state.detected_cities = extract_cities_from_resume(resume_text_temp)
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
            jd_text_raw = st.text_area("粘贴 JD", placeholder="在此粘贴职位描述...", height=140, label_visibility="collapsed")
        else:
            uploaded_jd = st.file_uploader("上传 JD", type=["pdf", "docx"], label_visibility="collapsed")
            if uploaded_jd: jd_text_raw = extract_text(uploaded_jd)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-panel"><h3>📍 投递意向地区</h3>', unsafe_allow_html=True)
        if st.session_state.detected_cities:
            st.markdown(f'<div class="city-detected">🎯 已从简历检测到意向城市：{"、".join(st.session_state.detected_cities)}</div>', unsafe_allow_html=True)
            st.selectbox("确认意向城市", st.session_state.detected_cities + ["其他（手动输入）"], label_visibility="collapsed")
        else:
            st.markdown('<div class="city-not-detected">○ 未从简历检测到意向城市，请手动选择</div>', unsafe_allow_html=True)
            scope = st.radio("地区范围", ["国内", "海外"], horizontal=True, label_visibility="collapsed")
            st.selectbox("选择目标区域", CHINA_CITIES if scope == "国内" else OVERSEAS_COUNTRIES, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    has_res, has_jd = uploaded_resume is not None, bool(jd_text_raw and len(jd_text_raw.strip()) >= 10)
    
    col_s, col_b = st.columns([1, 2])
    col_s.markdown('<div class="status-chip chip-ready">✓ 信息已就绪</div>' if (has_res and has_jd) else '<div class="status-chip chip-wait">○ 待完善输入源数据</div>', unsafe_allow_html=True)
    
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
    p_text, p_bar = st.empty(), st.progress(0)
    stages = [("📄 解析简历结构", 30), ("🎯 分析岗位 JD", 60), ("🤖 生成匹配策略", 90), ("✨ 即将完成", 100)]
    for i in range(100):
        time.sleep(0.02)
        p_bar.progress(i + 1)
        for text, threshold in stages:
            if i < threshold:
                p_text.markdown(f"<div style='text-align:center; color:white; font-weight:500;'>{text} {i+1}%</div>", unsafe_allow_html=True)
                break
    st.session_state.loading, st.session_state.app_stage = False, "result"
    st.rerun()

# ==========================================
# 8. 渲染逻辑：结果展现页
# ==========================================
elif st.session_state.app_stage == "result":

    # 结果页的标题也塞进专属毛玻璃卡片
    st.markdown("""
    <div class="result-header-glass">
        <h3>🔍 智能解析对比看板</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="step-track"><div class="step-node completed">✓</div><div class="step-line active"></div><div class="step-node active">2</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="success-glass">🎉 Agent 已完成深度解析，以下是实时多维对比视图</div>', unsafe_allow_html=True)

    if st.button("← 返回修改数据", key="back_btn"):
        st.session_state.app_stage = "input"
        st.rerun()

    res_col1, res_col2 = st.columns(2, gap="large")

    with res_col1:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">📄 简历解析结果</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.resume_content)} 字符 · 数据已完全解构</div>', unsafe_allow_html=True)
        st.text_area("R", value=st.session_state.resume_content, height=420, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col2:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">🎯 目标岗位 JD</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.jd_content)} 字符 · 上下文已注入容器</div>', unsafe_allow_html=True)
        st.text_area("J", value=st.session_state.jd_content, height=420, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='footer-hint'>💡 对比视图已生成，后续可接入大模型进行智能润色与匹配分析</div>", unsafe_allow_html=True)
