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
# 2. 高级 CSS - 极致紧凑 iOS 毛玻璃 + 强制原位下拉
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    /* 全局网页背景 - 柔和蓝紫渐变流动 */
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

    /* 主内容外边距与最大宽度限制 */
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 1100px !important;
    }

    /* 标题区专用毛玻璃卡片样式（稍微收紧） */
    .title-glass-card {
        background: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 1rem 1.5rem;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        text-align: center;
        margin-bottom: 1.5rem;
        animation: fadeInDown 0.8s ease-out;
    }
    .main-header { 
        font-size: 2.4rem; 
        font-weight: 800; 
        color: rgba(255,255,255,0.95);
        margin: 0 0 0.2rem 0;
        letter-spacing: -0.03em;
    }
    .sub-header { 
        font-size: 0.95rem; 
        color: rgba(255,255,255,0.75); 
        margin: 0;
    }

    /* 🧠 核心修改：极致瘦身版 iOS 毛玻璃卡片（Padding 从 2rem 缩减到 1rem，紧凑致密） */
    .glass-panel {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 1rem 1.25rem !important; /* 极大收紧内边距 */
        border-radius: 16px; /* 圆角略微调小，更贴合紧凑风格 */
        border: 1px solid rgba(255, 255, 255, 0.23); 
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 0.75rem !important; /* 缩短卡片之间的上下间距 */
        transition: all 0.4s ease;
        animation: fadeInUp 0.6s ease-out both;
    }
    .glass-panel:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.2) !important;
    }

    /* 卡片内小标题样式（变小且紧凑） */
    .glass-panel h3 {
        color: rgba(255,255,255,0.95) !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important; /* 字体略微缩小 */
        margin-top: 0rem !important;
        margin-bottom: 0.75rem !important; /* 缩短标题与内容的距离 */
    }

    /* 🚨 降维打击改动：强力击碎 React 动态生成的浮层，死锁向下弹出，限制高度 🚨 */
    div[data-baseweb="popover"] {
        top: auto !important;
        bottom: auto !important;
        margin-top: 2px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="popover"] > div {
        max-height: 160px !important; /* 限制最大高度，让其必有滚动条，防触发上弹 */
        overflow-y: auto !important;
    }
    [data-baseweb="menu"] {
        background-color: rgba(255, 255, 255, 0.98) !important;
        border-radius: 10px !important;
        max-height: 160px !important;
        overflow-y: auto !important;
    }
    [data-baseweb="menu"] li {
        color: #1e293b !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 6px 12px !important; /* 选项行高变紧凑 */
    }
    [data-baseweb="menu"] li:hover {
        background-color: #f1f5f9 !important;
    }

    /* 极简流式步骤指示器 */
    .step-track {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        margin-bottom: 1.5rem;
    }
    .step-line { width: 50px; height: 2px; background: rgba(255,255,255,0.2); }
    .step-line.active { background: linear-gradient(90deg, rgba(255,255,255,0.6), rgba(255,255,255,0.9)); }
    .step-node {
        width: 30px; height: 30px; border-radius: 50%;
        background: rgba(255,255,255,0.1); border: 2px solid rgba(255,255,255,0.3);
        display: flex; align-items: center; justify-content: center;
        font-size: 0.8rem; font-weight: 700; color: rgba(255,255,255,0.6);
    }
    .step-node.active { background: rgba(255,255,255,0.25); border-color: rgba(255,255,255,0.8); color: rgba(255,255,255,0.95); }
    .step-node.completed { background: rgba(255,255,255,0.9); border-color: rgba(255,255,255,0.9); color: #667eea; }

    /* 状态指示胶囊 */
    .status-chip {
        display: inline-flex; align-items: center; gap: 0.3rem;
        padding: 0.25rem 0.75rem; border-radius: 100px;
        font-size: 0.75rem; font-weight: 600;
    }
    .chip-ready { background: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }
    .chip-wait { background: rgba(255, 255, 255, 0.1); color: rgba(255,255,255,0.6); border: 1px solid rgba(255,255,255,0.15); }

    /* 高级发光主操作按钮 */
    .stButton > button[kind="primary"] {
        background: rgba(255, 255, 255, 0.25) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: rgba(255,255,255,0.95) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        height: 44px !important; /* 按钮高度微调，更精致 */
    }
    .stButton > button[kind="primary"]:hover {
        background: rgba(255, 255, 255, 0.35) !important;
        transform: translateY(-2px);
    }

    /* 地区感知卡片配色 */
    .city-detected {
        background: rgba(16, 185, 129, 0.15) !important;
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        border-radius: 8px; padding: 0.5rem 0.75rem;
        color: #6ee7b7; font-size: 0.85rem; margin-bottom: 0.75rem;
    }
    .city-not-detected {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 8px; padding: 0.5rem 0.75rem;
        color: rgba(255,255,255,0.65); font-size: 0.85rem; margin-bottom: 0.75rem;
    }

    /* 文本输入框相关间距调整 */
    .hint-text { color: rgba(255,255,255,0.9) !important; font-weight: 600 !important; font-size: 0.85rem !important; margin-bottom: 0.4rem !important; }
    .stTextArea textarea { background: rgba(0, 0, 0, 0.15) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 10px !important; color: rgba(255,255,255,0.85) !important; }
    
    /* 结果页大标题卡片样式 */
    .result-header-glass {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        padding: 1rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.25);
        margin-bottom: 1.5rem; text-align: center;
    }
    .result-header-glass h3 { margin: 0 !important; color: rgba(255,255,255,0.95) !important; font-weight: 700 !important; font-size: 1.2rem !important; }
    .result-glass { background: rgba(255, 255, 255, 0.12) !important; backdrop-filter: blur(20px) saturate(150%) !important; padding: 1.25rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.2); }
    .result-title { font-size: 1rem; font-weight: 700; color: rgba(255,255,255,0.95); margin-bottom: 0.25rem; }
    .result-meta { font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-bottom: 0.75rem; }
    .success-glass { background: rgba(16, 185, 129, 0.2) !important; backdrop-filter: blur(16px) !important; border: 1px solid rgba(16, 185, 129, 0.3) !important; color: #6ee7b7 !important; padding: 0.6rem 1.2rem; border-radius: 10px; font-weight: 500; margin-bottom: 1rem; }

    .footer-hint { text-align: center; color: rgba(255,255,255,0.45); font-size: 0.8rem; margin-top: 1.5rem; }
    #MainMenu, footer, .stDeployButton, header { visibility: hidden; display: none !important; }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-15px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
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

    # 标题毛玻璃卡片
    st.markdown("""
    <div class="title-glass-card">
        <h1 class="main-header">💼 AutoJob-Agent</h1>
        <p class="sub-header">基于大模型的智能简历精准润色与海投一体化看板</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="step-track"><div class="step-node active">1</div><div class="step-line active"></div><div class="step-node">2</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        # 紧凑卡片 1
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

        # 紧凑卡片 2
        st.markdown('<div class="glass-panel"><h3>🤖 智能投递意向</h3>', unsafe_allow_html=True)
        st.selectbox("意向公司类型", ["大厂", "独角兽", "国央企", "外企/跨国公司", "中小型科技公司"])
        st.selectbox("大模型内核", ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude 3.5"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 紧凑卡片 3
        st.markdown('<div class="glass-panel"><h3>🎯 目标岗位 JD</h3>', unsafe_allow_html=True)
        jd_method = st.radio("提供方式", ["手动粘贴文本", "上传 JD 文档"], horizontal=True, label_visibility="collapsed")
        jd_text_raw = ""
        if jd_method == "手动粘贴文本":
            st.markdown('<div class="hint-text">请把招聘软件上的职位描述(JD)粘贴在这里</div>', unsafe_allow_html=True)
            jd_text_raw = st.text_area("粘贴 JD", placeholder="在此粘贴职位描述...", height=110, label_visibility="collapsed")
        else:
            uploaded_jd = st.file_uploader("上传 JD", type=["pdf", "docx"], label_visibility="collapsed")
            if uploaded_jd: jd_text_raw = extract_text(uploaded_jd)
        st.markdown('</div>', unsafe_allow_html=True)

        # 紧凑卡片 4
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
        time.sleep(0.015)
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
        st.markdown('<div class="result-title">📄 简历解析 results</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.resume_content)} 字符 · 数据已完全解构</div>', unsafe_allow_html=True)
        st.text_area("R", value=st.session_state.resume_content, height=400, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col2:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">🎯 目标岗位 JD</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-meta">{len(st.session_state.jd_content)} 字符 · 上下文已注入容器</div>', unsafe_allow_html=True)
        st.text_area("J", value=st.session_state.jd_content, height=400, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='footer-hint'>💡 对比视图已生成，后续可接入大模型进行智能润色与匹配分析</div>", unsafe_allow_html=True)
