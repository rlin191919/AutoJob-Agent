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

    /* 标题区 - 极简白色文字 */
    .title-container { 
        text-align: center; 
        margin-bottom: 2.5rem; 
        animation: fadeInDown 0.8s ease-out;
    }
    .main-header { 
        font-size: 3rem; 
        font-weight: 800; 
        color: rgba(255,255,255,0.95);
        margin-bottom: 0.5rem;
        letter-spacing: -0.03em;
        text-shadow: 0 2px 20px rgba(0,0,0,0.15);
    }
    .sub-header { 
        font-size: 1.05rem; 
        color: rgba(255,255,255,0.7); 
        font-weight: 400;
        animation: fadeInUp 0.8s ease-out 0.2s both;
    }

    /* iOS 毛玻璃卡片 - 核心效果 */
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
        font-size: 1.15rem !important;
        margin-bottom: 1.2rem !important;
    }

    /* 步骤指示器 - 极简 */
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

    /* 状态标签 - 毛玻璃风格 */
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

    /* 主按钮 - 发光玻璃效果 */
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
    .stButton > button[kind="primary"]:active {
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"]:disabled {
        background: rgba(255,255,255,0.08) !important;
        border-color: rgba(255,255,255,0.15) !important;
        color: rgba(255,255,255,0.35) !important;
    }

    /* 返回按钮 - 极简 */
    .back-link {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        padding: 0.5rem 0;
        margin-bottom: 1.5rem;
        background: none;
        border: none;
    }
    .back-link:hover {
        color: rgba(255,255,255,0.95);
        gap: 0.7rem;
    }

    /* 结果页卡片 */
    .result-glass {
        background: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(20px) saturate(150%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(150%) !important;
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
    .result-glass:nth-child(2) { animation-delay: 0.15s; }

    .result-title {
        font-size: 1rem;
        font-weight: 700;
        color: rgba(255,255,255,0.95);
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .result-meta {
        font-size: 0.8rem;
        color: rgba(255,255,255,0.55);
        margin-bottom: 1rem;
    }

    /* 成功提示 - 毛玻璃 */
    .success-glass {
        background: rgba(16, 185, 129, 0.2) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        color: #6ee7b7 !important;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 500;
        animation: slideInDown 0.5s ease-out;
        margin-bottom: 1.5rem;
    }

    /* 加载动画 - 极简 */
    .loader-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 0;
        animation: fadeIn 0.3s ease;
    }
    .loader-ring {
        width: 48px;
        height: 48px;
        border: 3px solid rgba(255,255,255,0.15);
        border-top-color: rgba(255,255,255,0.9);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    .loader-text {
        margin-top: 1.5rem;
        color: rgba(255,255,255,0.7);
        font-size: 0.95rem;
        font-weight: 500;
    }

    /* 分割线 - 柔和 */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
        margin: 2rem 0 !important;
    }

    /* 文本区域 - 深色玻璃 */
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.15) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: rgba(255,255,255,0.85) !important;
        transition: all 0.3s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: rgba(255,255,255,0.4) !important;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.1) !important;
        background: rgba(0, 0, 0, 0.2) !important;
    }
    .stTextArea textarea::placeholder {
        color: rgba(255,255,255,0.4) !important;
    }

    /* 选择器 - 玻璃风格 */
    .stSelectbox > div > div {
        background: rgba(0, 0, 0, 0.15) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: rgba(255,255,255,0.9) !important;
    }
    .stSelectbox > div > div:hover {
        border-color: rgba(255,255,255,0.3) !important;
    }

    /* 强制下拉列表向下展开 - 覆盖 baseweb 默认行为 */
    .stSelectbox [data-baseweb="select"] [data-baseweb="popover"],
    .stSelectbox [data-baseweb="select"] [role="listbox"],
    .stSelectbox [data-baseweb="select"] > div:nth-child(2),
    .stSelectbox [data-baseweb="menu"] {
        top: 100% !important;
        bottom: auto !important;
        margin-top: 4px !important;
        margin-bottom: 0 !important;
    }

    /* 文件上传器 */
    .stFileUploader > div {
        background: rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(8px) !important;
        border: 2px dashed rgba(255,255,255,0.2) !important;
        border-radius: 16px !important;
        transition: all 0.3s ease !important;
    }
    .stFileUploader > div:hover {
        border-color: rgba(255,255,255,0.4) !important;
        background: rgba(0, 0, 0, 0.15) !important;
    }

    /* 单选按钮 - 白色 */
    .stRadio > div {
        color: rgba(255,255,255,0.8) !important;
    }
    .stRadio > div > div > label {
        color: rgba(255,255,255,0.8) !important;
    }

    /* 底部提示 */
    .footer-hint {
        text-align: center;
        color: rgba(255,255,255,0.45);
        font-size: 0.85rem;
        margin-top: 2rem;
    }

    /* 关键帧 */
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
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideInDown {
        from { opacity: 0; transform: translateY(-15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none !important;}
    header {visibility: hidden;}

    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.2);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.3);
    }

    /* 黑体提示文字 */
    .hint-text {
        color: rgba(255,255,255,0.95) !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* 城市选择区域 */
    .city-detected {
        background: rgba(16, 185, 129, 0.2) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: #6ee7b7;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.4s ease;
    }
    .city-not-detected {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(8px) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    /* 卡片标题样式 - 确保在毛玻璃内 */
    .card-header {
        color: rgba(255,255,255,0.95);
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 城市数据
# ==========================================
CHINA_CITIES = [
    "北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京", "西安", "重庆",
    "天津", "苏州", "长沙", "郑州", "青岛", "大连", "厦门", "宁波", "无锡", "佛山",
    "济南", "合肥", "福州", "东莞", "昆明", "沈阳", "哈尔滨", "长春", "石家庄", "太原",
    "南昌", "贵阳", "南宁", "兰州", "海口", "乌鲁木齐", "呼和浩特", "银川", "西宁", "拉萨",
    "温州", "常州", "南通", "徐州", "烟台", "泉州", "唐山", "珠海", "惠州", "中山"
]

OVERSEAS_COUNTRIES = [
    "美国", "英国", "加拿大", "澳大利亚", "德国", "法国", "日本", "新加坡", "荷兰", "瑞典",
    "瑞士", "新西兰", "爱尔兰", "丹麦", "挪威", "芬兰", "奥地利", "比利时", "卢森堡", "其他"
]

# ==========================================
# 4. 文本提取函数
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

def extract_cities_from_resume(text):
    """从简历文本中提取意向城市"""
    if not text:
        return []

    found_cities = []
    for city in CHINA_CITIES:
        if city in text:
            found_cities.append(city)

    return list(dict.fromkeys(found_cities))[:3]

# ==========================================
# 5. 状态管理
# ==========================================
if "app_stage" not in st.session_state:
    st.session_state.app_stage = "input"
if "loading" not in st.session_state:
    st.session_state.loading = False
if "resume_content" not in st.session_state:
    st.session_state.resume_content = ""
if "jd_content" not in st.session_state:
    st.session_state.jd_content = ""
if "detected_cities" not in st.session_state:
    st.session_state.detected_cities = []
if "city_scope" not in st.session_state:
    st.session_state.city_scope = "国内"
if "selected_city" not in st.session_state:
    st.session_state.selected_city = None
if "custom_city" not in st.session_state:
    st.session_state.custom_city = ""

# ==========================================
# 6. 标题区
# ==========================================
st.markdown("""
<div class="title-container">
    <div class="main-header">💼 AutoJob-Agent</div>
    <div class="sub-header">基于大模型的智能简历精准润色与海投一体化看板</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 7. 输入页面
# ==========================================
if st.session_state.app_stage == "input":

    # 步骤指示器
    st.markdown("""
    <div class="step-track">
        <div class="step-node active">1</div>
        <div class="step-line active"></div>
        <div class="step-node">2</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        # === 简历上传 - 标题在毛玻璃内 ===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📄 原始简历上传</div>', unsafe_allow_html=True)

        uploaded_resume = st.file_uploader(
            "支持 PDF 或 DOCX", 
            type=["pdf", "docx"], 
            label_visibility="collapsed"
        )

        if uploaded_resume:
            resume_text_temp = extract_text(uploaded_resume)
            if resume_text_temp:
                detected = extract_cities_from_resume(resume_text_temp)
                st.session_state.detected_cities = detected
            st.markdown(f'<div class="status-chip chip-ready">✓ {uploaded_resume.name}</div>', unsafe_allow_html=True)
        else:
            st.session_state.detected_cities = []
            st.markdown('<div class="status-chip chip-wait">○ 等待上传</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # === 智能投递意向 - 标题在毛玻璃内 ===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🤖 智能投递意向</div>', unsafe_allow_html=True)

        target_company = st.selectbox(
            "意向公司类型", 
            ["大厂", "独角兽", "国央企", "外企/跨国公司", "中小型科技公司", "不限"]
        )
        model_provider = st.selectbox(
            "大模型内核", 
            ["DeepSeek-V3 (推荐)", "GPT-4o", "Claude 3.5"]
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # === 目标岗位 JD - 标题在毛玻璃内 ===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🎯 目标岗位 JD</div>', unsafe_allow_html=True)

        jd_input_method = st.radio(
            "提供方式", 
            ["手动粘贴文本", "上传 JD 文档"], 
            horizontal=True,
            label_visibility="collapsed"
        )

        jd_text_raw = ""
        if jd_input_method == "手动粘贴文本":
            st.markdown('<div class="hint-text">请把招聘软件上的职位描述(JD)粘贴在这里</div>', unsafe_allow_html=True)
            jd_text_raw = st.text_area(
                "粘贴 JD", 
                placeholder="在此粘贴职位描述...", 
                height=140,
                label_visibility="collapsed"
            )
        else:
            uploaded_jd = st.file_uploader(
                "上传 JD", 
                type=["pdf", "docx"],
                label_visibility="collapsed"
            )
            if uploaded_jd: 
                jd_text_raw = extract_text(uploaded_jd)

        if jd_text_raw:
            word_count = len(jd_text_raw.strip())
            st.markdown(f'<div style="text-align:right; font-size:0.8rem; color:rgba(255,255,255,0.5); margin-top:0.5rem;">{word_count} 字符</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # === 投递意向地区 - 标题在毛玻璃内 ===
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📍 投递意向地区</div>', unsafe_allow_html=True)

        if st.session_state.detected_cities:
            cities_str = "、".join(st.session_state.detected_cities)
            st.markdown(f'<div class="city-detected">🎯 已从简历检测到意向城市：{cities_str}</div>', unsafe_allow_html=True)

            selected_from_resume = st.selectbox(
                "确认意向城市",
                st.session_state.detected_cities + ["其他（手动输入）"],
                label_visibility="collapsed"
            )

            if selected_from_resume == "其他（手动输入）":
                st.session_state.city_scope = "其他"
                st.session_state.custom_city = st.text_input("输入意向城市", placeholder="例如：三亚", label_visibility="collapsed")
            else:
                st.session_state.selected_city = selected_from_resume
                st.session_state.city_scope = "国内"
        else:
            st.markdown('<div class="city-not-detected">○ 未从简历检测到意向城市，请手动选择</div>', unsafe_allow_html=True)

            city_scope = st.radio(
                "地区范围",
                ["国内", "海外"],
                horizontal=True,
                label_visibility="collapsed"
            )
            st.session_state.city_scope = city_scope

            if city_scope == "国内":
                selected_city = st.selectbox(
                    "选择城市",
                    CHINA_CITIES,
                    label_visibility="collapsed"
                )
                st.session_state.selected_city = selected_city
            else:
                country = st.selectbox(
                    "选择国家/地区",
                    OVERSEAS_COUNTRIES,
                    label_visibility="collapsed"
                )

                if country == "其他":
                    custom_overseas = st.text_input("输入意向城市/国家", placeholder="例如：迪拜", label_visibility="collapsed")
                    st.session_state.custom_city = custom_overseas
                    st.session_state.selected_city = custom_overseas
                else:
                    st.session_state.selected_city = country

        st.markdown('</div>', unsafe_allow_html=True)

    # 提交区域
    st.markdown("---")

    has_resume = uploaded_resume is not None
    has_jd = bool(jd_text_raw and len(jd_text_raw.strip()) >= 10)

    col_status, col_btn = st.columns([1, 2])
    with col_status:
        if has_resume and has_jd:
            st.markdown('<div class="status-chip chip-ready">✓ 信息已就绪</div>', unsafe_allow_html=True)
        else:
            missing = []
            if not has_resume: missing.append("简历")
            if not has_jd: missing.append("JD")
            st.markdown(f'<div class="status-chip chip-wait">○ 待完善: {"/".join(missing)}</div>', unsafe_allow_html=True)

    with col_btn:
        if st.button("✨ 一键开始智能匹配", type="primary", use_container_width=True, disabled=not (has_resume and has_jd)):
            resume_text = extract_text(uploaded_resume)

            if not resume_text:
                st.error("❌ 简历解析失败")
            elif not jd_text_raw or len(jd_text_raw.strip()) < 10:
                st.error("❌ JD 内容过短")
            else:
                st.session_state.loading = True
                st.session_state.resume_content = resume_text
                st.session_state.jd_content = jd_text_raw
                st.rerun()

# ==========================================
# 8. 加载页面
# ==========================================
elif st.session_state.loading:

    progress_text = st.empty()
    progress_bar = st.progress(0)

    stages = [
        ("📄 解析简历结构", 30),
        ("🎯 分析岗位 JD", 60),
        ("🤖 生成匹配策略", 90),
        ("✨ 即将完成", 100)
    ]

    for i in range(100):
        time.sleep(0.025)
        progress_bar.progress(i + 1)

        for stage_text, threshold in stages:
            if i < threshold:
                progress_text.markdown(f"<div style='text-align:center; color:rgba(255,255,255,0.7); font-weight:500;'>{stage_text} {i+1}%</div>", unsafe_allow_html=True)
                break

    st.session_state.loading = False
    st.session_state.app_stage = "result"
    st.rerun()

# ==========================================
# 9. 结果页面
# ==========================================
elif st.session_state.app_stage == "result":

    # 步骤指示器更新
    st.markdown("""
    <div class="step-track">
        <div class="step-node completed">✓</div>
        <div class="step-line active"></div>
        <div class="step-node active">2</div>
    </div>
    """, unsafe_allow_html=True)

    # 成功提示
    st.markdown("""
    <div class="success-glass">
        🎉 Agent 已完成深度解析，以下是实时对比视图
    </div>
    """, unsafe_allow_html=True)

    # 极简返回
    if st.button("← 返回", key="back_btn", type="tertiary"):
        st.session_state.app_stage = "input"
        st.rerun()

    st.markdown("### 🔍 智能解析对比")

    res_col1, res_col2 = st.columns(2, gap="large")

    with res_col1:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">📄 简历解析结果</div>', unsafe_allow_html=True)

        resume_words = len(st.session_state.resume_content)
        st.markdown(f'<div class="result-meta">{resume_words} 字符 · 已结构化处理</div>', unsafe_allow_html=True)

        st.text_area(
            "简历", 
            value=st.session_state.resume_content, 
            height=400, 
            disabled=True, 
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with res_col2:
        st.markdown('<div class="result-glass">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">🎯 目标岗位 JD</div>', unsafe_allow_html=True)

        jd_words = len(st.session_state.jd_content)
        st.markdown(f'<div class="result-meta">{jd_words} 字符 · 已锁定上下文</div>', unsafe_allow_html=True)

        st.text_area(
            "JD", 
            value=st.session_state.jd_content, 
            height=400, 
            disabled=True, 
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div class='footer-hint'>💡 对比视图已生成，后续可接入大模型进行智能润色与匹配分析</div>", unsafe_allow_html=True)
